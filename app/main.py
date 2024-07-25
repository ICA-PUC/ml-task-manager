"""Entrypoint for the Task Manager API Server"""
from typing import Annotated
from fastapi import FastAPI, UploadFile, Depends
from fastapi.security import OAuth2PasswordBearer
from . import utils
from .db_manager import DBManager
from .task_manager import TaskManager

dbm = DBManager()
app = FastAPI()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


@app.post("/new_task/")
async def create_task(files: list[UploadFile],
                      token: Annotated[str, Depends(oauth2_scheme)]):
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


@app.get("/tasks/")
async def get_tasks(token: Annotated[str, Depends(oauth2_scheme)]):
    """Retrieve all saved tasks"""
    return dbm.get_tasks()


@app.get("/task/{task_id}")
async def get_task_by_id(task_id: str,
                         token: Annotated[str, Depends(oauth2_scheme)]):
    """Retreive a single task given task ID"""
    return dbm.get_task_by_id(task_id)


@app.get("/job_status/{job_id}")
async def get_job_status(job_id: int,
                         token: Annotated[str, Depends(oauth2_scheme)]):
    """Retrieve job status given job ID"""
    remote = utils.atena_connect()
    remote.exec(f"squeue -j {job_id} -h --states=all")
    output = remote.get_output()[0]
    job_status = output.split()[4]
    return utils.get_status_message(job_status)


@app.get("/users/")
async def get_users():
    return dbm.get_users()
