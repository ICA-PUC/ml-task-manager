"""Oracle database connection variables"""
import os

sysuser = os.environ.get("PYTHON_SYSUSER", "SYSTEM")
syspw = os.environ.get("PYTHON_SYSPASSWORD", "Digital_twin_db42")
dsn = os.environ.get("PYTHON_CONNECT_STRING",
                     "localhost/ORCLPDB1")
