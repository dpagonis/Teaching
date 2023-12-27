import requests
import json

# Constants
BASE_URL = "https://weber.instructure.com/api/v1"

# Load the API token and course ID
with open("config.txt", "r") as file:
    API_TOKEN = file.readline().strip()

HEADERS = {
    "Authorization": f"Bearer {API_TOKEN}"
}

submission_id = 20209883


# Disable the default headers set by `requests` by creating a Session
session = requests.Session()
session.headers.clear()
session.headers.update(HEADERS)

params = {

}


response = session.get(f"{BASE_URL}/quiz_submissions/{submission_id}/questions", params=params)

# For debugging
# print(f"HTTP Method: {response.request.method}")
# print(f"URL: {response.request.url}")
# print(f"Headers: {response.request.headers}")


if response.status_code == 200:
    data = response.json()

    with open('Submission_Questions.json', 'w') as json_file:
        json.dump(data, json_file, indent=4)

else:
    print(f"Error {response.status_code}: {response.text}")
