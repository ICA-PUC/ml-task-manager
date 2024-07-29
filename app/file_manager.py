import json
from .utils import save_file, get_status_message
from fastapi import UploadFile
import time
import asyncio

class FileManager():
    def __init__(self):
        self.py_name = None
        self.conf_path = None
        
    async def process_files(self, files: list[UploadFile], task_id):
        for file in files:
            fname = file.filename
            fdata = await file.read()  # This is an async operation, so use 'await'
            fpath = save_file(fname, fdata, task_id)
            if fname.endswith(".json"):
                self.conf_path = fpath
            if fname.endswith(".py"):
                self.py_name = fname
        
        return self.py_name, self.conf_path


    # def _load_json(self, path: str) -> dict:
    #     """Loads json file and returns as a dictionary"""
    #     with open(path, encoding='utf-8') as f:
    #         return json.load(f)
    
   
    # def _strip_filename(self, file_path: str) -> str:
    #     """Strip filename from a path

    #     :param file_path: path to be stripped
    #     :type file_path: str
    #     :return: filename stripped
    #     :rtype: str
    #     """
    #     return file_path.split('/')[-1]

    # def _process_config(self, fpath: str) -> dict:
    #     """Process configuration file"""
    #     # print(f'Esse foi o fpath que recebi :{fpath}')
    #     # print(f'Esse é o fpath que vou usar :{self.conf_path}')
    #     conf = self._load_json(self.conf_path)
    #     filtered_confs = {}
    #     cluster_confs = {
    #         'atena02': ['instance_type', 'image_name', 'account'],
    #         'dev': ['instance_type', 'image_name', 'account']
    #     }
    #     target_cluster = conf['runner_location']
    #     general_confs = ['runner_location', 'dataset_name',
    #                     'script_path', 'experiment_name']

    #     for param in general_confs:
    #         filtered_confs[param] = conf[param]

    #     for param in cluster_confs[target_cluster]:
    #         cluster_param = conf['clusters'][target_cluster]['infra_config'][param]
    #         filtered_confs[param] = cluster_param
    #     return filtered_confs