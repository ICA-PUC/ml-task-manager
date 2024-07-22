import requests
import sys

node_name = sys.argv[1]
url = f"http://{node_name}:8008/dummy_insert_task"

response = requests.post(url)
print("response.text:", response.text)
