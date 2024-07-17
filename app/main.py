"""Entrypoint for the Task Manager API Server"""
from contextlib import asynccontextmanager
from fastapi import FastAPI, UploadFile, status
from sqlmodel import Session, SQLModel, create_engine, select
from .models.task import Task
from .utils import save_file, process_config, get_status_message
from .utils import strip_filename
from .controllers.ssh.handler import RemoteHandler
from .controllers.slurm.slurm_manager import prep_template
from .config import settings
import datetime
import random

from .task_manager import TaskManager

SQLITE_FILE_NAME = "database.db"
sqlite_url = f"sqlite:///{SQLITE_FILE_NAME}"
engine = create_engine(sqlite_url, echo=True)


def create_db_and_tables():
    """initialize db and tables"""
    SQLModel.metadata.create_all(engine)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan function for initialization and shutting down functions"""
    create_db_and_tables()
    yield

app = FastAPI(lifespan=lifespan)


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


# @app.post("/new_task/")
# async def create_task(files: list[UploadFile]):
#     """Create new task and save it to DB"""
#     # TODO: Split this frankenstein into functions
#     task_id = datetime.datetime.now().strftime('%Y%m%d%H%M%S%f') + f"{random.randint(0, 9999):04d}"
#     for file in files:
#         fname = file.filename
#         fdata = await file.read()
#         fpath = save_file(fname, fdata, task_id)
#         if ".json" in fname:
#             conf_path = fpath
#         if ".py" in fname:
#             py_name = fname
#     print(f'Essas sao as minhas files {files}')
#     print(f'Esse é o conf_path: {conf_path}')
#     print(f'Essas é o fpath {fpath}')
#     print(f'Essas é o fname {fname}')
#     task = process_config(conf_path)
#     print(f'Essas é o task {task}')
#     script_name = strip_filename(task['script_path'])
#     if script_name != py_name:
#         return {
#             "msg": f"{script_name} and {py_name} must have same name",
#             "status": status.HTTP_400_BAD_REQUEST
#         }
#     if "atena" in task['runner_location']:
#         output = create_atena_task(py_name, task)
#     elif "dev" in task['runner_location']:
#         output = create_dev_task(py_name, task)
#     if output[0]:
#         job_id = output[0].split('Submitted batch job ')[1][:-1]
#     elif output[1]:
#         return {"msg": output[1]}
#     task['job_id'] = job_id
#     with Session(engine) as session:
#         db_task = Task.model_validate(task)
#         session.add(db_task)
#         session.commit()
#         session.refresh(db_task)
#         return db_task

@app.post("/new_task/")
async def create_task(files: list[UploadFile]):
    """Create new task and save it to DB"""
    # TODO: Split this frankenstein into functions
    task_id = datetime.datetime.now().strftime('%Y%m%d%H%M%S%f') + f"{random.randint(0, 9999):04d}"
    for file in files:
        fname = file.filename
        fdata = await file.read()
        fpath = save_file(fname, fdata, task_id)
        if ".json" in fname:
            conf_path = fpath
        if ".py" in fname:
            py_name = fname
    task_manager = TaskManager(task_id, py_name, conf_path, engine)
    output = task_manager.run_task()
    with Session(engine) as session:
        db_task = Task.model_validate(output)
        session.add(db_task)
        session.commit()
        session.refresh(db_task)
        return db_task


@app.get("/tasks/", response_model=list[Task])
async def get_tasks():
    """Retrieve all saved tasks"""
    with Session(engine) as session:
        tasks = session.exec(select(Task)).all()
        return tasks


@app.get("/job_status/{job_id}")
async def get_job_status(job_id: int):
    """Retrieve job status given ID"""
    remote = atena_connect()
    remote.exec(f"squeue -j {job_id} -h --states=all")
    output = remote.get_output()[0]
    job_status = output.split()[4]
    return get_status_message(job_status)


if __name__ == "__main__":
    create_db_and_tables()
