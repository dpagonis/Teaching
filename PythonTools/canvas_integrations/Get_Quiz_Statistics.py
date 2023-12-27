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

course_id = 570517 #input("Enter the course ID: ")
quiz_id = 1434899 # Practice HW 1 (practice)
#quiz_id = 1505899 # Practice HW 7 (graded)


# Disable the default headers set by `requests` by creating a Session
session = requests.Session()
session.headers.clear()
session.headers.update(HEADERS)

params = {
    "all_versions":"True"
}


response = session.get(f"{BASE_URL}/courses/{course_id}/quizzes/{quiz_id}/statistics", params=params)

# For debugging
# print(f"HTTP Method: {response.request.method}")
# print(f"URL: {response.request.url}")
# print(f"Headers: {response.request.headers}")


if response.status_code == 200:
    data = response.json()

    with open('Quiz_Statistics.json', 'w') as json_file:
        json.dump(data, json_file, indent=4)

else:
    print(f"Error {response.status_code}: {response.text}")
