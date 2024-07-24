import sys
from pprint import pprint
import requests

node_name = sys.argv[1]

url = f"http://{node_name}:8008/new_task"
files = [("files", open("submiter_confs.json", "rb")),
         ("files", open("test.py", "rb"))]

print("antes de enviar")
response = requests.post(url, files=files, timeout=10)
print("depois de enviar")

print("response.text:")
pprint(response.json())
