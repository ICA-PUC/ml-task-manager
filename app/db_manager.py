"""Database Manager module"""
import oracledb
from sqlmodel import create_engine, Session, select
from .config import settings
from .models.task import Task


class DBManager:
    """Database Manager class for all database related operations"""

    def __init__(self):
        envs = settings.env_confs
        username = envs['DB_USER']
        password = envs['DB_PASSWORD']
        cp = oracledb.ConnectParams()
        cp.parse_connect_string(envs['DB_STRING'])
        self.engine = create_engine(
            f'oracle+oracledb://{username}:{password}@{cp.host}:{cp.port} \
                /?service_name={cp.service_name}')

    def insert_task(self, task):
        """Insert new task into database"""
        with Session(self.engine) as session:
            db_task = Task.model_validate(task)
            session.add(db_task)
            session.commit()
            session.refresh(db_task)
            return db_task

    def get_tasks(self):
        """Fetch all tasks from database"""
        with Session(self.engine) as session:
            statement = select(Task)
            results = session.exec(statement).all()
            return results

    def get_task_by_id(self, task_id):
        """Retreive single task from database given ID"""
        with Session(self.engine) as session:
            statement = select(Task).where(Task.id == task_id)
            results = session.exec(statement).all()
            return results
