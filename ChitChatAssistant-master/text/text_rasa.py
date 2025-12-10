import requests

url = 'http://127.0.0.1:5005/webhooks/rest/webhook'
payload = {
    "sender": "jiangdg",
    "message": "hello"
}
response = requests.post(url, json=payload)
print(response.text)
