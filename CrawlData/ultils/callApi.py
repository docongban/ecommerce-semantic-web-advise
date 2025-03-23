import requests

def callApiCellphones(url, payload):
    headers = {
        "Content-Type": "application/json"
    }
    response = requests.post(url, json=payload, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error {response.status_code}: {response.text}")
        return None

def callApiFpt(method, url, payload):
    headers = {
        "Content-Type": "application/json",
        "order-channel": "1",
    }
    response = requests.request(method=method.upper(), url = url, json=payload, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error {response.status_code}: {response.text}")
        return None