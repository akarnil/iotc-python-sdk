#!/usr/bin/python3
import os
import sys
from importlib import import_module, reload

# this the runner of the demo, used to show A/B updates
# the actual code lives inside a folder called `primary_app_dir`
# should it fail, an attempt will be made to run the previous code in `secondary_app_dir`

# Stuff to change
app_name: str = "basic_sample.py"
primary_app_dir: str = "/primary/"
secondary_app_dir: str = "/secondary/"
tarball_download_dir = "/.temp_ota/"
tarball_extract_dir: str = "/.temp_extracted/"
primary_backup_extension:str = ".backup"

module_name:str = app_name.replace(".py","")
main_dir: str = os.path.dirname(__file__)
primary_app_backup_folder_name:str = primary_app_dir.rstrip("/") + primary_backup_extension


app_paths: dict = {
    "app_name": app_name,
    "primary_app_dir": primary_app_dir,
    "secondary_app_dir": secondary_app_dir,
    "tarball_download_dir": tarball_download_dir,
    "tarball_extract_dir": tarball_extract_dir,
    "module_name": module_name,
    "main_dir": main_dir,
    "primary_app_backup_folder_name" : primary_app_backup_folder_name
}

if __name__ == "__main__":

    secondary_exists: bool = False
    secondary_path: str = main_dir + secondary_app_dir + app_name    
    if os.path.exists(secondary_path):
        secondary_exists = True

    primary_exists: bool = False
    primary_path: str = main_dir + primary_app_dir + app_name
    if os.path.exists(primary_path):
        primary_exists = True

    if primary_exists and secondary_exists:
        try:
            print("Running app on A")
            path = primary_path
            sys.path.append(path.replace(app_name,""))
            module = import_module(module_name)
            print("using app at " + path)
            module.main(app_paths)
        except Exception as ex:
            print(str(ex))
            print("app on A, has failed trying secondary B")
            sys.path.remove(path.replace(app_name,""))
            path = secondary_path
            sys.path.append(path.replace(app_name,""))
            reload(module)
            print("Running app on B")
            print("using app at " + path)
            module.main(app_paths)

    elif primary_exists:
        try:
            print("Running app on A")
            path = primary_path
            sys.path.append(path.replace(app_name,""))
            module = import_module(module_name)
            print("using app at " + path)
            module.main(app_paths)
        except Exception as ex:
            print("App failed")
            print(str(ex))

    elif secondary_exists:
        try:
            print("Running app on B")
            path = secondary_path
            sys.path.append(path.replace(app_name,""))
            module = import_module(module_name)
            print("using app at " + path)
            module.main(app_paths)
        except Exception as ex:
            print("App failed")
            print(str(ex))