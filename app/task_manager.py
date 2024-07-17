from .utils import atena_upload, atena_connect
from .controllers.slurm.slurm_manager import prep_template
from sqlmodel import Session
from .models.task import Task
import json
# from .file_manager import FileManager
import datetime
import random

class TaskManager():

    def __init__(self, task_id, py_name, conf_path, engine):
        self.task_id = task_id# self._create_task_id()
        self.py_name = py_name
        # self.file_manager = FileManager(task_id, py_name, conf_path)
        self.engine = engine
        self.task_dict = None
        self.conf_path = conf_path
        # print(f'Esse é o tipo do self.conf_path:{self.conf_path}')
        # print(f'Esse é o tipo do self.py_name:{self.py_name}')
    
    def _load_json(self, path: str) -> dict:
        """Loads json file and returns as a dictionary"""
        with open(path, encoding='utf-8') as f:
            return json.load(f)
    
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

    def _create_task_id(self):
        return datetime.datetime.now().strftime('%Y%m%d%H%M%S%f') + f"{random.randint(0, 9999):04d}"
    
    def _config_task_dict(self):
        self.task_dict = self._process_config(self.conf_path)
        self.task_dict['id'] = self.task_id
       
    def _is_file_name_equal(self):
        script_name = self._strip_filename(self.task_dict['script_path'])
        return script_name == self.py_name

    def _create_atena_task(self):
        """Create and submit a new task to atena"""
        remote = atena_connect()
        atena_upload(self._strip_filename(self.task_dict['script_path']), remote, self.task_dict['id'])
        srm_name = prep_template(self.task_dict)
        srm_path = atena_upload(srm_name, remote, self.task_dict['id'])
        remote.exec(f"sbatch {srm_path}")
        output = remote.get_output()
        remote.close()
        return output
    
    def _create_dev_task(self):
        """Create and submit a new task to dev"""
        return 1
        
    def _create_task(self):
        if "atena" in self.task_dict['runner_location']:
            output = self._create_atena_task()
        elif "dev" in self.task_dict['runner_location']:
            output = self._create_dev_task()
        return output
    
    def run_task (self):     
        self._config_task_dict()       
        status = not self._is_file_name_equal()
        # Erro Handling
        if status:
            return_msg = { 
                            "msg": f"{self.task_dict['script_path']} and {self.task_dict['py_name']} must be equal!",
                            "status" : status.HTTP_400_BAD_REQUEST
                            }
            return return_msg 
                            
        output = self._create_task()

        if output [0]:
            string = output[0].strip()
            job_id = string.split('Submitted batch job ')[1].strip() #output[0].split('Submitted bacth job ')[1][:-1]
            self.task_dict['job_id'] = job_id

            return self.task_dict
            
            # # todo: How to work with this db, we should pass an instance into the __init__ ?
            # with Session(self.engine) as session:
            #     db_task = Task.model_validate(self.task_dict)
            #     print(f'db_task :{db_task}')
            #     session.add(db_task)
            #     session.commit()
            #     session.refresh(db_task)
            #     return db_task
            
        elif output [1]:
            return {"msg": output[1]} 