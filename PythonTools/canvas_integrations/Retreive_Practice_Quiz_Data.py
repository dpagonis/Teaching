import requests
import json
import time
import pandas as pd
from io import StringIO
from collections import Counter



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


# Create a session
session = requests.Session()
session.headers.clear()
session.headers.update(HEADERS)

endpoint = f"{BASE_URL}/courses/{course_id}/quizzes"

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


assignments_dict = {assignment['title']: assignment['id'] for assignment in assignments_json}

matches = [(name, id) for name, id in assignments_dict.items() if 'practice' in name.lower()]

print(f'Found {len(matches)} practice quizzes.')

############ Get reports ##############

student_set = set()
student_counter = Counter()

params = {
    "quiz_report[report_type]":"student_analysis",
    "include":["file"],
    "quiz_report[includes_all_versions]":"true"
}

# Iterate over each assignment in matches
for assignment_name, id in matches:
    response = session.post(f"{BASE_URL}/courses/{course_id}/quizzes/{id}/reports", params=params)

    if response.status_code == 200:
        data = response.json()

        # Assuming that the report creation process is similar to the quiz report process
        progress_url = data.get('progress_url')
        report_id = data.get('id')

        while True:
            progress_response = session.get(progress_url)
            if progress_response.status_code == 200:
                progress = progress_response.json()
                status = progress.get('completion', 0)
                if status == 100:
                    response = session.get(f"{BASE_URL}/courses/{course_id}/quizzes/{id}/reports/{report_id}", params=params)
                    report_data = response.json()
                    download_url = report_data.get('file', {}).get('url')
                    print(f'Report generation {status}% complete for assignment {assignment_name}')
                    break
                else:
                    print(f'Report generation {status}% complete for assignment {assignment_name}')
                    time.sleep(2) 
            else:
                print(f"Error {progress_response.status_code}: {progress_response.text}")

        if download_url:
            response = session.get(download_url)

            if response.status_code == 200:
                # Read the content directly into a DataFrame
                df = pd.read_csv(StringIO(response.text))
                
                for id in df['id']:
                    student_set.add(id)
                student_counter.update(df['name'])
            else:
                print(f"Failed to download the file for assignment {assignment_name}. Status code: {response.status_code}")
        else:
            print(f"Error {response.status_code} for assignment {assignment_name}: {response.text}")
    
    else:
        print(f"Error {response.status_code} for assignment {assignment_name}: {response.text}")


print('')
print('############# FINAL OUTPUT #############')
print(f'{len(student_set)} students took practice quizzes')
for id, count in student_counter.items():
    print(f"ID: {id}, Count: {count}")