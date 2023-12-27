import requests
import json
import time

# Constants
BASE_URL = "https://weber.instructure.com/api/v1"

# Load the API token and course ID
with open("config.txt", "r") as file:
    API_TOKEN = file.readline().strip()

HEADERS = {
    "Authorization": f"Bearer {API_TOKEN}"
}

course_id = 570517 #input("Enter the course ID: ")
quiz_id = 1434880 #input("Enter the quiz ID: ")


# Disable the default headers set by `requests` by creating a Session
session = requests.Session()
session.headers.clear()
session.headers.update(HEADERS)

params = {
    "quiz_report[report_type]":"student_analysis",
    "include":["file"],
    "quiz_report[includes_all_versions]":"true"
}

response = session.post(f"{BASE_URL}/courses/{course_id}/quizzes/{quiz_id}/reports", params=params)



if response.status_code == 200:
    data = response.json()
    if data['report_type'] == 'student_analysis':
        progress_url = data['progress_url']
        report_id = data['id']
    with open('Quiz_Report.json', 'w') as json_file:
        json.dump(data, json_file, indent=4)
else:
    print(f"Error {response.status_code}: {response.text}")


while True:
    progress_response = session.get(progress_url)
    if progress_response.status_code == 200:
        progress = progress_response.json()
        status = progress['completion']
        if status==100:
            response = session.get(f"{BASE_URL}/courses/{course_id}/quizzes/{quiz_id}/reports/{report_id}", params=params)
            data = response.json()
            if 'file' in data and 'url' in data['file']:
                download_url = data['file']['url']
            else:
                # Handle the case where the keys are missing
                download_url = None
            break
        else:
            print(f'Report generation {status} % complete')
            time.sleep(0.2) 
    else:
        print(f"Error {progress_response.status_code}: {progress_response.text}")

response = session.get(download_url, stream=True)

# Check if the request was successful
if response.status_code == 200:
    # Determine the desired local file path
    local_filepath = "QuizReport_Student.csv"  # Replace with your desired path and filename

    # Save the content to the local file
    with open(local_filepath, 'wb') as file:
        for chunk in response.iter_content(chunk_size=8192):
            file.write(chunk)

    print(f'File saved to {local_filepath}.')
else:
    print(f"Failed to download the file. Status code: {response.status_code}")