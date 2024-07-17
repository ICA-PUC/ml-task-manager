import requests
import sys

node_name = sys.argv[1]
url = f"http://{node_name}:8008/tasks"

response = requests.get(url)
print("response.text:", response.text)
