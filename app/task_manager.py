"""Task Manager class module"""
import os
import datetime
import random
import hashlib
import json
from fastapi import UploadFile
from . import utils
from .config import settings


class TaskManager():
    """Class Manager for all task related logic"""

    def __init__(self, task_id):
        self.task_id = task_id
        self.py_name = None
        self.task_dict = None
        self.conf_path = None

    def _load_json(self, path: str) -> dict:
        """Loads json file and returns as a dictionary"""
        with open(path, encoding='utf-8') as f:
            return json.load(f)

    def _strip_filename(self, file_path: str) -> str:
        """Strip filename from a path"""
        return file_path.split('/')[-1]

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
            fpath = self._save_file(fname, fdata, task_id)
            if fname.endswith(".json"):
                self.conf_path = fpath
            if fname.endswith(".py"):
                self.py_name = fname

    def _save_file(self, filename: str, filedata: bin, task_id: str) -> str:
        """Save file to disk"""
        root = settings.nfs_root
        folder_destination = 'scripts'
        fpath = f"{root}/{folder_destination}/{str(task_id)}"
        os.makedirs(fpath, exist_ok=True)
        fpath = f"{root}/scripts/{str(task_id)}/{filename}"
        if isinstance(filedata, str):
            filedata = filedata.encode('utf-8')
        with open(fpath, 'wb') as f:
            f.write(filedata)
            with open(f"{fpath}.md5", "wb") as f:
                hashmd5 = hashlib.md5(filedata).hexdigest()
                f.write(hashmd5.encode())
        return fpath

    def _process_configuration(self) -> dict:
        """Process configuration file"""
        configuration = self._load_json(self.conf_path)
        filtered_configuration = {}
        cluster_configuration = {
            'atena02': ['instance_type', 'image_name', 'account'],
            'dev': ['instance_type', 'image_name', 'account']
        }
        target_cluster = configuration['runner_location']
        general_configuration = ['runner_location', 'dataset_name',
                                 'script_path', 'project_path',
                                 'experiment_name', 'command']

        for parameters in general_configuration:
            filtered_configuration[parameters] = configuration[parameters]

        for parameters in cluster_configuration[target_cluster]:
            cluster_parameters = configuration['clusters'][target_cluster]['infra_config'][parameters]
            filtered_configuration[parameters] = cluster_parameters

        # Extract backend execution configuration based on execution_mode
        execution_mode = configuration['execution_mode']
        filtered_configuration['execution_mode'] = configuration['execution_mode']
        backend_execution_config = configuration['backend_execution'][execution_mode]['execution_config']
        for key, value in backend_execution_config.items():
            filtered_configuration[key] = value

        print(filtered_configuration)

        return filtered_configuration

    def _create_task_id(self):
        return datetime.datetime.now().strftime('%Y%m%d%H%M%S%f') + f" \
            {random.randint(0, 9999):04d}"

    def _config_task_dict(self):
        self.task_dict = self._process_configuration()
        self.task_dict['id'] = self.task_id

    def _create_atena_task(self):
        """Create and submit a new task to atena"""
        remote = utils.atena_connect()
        utils.atena_upload(self._strip_filename(
            self.task_dict['script_path']), remote, self.task_dict['id'])
        srm_name = utils.prepare_srm_template(self.task_dict)
        srm_path = utils.atena_upload(srm_name, remote, self.task_dict['id'])
        remote.exec(f"sbatch {srm_path}")
        output_tuple = remote.get_output()
        remote.close()
        return output_tuple

    def _create_dev_task(self):
        """Create and submit a new task to dev"""
        output_tuple = 1
        return output_tuple

    def _create_task(self):
        if "atena" in self.task_dict['runner_location']:
            task_output_tuple = self._create_atena_task()
        elif "dev" in self.task_dict['runner_location']:
            task_output_tuple = self._create_dev_task()
        return task_output_tuple

    def run_task(self):
        """Run a new task"""
        self._config_task_dict()
        task_output_tuple = self._create_task()
        if task_output_tuple[0]:
            text = task_output_tuple[0].strip()
            job_id = text.split('Submitted batch job ')[1].strip()
            self.task_dict['job_id'] = job_id
            return self.task_dict

        return {"msg": task_output_tuple[1]}
