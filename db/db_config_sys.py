"""Oracle database connection variables"""
import os

sysuser = os.environ.get("PYTHON_SYSUSER", "C5KI")
syspw = os.environ.get("PYTHON_SYSPASSWORD", "nNe#1Eqaiv")
dsn = os.environ.get("PYTHON_CONNECT_STRING",
                     "bdc5kit.petrobras.com.br:1521/c5kit.petrobras.com.br")
