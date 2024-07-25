"""Insert admin user into twincore_user table"""
import oracledb
import db_config
import run_sql_script

con = oracledb.connect(
    user=db_config.user, password=db_config.pw, dsn=db_config.dsn
)

run_sql_script.run_sql_script(con, "insert_admin_user", user=db_config.user)

print("Done.")
