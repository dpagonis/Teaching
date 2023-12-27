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


rubric_id = 643638

# Disable the default headers set by `requests` by creating a Session
session = requests.Session()
session.headers.clear()
session.headers.update(HEADERS)


response = session.get(f"{BASE_URL}/courses/{course_id}/rubrics/{rubric_id}")

# For debugging
# print(f"HTTP Method: {response.request.method}")
# print(f"URL: {response.request.url}")
# print(f"Headers: {response.request.headers}")


if response.status_code == 200:
    resp = response.json()

    data = resp.get('data')

    for i in data:
        print(i.get('id'),i.get('description'))


else:
    print(f"Error {response.status_code}: {response.text}")
