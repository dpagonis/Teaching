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

course_id = 570517
quiz_id = 1434880
group_id = 994724


session = requests.Session()
session.headers.clear()
session.headers.update(HEADERS)


response = session.get(f"{BASE_URL}/courses/{course_id}/quizzes/{quiz_id}/groups/{group_id}")

# For debugging
# print(f"HTTP Method: {response.request.method}")
# print(f"URL: {response.request.url}")
# print(f"Headers: {response.request.headers}")


if response.status_code == 200:
    data = response.json()
    print(data)
    with open('Question_Group_Info.json', 'w') as json_file:
        json.dump(data, json_file, indent=4)


else:
    print(f"Error {response.status_code}")
