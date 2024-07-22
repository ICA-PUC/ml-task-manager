"""Task Manager class module"""
import json
import datetime
import random
from fastapi import status
from . import utils
from .controllers.slurm.slurm_manager import prepare_srm_template


class TaskManager():
    """Class Manager for all task related logic"""

    def __init__(self, task_id, py_name, conf_path):
        self.task_id = task_id
        self.py_name = py_name
        self.task_dict = None
        self.conf_path = conf_path

    def _load_json(self, path: str) -> dict:
        """Loads json file and returns as a dictionary"""
        with open(path, encoding='utf-8') as f:
            return json.load(f)

    def _strip_filename(self, file_path: str) -> str:
        """Strip filename from a path"""
        return file_path.split('/')[-1]

    def _process_configuration(self) -> dict:
        """Process configuration file"""
        configuration = self._load_json(self.conf_path)
        filtered_configuration = {}
        cluster_conf = {
            'atena02': ['instance_type', 'image_name', 'account'],
            'dev': ['instance_type', 'image_name', 'account']
        }
        target_cluster = configuration['runner_location']
        general_configuration = ['runner_location', 'dataset_name',
                                 'script_path', 'experiment_name']

        for parameters in general_configuration:
            filtered_configuration[parameters] = configuration[parameters]

        for parameters in cluster_conf[target_cluster]:
            cluster_conf = configuration['clusters'][target_cluster]
            infra_params = ['infra_config'][parameters]
            filtered_configuration[parameters] = infra_params
        return filtered_configuration

    def _create_task_id(self):
        return datetime.datetime.now().strftime('%Y%m%d%H%M%S%f') + f" \
            {random.randint(0, 9999):04d}"

    def _config_task_dict(self):
        self.task_dict = self._process_configuration()
        self.task_dict['id'] = self.task_id

    def _is_file_name_equal(self):
        script_name = self._strip_filename(self.task_dict['script_path'])
        return script_name == self.py_name

    def _create_atena_task(self):
        """Create and submit a new task to atena"""
        remote = utils.atena_connect()
        utils.atena_upload(self._strip_filename(
            self.task_dict['script_path']), remote, self.task_dict['id'])
        srm_name = prepare_srm_template(self.task_dict)
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
        if not self._is_file_name_equal():
            return_msg = {
                "msg": f"{self.task_dict['script_path']} \
                            and {self.task_dict['py_name']} must be equal!",
                "status": status.HTTP_400_BAD_REQUEST
            }
            return return_msg

        task_output_tuple = self._create_task()

        if task_output_tuple[0]:
            text = task_output_tuple[0].strip()
            job_id = text.split('Submitted batch job ')[1].strip()
            self.task_dict['job_id'] = job_id
            return self.task_dict

        return {"msg": task_output_tuple[1]}