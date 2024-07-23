"""Create twincore_task table with current user"""
import oracledb
import db_config
import run_sql_script

# Connect using the System User ID and password
con = oracledb.connect(
    user=db_config.user, password=db_config.pw, dsn=db_config.dsn
)

# create twincore_task table
run_sql_script.run_sql_script(
    con, "create_table", user=db_config.user, pw=db_config.pw,
    dsn=db_config.dsn
)
print("Done.")
