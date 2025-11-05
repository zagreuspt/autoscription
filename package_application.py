import os
import shutil
import subprocess
from pathlib import Path

from PyInstaller import DEFAULT_WORKPATH, DEFAULT_DISTPATH
from PyInstaller import __main__ as pyinstaller_main

# my spec file in "dev\config" dir
autoscription_spec_file = os.path.join(os.getcwd(), "autoscription_main.spec")
installer_spec_file = os.path.join(os.getcwd(), "installer.spec")

# # TODO: check if exists and remove ignore_errors
shutil.rmtree(DEFAULT_DISTPATH, ignore_errors=True)
print("dist directory deleted")
shutil.rmtree(DEFAULT_WORKPATH, ignore_errors=True)
print("build directory deleted")
shutil.rmtree("nuitka_build", ignore_errors=True)
print("nuitka_build directory deleted")

subprocess.run(
    ["nuitka.bat", "--module", "installer", "--include-package=installer", "--output-dir=../../../nuitka_build"],
    cwd="src/autoscription/delivery",
)

subprocess.run(
    ["nuitka.bat", "--module", "autoscription_main.py", "--output-dir=nuitka_build", "--include-package=src"]
)
pyinstaller_main.run(
    ["--distpath", DEFAULT_DISTPATH, "--workpath", DEFAULT_WORKPATH, autoscription_spec_file, "--noconfirm"]
)
pyinstaller_main.run(
    ["--distpath", DEFAULT_DISTPATH, "--workpath", DEFAULT_WORKPATH, installer_spec_file, "--noconfirm"]
)

print("Starting zip process...")
root_dir_path = Path(DEFAULT_DISTPATH) / "autoscription_main"

# The base name for your zip file
zip_file_base_name = root_dir_path.as_posix()
# The new target directory name you want inside your zip file
target_dir_inside_zip = "autoscription_main"
# The path for the temporary directory where we'll replicate the structure
temp_dir_path = Path(zip_file_base_name + "_temp")
# Create a temporary directory that will hold the directory structure you want
temp_target_dir_path = temp_dir_path / target_dir_inside_zip
shutil.copytree(root_dir_path, temp_target_dir_path)

# Create a zip file from the temporary directory
shutil.make_archive(base_name=zip_file_base_name, format="zip", root_dir=temp_dir_path)

# Clean up the temporary directory after making the zip file
shutil.rmtree(temp_dir_path)
zip_file_path = root_dir_path / "autoscription_main.zip"
print(
    f"Zip Completed.\n Saved on {zip_file_path}\n DO NOT ZIP THE APPLICATION"
    + " MANUALLY.\n USE THE ZIP FILE PROVIDED!!!"
)
