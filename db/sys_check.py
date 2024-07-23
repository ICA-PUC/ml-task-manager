"""Oracle database connection test module"""
import oracledb
import db_config_sys

con = oracledb.connect(
    user=db_config_sys.sysuser,
    password=db_config_sys.syspw,
    dsn=db_config_sys.dsn
)
print("Database version:", con.version)
