#!/bin/sh

curl -X 'POST' \
  'http://atn1b03n24:8008/auth/login' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/x-www-form-urlencoded' \
  -d 'grant_type=&username=admin&password=admin123&scope=&client_id=&client_secret='

