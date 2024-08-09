"""Task Manager class module"""
from . import utils
from . import file_manager


class TaskManager():
    """Class Manager for all task related logic"""

    def __init__(self, task_id, conf_path):
        self.task_dict = self._process_configuration(task_id, conf_path)

    def _process_configuration(self, task_id, conf_path) -> dict:
        """Process configuration file"""
        conf = utils.load_json(conf_path)
        filtered_conf = {}
        cluster_conf = {
            'atena02': ['instance_type', 'image_name', 'account'],
            'dev': ['instance_type', 'image_name', 'account']
        }
        target_cluster = conf['runner_location']
        general_conf = ['runner_location', 'dataset_name',
                        'project_path', 'experiment_name', 'command']

        for parameters in general_conf:
            filtered_conf[parameters] = conf[parameters]
        clusters = conf['clusters']
        for params in cluster_conf[target_cluster]:
            cluster_params = clusters[target_cluster]['infra_config'][params]
            filtered_conf[params] = cluster_params

        # Extract backend execution conf based on execution_mode
        execution_mode = conf['execution_mode']
        bk_exec = conf['backend_execution']
        filtered_conf['execution_mode'] = conf['execution_mode']
        backend_execution_config = bk_exec[execution_mode]['execution_config']
        for key, value in backend_execution_config.items():
            filtered_conf[key] = value

        filtered_conf['id'] = task_id

        return filtered_conf

    def _create_atena_task(self):
        """Create and submit a new task to atena"""
        rm = utils.atena_connect()
        srm_temp = utils.prepare_srm_template(self.task_dict)
        local_f = utils.get_local_folder(self.task_dict['task_id'])
        local_srm_path = file_manager.save_file(local_f, srm_temp,
                                                "run_job.srm")
        remote_f = utils.get_remote_folder(self.task_dict['task_id'])
        remote_srm_path = f"{remote_f}/run_job.srm"
        rm.send_file(local_srm_path, remote_srm_path)
        rm.exec(f"sbatch {remote_srm_path}")
        output_tuple = rm.get_output()
        rm.close()
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
        task_output_tuple = self._create_task()
        if task_output_tuple[0]:
            text = task_output_tuple[0].strip()
            job_id = text.split('Submitted batch job ')[1].strip()
            self.task_dict['job_id'] = job_id
            return self.task_dict

        return {"msg": task_output_tuple[1]}
