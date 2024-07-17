"""Entrypoint for the Task Manager API Server"""
from contextlib import asynccontextmanager
from fastapi import FastAPI, UploadFile, status
from sqlmodel import Session, SQLModel, create_engine, select
from .models.task import Task
from .utils import save_file, get_status_message, create_task_id
from .controllers.ssh.handler import RemoteHandler
from .config import settings
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
    # TODO: Split this frankenstein into functions
    task_id = create_task_id()
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
