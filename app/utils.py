"""Utility functions module"""
import hashlib
import json
import datetime
import random
import os
#################
# temp auxiliar #
#################
from fastapi import status
from .controllers.ssh.handler import RemoteHandler
#################
from .config import settings


def save_file(filename: str, filedata: bin, task_id: str) -> str:
    """Save file to disk"""
    # root = settings.atena_root
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


def load_json(path: str) -> dict:
    """Loads json file and returns as a dictionary"""
    with open(path, encoding='utf-8') as f:
        return json.load(f)


def process_config(fpath: str) -> dict:
    """Process configuration file"""
    conf = load_json(fpath)
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

# Temporary functions that will be replaced into class


def atena_upload(fname, remote, task_id):
    """Submit job to atena cluster"""
    # root = settings.atena_root
    root = settings.nfs_root
    folder_destination = 'scripts'
    file_path = f"{root}/{folder_destination}/{task_id}/{fname}"
    sanity_check = remote.send_file(fname, file_path, task_id)
    if not sanity_check:
        return status.HTTP_500_INTERNAL_SERVER_ERROR
    return file_path


def atena_connect():
    """Spawn new remote handler with atena config"""
    remote = RemoteHandler()
    host = "atn1mg4"
    user = settings.env_confs['ATENA_USER']
    passwd = settings.env_confs['ATENA_PASSWD']
    remote.connect(host, user, passwd)
    return remote

def get_mlflow_run_id(task):
    path_to_search = task.project_path
    target_file = "run_mlflow_config.txt"
    target_path = f"{path_to_search}/{target_file}"
    files_and_dirs = os.listdir(path_to_search)
    if  target_file in files_and_dirs:
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