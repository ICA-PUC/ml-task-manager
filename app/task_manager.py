"""Task Manager module for all task related logic"""
import json
import datetime
import random
from .utils import atena_upload, atena_connect
from .controllers.slurm.slurm_manager import prep_template


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

    def _process_config(self) -> dict:
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
        self.task_dict = self._process_config()
        self.task_dict['id'] = self.task_id

    def _is_file_name_equal(self):
        script_name = self._strip_filename(self.task_dict['script_path'])
        return script_name == self.py_name

    def _create_atena_task(self):
        """Create and submit a new task to atena"""
        remote = atena_connect()
        atena_upload(self._strip_filename(
            self.task_dict['script_path']), remote, self.task_dict['id'])
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

    def run_task(self):
        """Entrypoint for new task creation"""
        self._config_task_dict()
        status = not self._is_file_name_equal()
        # Erro Handling
        if status:
            return_msg = {
                "msg": f"{self.task_dict['script_path']} and \
                    {self.task_dict['py_name']} must be equal!",
                "status": status.HTTP_400_BAD_REQUEST
            }
            return return_msg

        output = self._create_task()

        if output[0]:
            string = output[0].strip()
            job_id = string.split('Submitted batch job ')[1].strip()
            self.task_dict['job_id'] = job_id

            return self.task_dict
        return {"msg": output[1]}
