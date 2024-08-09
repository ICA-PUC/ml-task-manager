"""File manager module for all file related logic"""
import os
import hashlib
from fastapi import UploadFile
from . import utils


async def process_upload(files: list[UploadFile], task_id: int) -> tuple:
    """Process the received list of files

    :param files: list of files uploaded
    :type files: list[UploadFile]
    :param task_id: task identifier number
    :type task_id: int
    :return: name of python file and name of config file
    :rtype: tuple
    """
    local_folder = utils.get_local_folder(task_id)
    for file in files:
        fname = file.filename
        fdata = await file.read()
        if fname.endswith(".json"):
            save_file(local_folder, fdata, "submiter_confs.json")
        elif fname.endswith(".zip"):
            save_file(local_folder, fdata, "files.zip")
        else:
            raise ValueError


def strip_filename(file_path: str) -> str:
    """Strip filename from a path"""
    return file_path.split('/')[-1]


def save_file(path: str, data: bin, file_name: str) -> str:
    """Save file to disk"""
    os.makedirs(path, exist_ok=True)
    file_path = f"{path}/{file_name}"
    if isinstance(data, str):
        data = data.encode('utf-8')
    with open(file_path, 'wb') as f:
        f.write(data)
        with open(f"{file_path}.md5", "wb") as f:
            hashmd5 = hashlib.md5(data).hexdigest()
            f.write(hashmd5.encode())
    return file_path
