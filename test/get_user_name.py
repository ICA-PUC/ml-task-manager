from pprint import pprint
import sys
import requests

node_name = sys.argv[1]
username = sys.argv[2]
url = f"http://{node_name}:8008/users/{username}"

response = requests.get(url)
print("response text:")
pprint(response.json())
