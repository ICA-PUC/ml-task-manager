"""File manager module for all file related logic"""
from fastapi import UploadFile
from .utils import save_file


class FileManager():
    """File manager class with file processing methods"""

    def __init__(self):
        self.py_name = None
        self.conf_path = None

    async def process_files(self, files: list[UploadFile],
                            task_id: int) -> tuple:
        """Process the received list of files

        :param files: list of files uploaded
        :type files: list[UploadFile]
        :param task_id: task identifier number
        :type task_id: int
        :return: name of python file and name of config file
        :rtype: tuple
        """
        for file in files:
            fname = file.filename
            fdata = await file.read()
            fpath = save_file(fname, fdata, task_id)
            if fname.endswith(".json"):
                self.conf_path = fpath
            if fname.endswith(".py"):
                self.py_name = fname

        return self.py_name, self.conf_path
