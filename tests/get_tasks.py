"""Testing tasks route using requests"""
from pprint import pprint
import sys
import requests
from login import login


node_name = sys.argv[1]
auth = login(node_name)
url = f"http://{node_name}:8008/tasks"
headers = {'accept': 'application/json',
           'Authorization': f"{auth['token_type']} {auth['access_token']}"}

response = requests.get(url, headers=headers, timeout=10)
print("response text:")
pprint(response.json())
