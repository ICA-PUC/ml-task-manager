"""Oracle database connection variables"""
from dotenv import dotenv_values

config = dotenv_values("../.env")

user = config['DB_USER']
pw = config['DB_PASSWORD']
dsn = config['DB_DSN']
