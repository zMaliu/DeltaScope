import urllib.request
import json

url = "http://127.0.0.1:5000/api/common/auth/register"
data = {
    "phone": "13800138000",
    "password": "password123",
    "role": "student"
}
req = urllib.request.Request(url, data=json.dumps(data).encode('utf-8'), headers={'Content-Type': 'application/json'}, method='POST')

try:
    with urllib.request.urlopen(req) as response:
        result = response.read()
        print("Success:", result.decode('utf-8'))
except urllib.error.HTTPError as e:
    print("Error:", e.code)
    print("Response:", e.read().decode('utf-8'))
