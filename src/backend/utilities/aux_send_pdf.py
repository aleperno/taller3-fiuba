import requests
import json
import base64

HEADERS =  {"Content-Type": "application/json"}

file = open('/tmp/template.pdf', 'rb').read()
encoded = base64.b64encode(file).decode('utf8')
response = requests.post('http://127.0.0.1:8080/uploadfile', data=json.dumps({'file_content': encoded}), headers=HEADERS)
print(response.json())
