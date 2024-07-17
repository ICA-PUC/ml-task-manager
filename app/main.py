"""Entrypoint for the Task Manager API Server"""
from fastapi import FastAPI, UploadFile, status
from .models.task import Task
from .utils import save_file, process_config, get_status_message
from .utils import strip_filename
from .controllers.ssh.handler import RemoteHandler
from .controllers.slurm.slurm_manager import prep_template
from .config import settings
from .db_manager import DBManager


dbm = DBManager()
app = FastAPI()


def atena_connect():
    """Spawn new remote handler with atena config"""
    remote = RemoteHandler()
    host = "atn1mg4"
    user = settings.env_confs['ATENA_USER']
    passwd = settings.env_confs['ATENA_PASSWD']
    remote.connect(host, user, passwd)
    return remote


def dev_connect():
    """Spawn new remote handler with dev config"""
    remote = RemoteHandler()
    host = "slurmmanager"
    user = "admin"
    passwd = "admin"
    remote.connect(host, user, passwd)
    return remote


def atena_upload(fname, remote):
    """Submit job to atena cluster"""
    root = settings.atena_root
    file_path = f"{root}/scripts/{fname}"
    sanity_check = remote.send_file(fname, file_path)
    if not sanity_check:
        return status.HTTP_500_INTERNAL_SERVER_ERROR
    return file_path


def create_atena_task(pyname, task):
    """Create and submit a new task to atena"""
    remote = atena_connect()
    atena_upload(pyname, remote)
    srm_name = prep_template(task)
    srm_path = atena_upload(srm_name, remote)
    remote.exec(f"sbatch {srm_path}")
    output = remote.get_output()
    remote.close()
    return output


def create_dev_task(pyname, task):
    """Create and submit a new task to dev"""
    return 1


@app.post("/new_task/")
async def create_task(files: list[UploadFile]):
    """Create new task and save it to DB"""
    # TODO: Split this frankenstein into functions

    for file in files:
        fname = file.filename
        fdata = await file.read()
        fpath = save_file(fname, fdata)
        if ".json" in fname:
            conf_path = fpath
        if ".py" in fname:
            py_name = fname
    task = process_config(conf_path)
    script_name = strip_filename(task['script_path'])
    if script_name != py_name:
        return {
            "msg": f"{script_name} and {py_name} must have same name",
            "status": status.HTTP_400_BAD_REQUEST
        }
    if "atena" in task['runner_location']:
        output = create_atena_task(py_name, task)
    elif "dev" in task['runner_location']:
        output = create_dev_task(py_name, task)
    if output[0]:
        job_id = output[0].split('Submitted batch job ')[1][:-1]
    elif output[1]:
        return {"msg": output[1]}
    task['job_id'] = job_id
    dbm.insert_task(task)
    return dbm.get_task_by_id(task['id'])


@app.post("/dummy_insert_task/")
async def insert_dummy_task():
    """Testing task insertion"""
    dummy_task = {
        "id": "unique_id_2",
        "instance_type": "GPU",
        "image_name": "sklearn_image.sif",
        "account": "twinscie",
        "runner_location": "atena02",
        "script_path": "path/to/my/script.py",
        "dataset_name": "titanic.csv",
        "experiment_name": "task_insertion",
        "job_id": 42,
    }
    dbm.insert_task(dummy_task)
    return dbm.get_task_by_id(dummy_task['id'])


@app.get("/tasks/", response_model=list[Task])
async def get_tasks():
    """Retrieve all saved tasks"""
    return dbm.get_tasks()


@app.get("/task/{task_id}")
async def get_task_by_id(task_id: str):
    """Retreive a single task given task ID"""
    return dbm.get_task_by_id(task_id)


@app.get("/job_status/{job_id}")
async def get_job_status(job_id: int):
    """Retrieve job status given job ID"""
    remote = atena_connect()
    remote.exec(f"squeue -j {job_id} -h --states=all")
    output = remote.get_output()[0]
    job_status = output.split()[4]
    return get_status_message(job_status)
