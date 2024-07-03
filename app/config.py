"""Compose environment loader
"""
import os
from pydantic_settings import BaseSettings
from pydantic import Field
from dotenv import dotenv_values


class Settings(BaseSettings):
    """Database settings class

    :param BaseSettings: pydantic base settings class
    :type BaseSettings: class
    """
    env_confs: dict = dotenv_values(".env", verbose=True)
    db_url: str = env_confs["DATABASE_URL"]
    atena_root: str = Field(validation_alias='ATENA_ROOT')


settings = Settings()
