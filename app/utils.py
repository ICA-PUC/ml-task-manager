"""Utility functions module"""
import hashlib
import json
from .config import settings
import datetime
import random
import os

def save_file(filename: str, filedata: bin, task_id: str) -> str:
    """Save file to disk"""
    root = settings.atena_root
    
    fpath = f"{root}/scripts/{str(task_id)}"
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
    task_id = datetime.datetime.now().strftime('%Y%m%d%H%M%S%f') + f"{random.randint(0, 9999):04d}"
    return task_id
