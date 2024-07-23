"""Database Manager module"""
from sqlmodel import create_engine, Session, select
from .config import settings
from .models.task import Twincore_task as Task


class DBManager:
    """Database Manager class for all database related operations"""

    def __init__(self):
        envs = settings.env_confs
        username = envs['DB_USER']
        password = envs['DB_PASSWORD']
        host = envs['DB_HOST']
        if envs['DB_NAME'] == "ORACLE":
            port = envs['ORACLE_DB_PORT']
            service_name = envs['ORACLE_DB_SERVICE']
            self.engine = create_engine(
                f'oracle+oracledb://{username}:{password}@{host}:{port} \
                    /?service_name={service_name}')
        else:
            port = envs['PSQL_DB_PORT']
            service_name = envs['PSQL_DB_SERVICE']
            self.engine = create_engine(
                f'postgresql://{username}:{password}@{host}:{port} \
                    /{service_name}'
            )

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


def insert_dummy_task():
    """Testing task insertion"""

    dbm = DBManager()
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


if __name__ == "__main__":
    insert_dummy_task()
