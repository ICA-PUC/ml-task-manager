"""Entrypoint for the Task Manager API Server"""
from fastapi import FastAPI, UploadFile
from . import utils
from .controllers.ssh.handler import RemoteHandler
from .db_manager import DBManager
from .task_manager import TaskManager
from .file_manager import FileManager


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
    task_manager = TaskManager(task_id)
    await task_manager.process_files(files)
    output = task_manager.run_task()
    dbm.insert_task(output)
    return dbm.get_task_by_id(output['id'])


@app.get("/tasks/")
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
    remote = utils.atena_connect()
    remote.exec(f"squeue -j {job_id} -h --states=all")
    output = remote.get_output()[0]
    job_status = output.split()[4]
    return utils.get_status_message(job_status)
