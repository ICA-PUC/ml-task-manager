"""User creation module"""

import getpass
import os
import oracledb
import db_config_sys
import run_sql_script

# default values
PYTHON_USER = "SYSTEM"

PARAMETERS = {}


def get_value(name, label, default_value=""):
    "Get value from dict, env our default param"
    value = PARAMETERS.get(name)
    if value is not None:
        return value
    value = os.environ.get(name)
    if value is None:
        if default_value:
            label += f" [{default_value}]"
        label += ": "
        if default_value:
            value = input(label).strip()
        else:
            value = getpass.getpass(label)
        if not value:
            value = default_value
    PARAMETERS[name] = value
    return value


def get_main_user():
    "Return the main user from provided confs"
    return get_value("user", "Enter the User to be created", PYTHON_USER)


def get_main_password():
    "Return the main password from provided confs"
    return get_value("pw", f"Enter the Password for {get_main_user()}")


# Connect using the System User ID and password
con = oracledb.connect(
    user=db_config_sys.sysuser,
    password=db_config_sys.syspw,
    dsn=db_config_sys.dsn,
)

# create sample user and schema
print("Creating user...")
run_sql_script.run_sql_script(
    con, "create_user", user=get_main_user(), pw=get_main_password()
)
print("Done.")
