"""Create twincore_user table with current user"""
import oracledb
import db_config
import run_sql_script

con = oracledb.connect(
    user=db_config.user, password=db_config.pw, dsn=db_config.dsn
)

run_sql_script.run_sql_script(con, "create_user_table", user=db_config.user)

print("Done.")
