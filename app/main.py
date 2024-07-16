"""Entrypoint for the Task Manager API Server"""
from contextlib import asynccontextmanager
from fastapi import FastAPI, UploadFile, status
from sqlmodel import Session, SQLModel, create_engine, select
from .models.task import Task
from .utils import save_file, process_config, get_status_message, strip_filename, create_task_id
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


def atena_upload(fname, remote, task_id: str):
    """Submit job to atena cluster"""
    root = settings.atena_root
    file_path = f"{root}/scripts/{task_id}/{fname}"
    sanity_check = remote.send_file(fname, file_path, task_id)
    if not sanity_check:
        return status.HTTP_500_INTERNAL_SERVER_ERROR
    return file_path


def create_atena_task(task):
    """Create and submit a new task to atena"""
    remote = atena_connect()
    atena_upload(strip_filename(task['script_path']), remote, task['id'])
    srm_name = prep_template(task)
    srm_path = atena_upload(srm_name, remote, task['id'])
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
    task_id = create_task_id()
    for file in files:
        fname = file.filename
        fdata = await file.read()
        fpath = save_file(fname, fdata, task_id)
        if ".json" in fname:
            conf_path = fpath
        if ".py" in fname:
            py_path = fpath
            py_name = fname
    task = process_config(conf_path)
    task['id'] = task_id
    script_name = strip_filename(task['script_path'])
    if script_name != py_name:
        return {
            "msg": f"{script_name} and {py_name} must have same name",
            "status": status.HTTP_400_BAD_REQUEST
        }
    if "atena" in task['runner_location']:
        output = create_atena_task(task)
    elif "dev" in task['runner_location']:
        output = create_dev_task(task)
    if output[0]:
        job_id = output[0].split('Submitted batch job ')[1][:-1]
    elif output[1]:
        return {"msg": output[1]}
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
    remote.exec(f"squeue -j {job_id} -h --states=all")
    output = remote.get_output()[0]
    job_status = output.split()[4]
    return get_status_message(job_status)


if __name__ == "__main__":
    create_db_and_tables()
