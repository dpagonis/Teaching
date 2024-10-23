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

with open("COURSE_ID.txt", "r") as file:
    course_id = file.readline().strip()

# Disable the default headers set by `requests` by creating a Session
session = requests.Session()
session.headers.clear()
session.headers.update(HEADERS)

response = session.get(f"{BASE_URL}/courses/{course_id}/question_banks")

if response.status_code == 200:
    resp = response.json()
    print(json.dumps(resp,indent=2))
else:
    print(f"Error {response.status_code}: {response.text}")
