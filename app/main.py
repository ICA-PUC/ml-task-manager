"""Entrypoint for the Task Manager API Server"""
from fastapi import FastAPI, UploadFile
from .models.task import Task
from . import utils
from .controllers.ssh.handler import RemoteHandler
from .db_manager import DBManager
from .task_manager import TaskManager


dbm = DBManager()
app = FastAPI()


def dev_connect():
    """Spawn new remote handler with dev config"""
    remote = RemoteHandler()
    host = "slurmmanager"
    user = "admin"
    passwd = "admin"
    remote.connect(host, user, passwd)
    return remote


@app.post("/new_task/")
async def create_task(files: list[UploadFile]):
    """Create new task and save it to DB"""
    task_id = utils.create_task_id()
    for file in files:
        fname = file.filename
        fdata = await file.read()
        fpath = utils.save_file(fname, fdata, task_id)
        if ".json" in fname:
            conf_path = fpath
        if ".py" in fname:
            py_name = fname
    task_manager = TaskManager(task_id, py_name, conf_path)
    output = task_manager.run_task()
    dbm.insert_task(output)
    return dbm.get_task_by_id(output['id'])


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
    return utils.get_status_message(job_status)
