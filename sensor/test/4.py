from twisted.internet import reactor
import requests
import json

headers = {'Content-Type': 'application/json'}
a = json.dumps({"1": 2})
url = "http://127.0.0.1:5003/post_data"
r = requests.session().post(url, data=a, headers=headers)

print r.text

print r.status_code