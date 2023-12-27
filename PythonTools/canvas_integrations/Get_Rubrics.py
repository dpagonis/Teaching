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

params = {
    "include[]": ["assessments", "associations"],
    "per_page": 100  # Adjust as needed
}

response = session.get(f"{BASE_URL}/courses/{course_id}/rubrics", params=params)

# For debugging
# print(f"HTTP Method: {response.request.method}")
# print(f"URL: {response.request.url}")
# print(f"Headers: {response.request.headers}")


if response.status_code == 200:
    data = response.json()

    with open('Rubrics.json', 'w') as json_file:
        json.dump(data, json_file, indent=4)

else:
    print(f"Error {response.status_code}: {response.text}")
