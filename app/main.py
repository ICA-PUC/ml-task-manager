"""Entrypoint for the Task Manager API Server"""
import os
import shutil
from contextlib import asynccontextmanager
from dotenv import load_dotenv
from fastapi import FastAPI, UploadFile, status
from sqlmodel import Session, SQLModel, create_engine, select
from .models.task import Task, TaskRead
from .utils import save_file, process_config, get_status_message
from .utils import strip_filename
from .controllers.ssh.handler import RemoteHandler
from .controllers.slurm.slurm_manager import prep_template
from .config import settings

SQLITE_FILE_NAME = "database.db"
sqlite_url = f"sqlite:///{SQLITE_FILE_NAME}"
engine = create_engine(sqlite_url, echo=True)


def create_db_and_tables():
    """initialize db and tables"""
    SQLModel.metadata.create_all(engine)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan function for initialization and shutting down functions"""
    # db.init_db()
    create_db_and_tables()
    load_dotenv()
    os.makedirs('app/tmp', exist_ok=True)

    yield
    # TODO: FIX: this is not running when using `scancel`
    shutil.rmtree('app/tmp')

app = FastAPI(lifespan=lifespan)


def atena_connect():
    """Spawn new remote handler with atena config

    :return: remote handler object connected to atena
    :rtype: RemoteHandler
    """
    remote = RemoteHandler()
    # adjust to the API's user
    host = "atn1mg4"
    user = os.getenv('ATENA_USER')
    passwd = os.getenv('ATENA_PASSWD')
    remote.connect(host, user, passwd)
    return remote


def dev_connect():
    """Spawn new remote handler with dev config

    :return: remote handler object connected to dev slurm
    :rtype: RemoteHandler
    """
    remote = RemoteHandler()
    host = "slurmmanager"
    user = "admin"
    passwd = "admin"
    remote.connect(host, user, passwd)
    return remote


def file_upload(fname, remote_path, remote):
    """Submit job to atena cluster"""
    sanity_check = remote.send_file(fname, remote_path)
    if not sanity_check:
        return status.HTTP_500_INTERNAL_SERVER_ERROR
    return status.HTTP_200_OK


@app.post("/new_task/")
async def create_task(files: list[UploadFile]):
    """Create new task and save it to DB"""
    # TODO: Split this frankenstein into functions
    root_folder = settings.folder

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
        remote = atena_connect()
    else:
        remote = dev_connect()
    file_upload(fname, task['script_path'], remote)
    srm_name = prep_template(task)
    srm_path = f"{root_folder}/{srm_name}"
    file_upload(srm_name, srm_path, remote)
    remote.exec(f"sbatch {srm_path}")
    output = remote.get_output()
    if output[0]:
        job_id = output[0].split('Submitted batch job ')[1][:-1]
    elif output[1]:
        return {"msg": output[1]}
    remote.close()
    task['job_id'] = job_id
    with Session(engine) as session:
        db_task = Task.model_validate(task)
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
    # TODO: Adjust squeue params to prevent using try-except for ended job
    # check squeue --help for options
    remote.exec(f"squeue -j {job_id}")
    output = remote.get_output()[0]
    try:
        job_status = output.splitlines()[1].split()[4]
    except IndexError:
        return output
    return get_status_message(job_status)


if __name__ == "__main__":
    create_db_and_tables()
