"""Database Manager module"""
from sqlmodel import create_engine, Session, select
from app.config import settings
from app.models.task import ffir_twincore_task as Task
from app.models.user import ffir_twincore_user as User


class DBManager:
    """Database Manager class for all database related operations"""

    def __init__(self):
        envs = settings.env_confs
        username = envs['DB_USER']
        password = envs['DB_PASSWORD']
        host = envs['DB_HOST']
        port = envs['ORACLE_DB_PORT']
        service_name = envs['ORACLE_DB_SERVICE']
        self.engine = create_engine(
            f'oracle+oracledb://{username}:{password}@{host}:{port} \
                /?service_name={service_name}')

    def insert_task(self, task):
        """Insert new task into database"""
        with Session(self.engine) as session:
            db_task = Task.model_validate(task)
            session.add(db_task)
            session.commit()
            session.refresh(db_task)
            return db_task

    def insert_user(self, user):
        """Insert new user into db"""
        with Session(self.engine) as session:
            db_user = User.model_validate(user)
            session.add(db_user)
            session.commit()
            session.refresh(db_user)
            return db_user

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

    def get_users(self):
        """Fetch all users from database"""
        with Session(self.engine) as session:
            statement = select(User)
            results = session.exec(statement).all()
            return results

    def get_user_by_name(self, username):
        """Retrieve user data"""
        with Session(self.engine) as session:
            statement = select(User).where(User.username == username)
            results = session.exec(statement).one()
            return results

    def get_task_by_job_id(self, job_id):
        """Retreive single task from database given ID"""
        with Session(self.engine) as session:
            statement = select(Task).where(Task.job_id == job_id)
            results = session.exec(statement).all()
            return results
