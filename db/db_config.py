"""Oracle database connection variables"""
import os

config = {
	'DB_USER': os.environ['DB_USER'],
	'DB_PASSWORD': os.environ['DB_PASSWORD'],
	'DB_DSN': os.environ['DB_DSN']
	}


user = config['DB_USER']
pw = config['DB_PASSWORD']
dsn = config['DB_DSN']

