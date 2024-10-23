"""
This script automates the process of granting extra time accommodations for students on quiz assignments in a Canvas LMS course.

It reads a CSV file ('extended_time_students.csv') containing student IDs and their respective time multipliers (e.g., 1.5 for time and a half). The script retrieves all assignments from a specific course in Canvas, identifies the published quizzes, and calculates the extra time needed for each student based on the quiz's original time limit.

For each student who requires extra time, the script posts a quiz extension to the Canvas API. It handles pagination to ensure all assignments are processed and reports success or errors for each extension posted.

Requires:
- A CSV file 'extended_time_students.csv' with columns 'id' (student's Canvas ID) and 'extra_time' (time multiplier). For time-and-a-half the value of extra_time should be 1.5
- 'config.txt' containing the Canvas API token.
- 'COURSE_ID.txt' containing the course ID.

The script uses the Canvas API to interact with the course and quiz data and requires internet connectivity and appropriate API permissions.

Written by Demetrios Pagonis, Weber State University
To generate a canvas API token (for WSU faculty): go to https://weber.instructure.com/profile/settings and click 'new access token'
"""


import requests
import pandas as pd

df_students = pd.read_csv('extended_time_students.csv') #columns are 'id' for student's canvas id and 'extra time' for the time multiplier. 1.5=time and a half

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

endpoint = f"{BASE_URL}/courses/{course_id}/assignments"

assignments_json= []

while endpoint:
    response = requests.get(endpoint, headers=HEADERS)

    if response.status_code == 200:
        assignments_json.extend(response.json())

        # Check for pagination 'next' link
        links = requests.utils.parse_header_links(response.headers['Link'])
        next_link = [link for link in links if link["rel"] == "next"]
        endpoint = next_link[0]["url"] if next_link else None

    else:
        print(f"Error {response.status_code}: {response.text}")
        endpoint = None

quizzes_to_extend = []
for ass in assignments_json:    # for each assignment in the course
    if ass['is_quiz_assignment'] and ass['published']:  # if it is a published quiz, pull its quiz info through quizzes endpoint
        quiz_id = ass['quiz_id']
        quiz = requests.get(f"{BASE_URL}/courses/{course_id}/quizzes/{quiz_id}", headers=HEADERS).json()
        time_allowed = quiz['time_limit']
        if time_allowed is not None:        # if there is a time limit, post a quiz extension for all students with extra time
            for index, student in df_students.iterrows():
                student_id = int(student['id'])
                time_multiplier = student['extra_time']
                extra_time = (time_multiplier*time_allowed)-time_allowed #extension is the amount of *extra* time, but we manage accommodations as 1.5 for time and a half
                endpoint = f"{BASE_URL}/courses/{course_id}/quizzes/{quiz_id}/extensions"
                payload = {
                    "quiz_extensions": [{
                        "user_id": student_id,
                        "extra_time": extra_time
                    }]
                }
                response = requests.post(endpoint, headers=HEADERS, json=payload)
                if response.status_code == 200:
                    print(f'successfully posted extension for {student_id} for assignment {quiz_id}')
                else:
                    print(f"Error {response.status_code}: {response.text}")