"""simple login module

:return: requests' response
:rtype: json
"""

import sys
import requests


def login(node_name):
    """Perform login on the given node_name and returns the response"""
    url = f"http://{node_name}:8008/auth/login"
    headers = {'accept': 'application/json',
               'Content-Type': 'application/x-www-form-urlencoded'}
    data = {'username': 'admin', 'password': 'admin123'}
    r = requests.post(url, headers=headers, data=data, timeout=10)
    return r.json()


if __name__ == "__main__":
    node = sys.argv[1]
    print(login(node))
