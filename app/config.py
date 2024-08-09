"""Environment loader"""
from pydantic_settings import BaseSettings
from pydantic import Field
from dotenv import dotenv_values


class Settings(BaseSettings):
    """Database settings class

    :param BaseSettings: pydantic base settings class
    :type BaseSettings: class
    """
    env_confs: dict = dotenv_values(".env", verbose=True)
    atena_root: str = Field(validation_alias='ATENA_ROOT')
    nfs_root: str = Field(validation_alias='NFS_ROOT')
    sif_root: str = Field(validation_alias='SIF_PATH')


settings = Settings()
