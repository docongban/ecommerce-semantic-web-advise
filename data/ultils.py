import requests

def callApiCellphones(url, payload):
    headers = {
        "Content-Type": "application/json"
    }
    response = requests.post(url, json=payload, headers=headers)
    if response.status_code == 200:
        print(response.json())
        return response.json()
    else:
        print(f"Error {response.status_code}: {response.text}")
        return None