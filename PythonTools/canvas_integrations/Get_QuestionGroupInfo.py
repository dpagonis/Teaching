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

quiz_id = 1528778
group_id = 1136995


session = requests.Session()
session.headers.clear()
session.headers.update(HEADERS)


response = session.get(f"{BASE_URL}/courses/{course_id}/quizzes/{quiz_id}/groups/{group_id}")


if response.status_code == 200:
    data = response.json()
    print(json.dumps(data, indent=2))

else:
    print(f"Error {response.status_code}")
