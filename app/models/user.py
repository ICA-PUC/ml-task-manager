"""User Model Class"""
from sqlmodel import SQLModel, Field


class User(SQLModel):
    """User base model class

    :param SQLModel: Default SQLModel class
    :type SQLModel: obj
    """
    username: str
    email: str | None = None
    full_name: str | None = None


class fg1n_twincore_user(User, table=True):
    """User class that will reference the table in database"""
    id: str | None = Field(default=None, primary_key=True)
    hashed_password: str
