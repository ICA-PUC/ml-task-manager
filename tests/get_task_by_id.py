"""Get task with given ID"""
from pprint import pprint
import sys
import requests
from login import login

node_name = sys.argv[1]
task_id = sys.argv[2]
auth = login(node_name)

url = f"http://{node_name}:8008/task/{task_id}"
headers = {'accept': 'application/json',
           'Authorization': f"{auth['token_type']} {auth['access_token']}"}

response = requests.get(url, headers=headers, timeout=10)
print("response text:")
pprint(response.json())
