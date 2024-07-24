"""Module to run SQL scripts using python-oracledb"""
import os
import sys


def run_sql_script(conn, script_name, **kwargs):
    """Run the given script name with the given connection object. 
    Script must be present in folder ./sql/"""
    statement_parts = []
    cursor = conn.cursor()
    replace_values = [("&" + k + ".", v) for k, v in kwargs.items()] + [
        ("&" + k, v) for k, v in kwargs.items()
    ]
    script_dir = os.path.dirname(os.path.abspath(sys.argv[0]))
    file_name = os.path.join(script_dir, "sql", script_name + ".sql")
    print("SQL File Name: ", file_name)
    for line in open(file_name, encoding='utf-8'):
        if line.strip() == "/":
            statement = "".join(statement_parts).strip()
            if statement:
                for search_value, replace_value in replace_values:
                    statement = statement.replace(search_value, replace_value)
                try:
                    cursor.execute(statement)
                except:
                    print("Failed to execute SQL:", statement)
                    raise
            statement_parts = []
        else:
            statement_parts.append(line)
    cursor.execute(
        """
        select name, type, line, position, text
        from dba_errors
        where owner = upper(:owner)
        order by name, type, line, position
        """,
        owner=kwargs["user"],
    )
    prev_name = prev_obj_type = None
    for name, obj_type, line_num, position, text in cursor:
        if name != prev_name or obj_type != prev_obj_type:
            print("%s (%s)" % (name, obj_type))
            prev_name = name
            prev_obj_type = obj_type
        print("    %s/%s %s" % (line_num, position, text))
