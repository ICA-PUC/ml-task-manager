"""Create new task with testing files"""
import sys
from pprint import pprint
import requests
from login import login

node_name = sys.argv[1]
auth = login(node_name)
url = f"http://{node_name}:8008/new_task"
headers = {'accept': 'application/json',
           'Authorization': f"{auth['token_type']} {auth['access_token']}"}
files = [("files", open("data/submiter_confs.json", "rb")),
         ("files", open("data/files.zip", "rb"))]

print("antes de enviar")
response = requests.post(url, headers=headers, files=files, timeout=10)
print("depois de enviar")

print("response.text:")
pprint(response.json())
