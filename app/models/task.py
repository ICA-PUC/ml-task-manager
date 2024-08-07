"""Task Model Class"""
from sqlmodel import SQLModel, Field


class TaskBase(SQLModel):
    """Task base model class

    :param SQLModel: Default SQLModel class
    :type SQLModel: obj
    """
    instance_type: str
    image_name: str
    account: str
    runner_location: str
    script_path: str
    dataset_name: str
    experiment_name: str
    job_id: int


class ffir_twincore_task(TaskBase, table=True):
    """Task class that will reference the table in database

    :param TaskBase: The base model class
    :type TaskBase: SQLModel
    :param table: SQLModel param to declare as a table, defaults to True
    :type table: bool, optional
    """
    id: str | None = Field(default=None, primary_key=True)
