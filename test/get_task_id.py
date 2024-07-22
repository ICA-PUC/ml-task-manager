import requests
import sys

node_name = sys.argv[1]
task_id = sys.argv[2]

url = f"http://{node_name}:8008/task/{task_id}"

response = requests.get(url)
print("response.text:", response.text)