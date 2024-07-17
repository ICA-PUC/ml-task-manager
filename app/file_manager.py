import json
from .utils import save_file, get_status_message
import time
import asyncio

class FileManager():
    def __init__(self, task_id, py_name, conf_path):
        # print(f'Isso é o que chega para o manager {files}') -> chegou a mesma coisa do input
        # self.files = files
        self.task_id = task_id
        self.py_name = py_name
        self.conf_path = conf_path
        # print(f'Isso é o que chega para o _process_files {self.files}') -> chegou a mesma coisa do input
        # self._process_files()

    def _load_json(self, path: str) -> dict:
        """Loads json file and returns as a dictionary"""
        with open(path, encoding='utf-8') as f:
            return json.load(f)
    
    # async def _read_file(self, file):
    #     content = await file.read()
    #     print(f'Esse é o type do content: {type(content)}')
    #     return content
    
    # def _process_files(self):
    #     for file in self.files:
    #         print(f'file: {file}')
    #         fname = file.filename
    #         print(f' Esse é o meu filename :{type(fname)}')
    #         print(f' Esse é o meu filename :{fname}')
    #         fdata =  self._read_file(file)  # Assuming file objects have a read method
    #         print(f' Esse é o meu problema :{type(fdata)}')
    #         print(f' Esse é o meu problema :{fdata}')
    #         # o file.read() esta virando um coroutine, e era para ser bit
    #         fpath =  save_file(fname, fdata, self.task_id)
    #         print(f' Esse é o meu fpath :{type(fpath)}')
    #         print('Aqui esta meu erro!!!')
    #         if ".json" in fname:
    #             self.conf_path = fpath
    #         if ".py" in fname:
    #             self.py_path = fpath
    #             self.py_name = fname
    
    def _strip_filename(self, file_path: str) -> str:
        """Strip filename from a path

        :param file_path: path to be stripped
        :type file_path: str
        :return: filename stripped
        :rtype: str
        """
        return file_path.split('/')[-1]

    def _process_config(self, fpath: str) -> dict:
        """Process configuration file"""
        # print(f'Esse foi o fpath que recebi :{fpath}')
        # print(f'Esse é o fpath que vou usar :{self.conf_path}')
        conf = self._load_json(self.conf_path)
        filtered_confs = {}
        cluster_confs = {
            'atena02': ['instance_type', 'image_name', 'account'],
            'dev': ['instance_type', 'image_name', 'account']
        }
        target_cluster = conf['runner_location']
        general_confs = ['runner_location', 'dataset_name',
                        'script_path', 'experiment_name']

        for param in general_confs:
            filtered_confs[param] = conf[param]

        for param in cluster_confs[target_cluster]:
            cluster_param = conf['clusters'][target_cluster]['infra_config'][param]
            filtered_confs[param] = cluster_param
        return filtered_confs