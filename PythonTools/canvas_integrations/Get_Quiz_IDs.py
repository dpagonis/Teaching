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

course_id = 559270 #input("Enter the course ID: ")


params = {"page": 1, "per_page": 100}

# Disable the default headers set by `requests` by creating a Session
session = requests.Session()
session.headers.clear()
session.headers.update(HEADERS)


response = session.get(f"{BASE_URL}/courses/{course_id}/quizzes", params=params)


if response.status_code == 200:
    resp = response.json()

    for i in resp:
        print(i.get('id'), i.get('title'))

    


else:
    print(f"Error {response.status_code}: {response.text}")
