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

quiz_id = 1434882 #HW2 practice

# Disable the default headers set by `requests` by creating a Session
session = requests.Session()
session.headers.clear()
session.headers.update(HEADERS)

response = session.get(f"{BASE_URL}/courses/{course_id}/quizzes/{quiz_id}/statistics")

# For debugging
# print(f"HTTP Method: {response.request.method}")
# print(f"URL: {response.request.url}")
# print(f"Headers: {response.request.headers}")


if response.status_code == 200:
    resp = response.json()

    
    stats = resp.get('quiz_statistics')
    

    for k in stats[0].keys():
        print(k)

    print ('------------')
    q_stat = stats[0].get('question_statistics')
    print(len(q_stat))
    for k in q_stat[0].keys():
        print(k)

    print ('------------')
    
    for q in q_stat:
        print(q.get('position'), q.get('correct'))
else:
    print(f"Error {response.status_code}: {response.text}")
