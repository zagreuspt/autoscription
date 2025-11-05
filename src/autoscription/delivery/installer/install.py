import logging
import os
import sys

from azure.core.paging import ItemPaged
from azure.storage.blob import BlobProperties

from .installer import Installer, get_installation_dir


def run() -> None:
    if hasattr(sys, "_MEIPASS"):
        import pyi_splash

        pyi_splash.update_text("UI Loaded ...")

    installer = Installer()

    current_version = installer.get_version()

    # Get a list of blobs in the specified directory
    blob_list: ItemPaged[BlobProperties] = installer.container_client.list_blobs()

    latest_blob: BlobProperties = sorted(
        blob_list,
        key=lambda b: [int(num) if num.isdigit() else num for num in str(b.name).rsplit("_v", 1)[-1].split(".")],
    )[-1]
    # Extract the version number from the blob name
    project_name, latest_version = latest_blob.name.rsplit("_", 1)
    latest_version = latest_version.rsplit(".", 1)[0]
    retries_remaining = 2

    while retries_remaining > 0:
        if latest_version != current_version:
            if hasattr(sys, "_MEIPASS"):
                pyi_splash.update_text("Autoscription Updating ...")
            logging.info("New Version found. Updating...")
            installation_dir = get_installation_dir()
            if not os.path.exists(installation_dir):
                os.makedirs(installation_dir)
            zip_path = os.path.join(installation_dir, latest_blob.name)
            installer.download_zip(latest_blob.name, zip_path)
            installer.clean_directory("executions")
            installer.unzip(zip_path)
            installer.add_version(latest_version)
            installer.delete_zip(zip_path)
        if hasattr(sys, "_MEIPASS"):
            pyi_splash.close()
        try:
            installer.run_exe()
            retries_remaining = 0
        except FileNotFoundError as e:
            logging.error(f"Error running executable: {str(e)}")
            retries_remaining -= 1
