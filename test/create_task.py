import sys
from pprint import pprint
import requests

node_name = sys.argv[1]

url = f"http://{node_name}:8008/new_task"
files = [("files", open("submiter_confs.json", "rb", encoding='utf-8')),
         ("files", open("test.py", "rb", encoding='utf-8'))]

print("antes de enviar")
response = requests.post(url, files=files)
print("depois de enviar")

print("response.text:")
pprint(response.json())
