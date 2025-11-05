import logging
import os
import shutil
import subprocess
import zipfile

from azure.storage.blob import BlobServiceClient


def get_installation_dir() -> str:
    # Get the path to the root directory (C:/)
    save_directory = os.path.abspath(os.sep)

    # Get the home directory
    # save_directory = os.path.expanduser("~")
    save_directory = os.path.join(save_directory, "OneDriveTmp", "tmp")

    return str(save_directory)


def get_installation_certs_dir() -> str:
    # Get the path to the root directory (C:/)
    certs_directory = os.path.abspath(os.sep)

    # Get the home directory
    # save_directory = os.path.expanduser("~")
    certs_directory = os.path.join(certs_directory, "OneDriveTmp", "certs")

    return str(certs_directory)


class Installer:
    def __init__(self) -> None:
        sas_token = (
            "?sv=2022-11-02&ss=b&srt=co"
            "&sp=rl&se=2033-05-20T19:01:14Z"
            "&st=2023-05-20T11:01:14Z&spr=https"
            "&sig=%2Bq2HEFSbBeBuSRxh6Tp8FnPi7SqrkxGxvmH08j2QMi0%3D"
        )
        self.container_name = "releases"
        self.blob_service_client = BlobServiceClient(
            account_url="https://stautoscriptionext002.blob.core.windows.net",
            credential=sas_token,
        )
        self.container_client = self.blob_service_client.get_container_client(self.container_name)
        self.project_name = "autoscription_main"

    def clean_directory(self, subdir_name: str) -> None:
        logging.info("Cleaning Installation directory")
        directory: str = os.path.join(get_installation_dir(), self.project_name)
        if not os.path.exists(directory):
            logging.info("Installation directory does not exist.")
            return

        if not os.path.isdir(directory):
            logging.info("Invalid installation directory path.")
            return

        subdir_path = os.path.join(directory, subdir_name)
        if not os.path.isdir(subdir_path):
            logging.info("Installation subdirectory does not exist.")
            return

        for item in os.listdir(directory):
            item_path = os.path.join(directory, item)
            if item not in ["cache", subdir_name]:
                if os.path.isfile(item_path):
                    os.remove(item_path)
                elif os.path.isdir(item_path):
                    shutil.rmtree(item_path)

        logging.info("Deletion complete.")

    def download_zip(self, file_name: str, directory: str) -> None:
        logging.info("Downloading Zip...")
        with open(directory, "wb") as file:
            self.container_client.download_blob(file_name).readinto(file)
        logging.info("Download successful...")

    def unzip(self, zip_file: str) -> None:
        logging.info("Extracting...")
        with zipfile.ZipFile(zip_file, "r") as zip_ref:
            zip_ref.extractall(get_installation_dir())
        logging.info("Extraction sucessful.")

    def add_version(self, version: str) -> None:
        with open(os.path.join(get_installation_dir(), self.project_name, "version.txt"), "w") as version_file:
            version_file.write(version)
        logging.info("version.txt creation successful.")

    def delete_zip(self, file_path: str) -> None:
        if not os.path.exists(file_path):
            logging.info("Zip file does not exist.")
            return

        if not os.path.isfile(file_path):
            logging.info("Zip invalid file path.")
            return

        try:
            os.remove(file_path)
            logging.info("Zip deletion successful.")
        except Exception as e:
            logging.exception(f"Error deleting file: {str(e)}")

    def get_version(self) -> str:
        file_path = os.path.join(get_installation_dir(), self.project_name, "version.txt")

        if not os.path.exists(file_path):
            logging.info("Version file path does not exist.")
            return ""

        if not os.path.isfile(file_path):
            logging.info("Version invalid file path.")
            return ""

        try:
            with open(file_path, "r") as file:
                content = file.read()
            return content
        except Exception as e:
            logging.exception(f"Error reading file: {str(e)}")
            return ""

    def run_exe(self) -> None:
        exe_dir: str = os.path.join(get_installation_dir(), self.project_name)
        exe_path: str = os.path.join(exe_dir, f"{self.project_name}.exe")
        if not os.path.exists(exe_path):
            raise FileNotFoundError(f"Executable file not found: {exe_path}")
        logging.info(exe_path)
        try:
            subprocess.run(exe_path, check=True, cwd=exe_dir)
        except subprocess.CalledProcessError as e:
            logging.error(f"Error running executable: {str(e)}")
            logging.error(e.output)
            logging.exception(e)
        except Exception as e:
            logging.exception(f"Error occurred: {str(e)}")
