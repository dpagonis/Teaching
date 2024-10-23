import requests

from .gets import HEADERS, BASE_URL


def send_canvas_message(recipient_id, subject, body):
    endpoint = f"{BASE_URL}/conversations"
    recipient_list = [recipient_id]
    payload = {
        "recipients[]": recipient_list,
        "subject": subject,
        "body": body
    }
    
    response = requests.post(endpoint, headers=HEADERS, data=payload)
    if response.status_code == 201:
        return response.json()
    else:
        print(f"Error {response.status_code}: {response.text}")
        return None