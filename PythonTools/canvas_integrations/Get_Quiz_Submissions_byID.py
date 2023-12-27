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
course_id = 559270 #1225
quiz_id = 1374628
user_id = 1880054

# Disable the default headers set by `requests` by creating a Session
session = requests.Session()
session.headers.clear()
session.headers.update(HEADERS)

endpoint = f"{BASE_URL}/users/{user_id}/missing_submissions"
all_submissions = []
params = {}
while endpoint:
    response = session.get(endpoint, params=params)

    if response.status_code == 200:
        all_submissions.extend(response.json()['quiz_submissions'])

        # Check for pagination 'next' link
        links = requests.utils.parse_header_links(response.headers['Link'])
        next_link = [link for link in links if link["rel"] == "next"]
        endpoint = next_link[0]["url"] if next_link else None

    else:
        print(f"Error {response.status_code}")
        endpoint = None

# Save all the quiz submissions to a JSON file
print(f'found {len(all_submissions)} submissions')
with open('Quiz_Submissions_ByID.json', 'w') as json_file:
    json.dump({"quiz_submissions": all_submissions}, json_file, indent=4)