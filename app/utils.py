"""Utility functions module"""
import json
import datetime
import random
import os
from .config import settings
from .remote_manager import RemoteManager


def load_json(path: str) -> dict:
    """Loads json file and returns as a dictionary"""
    with open(path, encoding='utf-8') as f:
        return json.load(f)


def get_status_message(code: str) -> str:
    """Get status message given status code

    :param code: job status code
    :type code: str
    :return: message for the given status code
    :rtype: str
    """
    squeue_status = {
        "CD": "COMPLETED: The job has completed successfully.",
        "CG": "COMPLETING: The job is finishing but some processes are still \
            active.",
        "F": "FAILED: The job terminated with a non-zero exit code and failed \
            to execute.",
        "PD": "PENDING: The job is waiting for resource allocation. It will \
            eventually run.",
        "R": "RUNNING: The job is allocated to a node and running.",
        "S": "SUSPENDED: Running job has been stopped with its cores \
            released to other jobs.",
        "ST": "STOPPED: Running job has been stopped with its cores retained.",
        "CA": "CANCELLED: Job was explicitly cancelled by the user or system \
            administrator."
    }
    if code not in squeue_status:
        return "UNKNOWN: The returned job code is not in the list!"
    return squeue_status[code]


def strip_filename(file_path: str) -> str:
    """Strip filename from a path

    :param file_path: path to be stripped
    :type file_path: str
    :return: filename stripped
    :rtype: str
    """
    return file_path.split('/')[-1]


def create_task_id() -> str:
    """Create task ID

    Create the ID based on the time that the task is created

    """
    task_id = datetime.datetime.now().strftime('%Y%m%d%H%M%S%f') + \
        f"{random.randint(0, 9999):04d}"
    return task_id


def read_file(file_path):
    """read file given path"""
    with open(file_path, "r", encoding='utf-8') as f:
        file_data = f.read()
    return file_data


def prepare_srm_template(task_dict):
    """Prepare srm template with task_dict"""
    if "atena" in task_dict['runner_location']:
        if task_dict['execution_mode'] == "mlflow":
            template = read_file(
                "app/controllers/slurm/slurm_template_with_mlflow.srm")
        else:
            template = read_file(
                "app/controllers/slurm/new_slurm_template.srm")
    slurm_script = template.format(
        experiment_name=task_dict['experiment_name'],
        instance_type=task_dict['instance_type'],
        account=task_dict['account'],
        image_name=task_dict['image_name'],
        zip_name="files.zip",
        dataset_name=task_dict['dataset_name'],
        task_id=task_dict['id'],
        sif_path=settings.sif_root,
        atena_root=settings.atena_root,
        nfs_root=settings.nfs_root,
        project_root=task_dict['project_path'],
        command=task_dict['command']
    )
    return slurm_script


def get_mlflow_run_id(path_to_search):
    target_file = "run_mlflow_config.txt"
    target_path = f"{path_to_search}/{target_file}"
    files_and_dirs = os.listdir(path_to_search)
    if target_file in files_and_dirs:
        with open(target_path, 'r', encoding='utf-8') as file:
            content = file.read()
        run_id = None
        for line in content.splitlines():
            if line.startswith('run_id:'):
                run_id = line.split(':', 1)[1].strip()
                break
    if run_id:
        return run_id
    else:
        return "Arquivo 'run_mlflow_config.txt' não encontrado no diretório."


def atena_connect():
    """Connect to atena cluster using settings"""
    host = "atn1mg4"
    user = settings.env_confs['ATENA_USER']
    passwd = settings.env_confs['ATENA_PASSWD']
    remote = RemoteManager()
    remote.connect(host, user, passwd)
    return remote


def get_local_folder(task_id: int) -> str:
    """Get local folder with the current task files"""
    root = settings.nfs_root
    folder_destination = 'scripts'
    local_folder = f"{root}/{folder_destination}/{str(task_id)}"
    return local_folder


def get_remote_folder(task_id: int) -> str:
    """Get remote folder with the uploaded task files"""
    root = settings.nfs_root
    folder_destination = "uploads"
    remote_folder = f"{root}/{folder_destination}/{str(task_id)}"
    return remote_folder
