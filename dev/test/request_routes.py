"""Request example using python modules"""
import requests

url = "http://localhost:8008/test_files"
files = [("files", open("submiter_confs.json", "rb")),
         ("files", open("test.py", "rb"))]

response = requests.post(url, files=files)

print(response.text)
