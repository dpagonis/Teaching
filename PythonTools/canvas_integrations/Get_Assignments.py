import requests
import json


with open("COURSE_ID.txt", "r") as file:
    course_id = file.readline().strip()

fout = 'Assignments.json'


#########################################################

BASE_URL = "https://weber.instructure.com/api/v1"

# Load the API token and course ID
with open("config.txt", "r") as file:
    API_TOKEN = file.readline().strip()

HEADERS = {
    "Authorization": f"Bearer {API_TOKEN}"
}

# Disable the default headers set by `requests` by creating a Session
session = requests.Session()
session.headers.clear()
session.headers.update(HEADERS)

endpoint = f"{BASE_URL}/courses/{course_id}/assignments"

all_data = []

while endpoint:
    response = requests.get(endpoint, headers=HEADERS)

    if response.status_code == 200:
        all_data.extend(response.json())

        # Check for pagination 'next' link
        links = requests.utils.parse_header_links(response.headers['Link'])
        next_link = [link for link in links if link["rel"] == "next"]
        endpoint = next_link[0]["url"] if next_link else None

    else:
        print(f"Error {response.status_code}: {response.text}")
        endpoint = None
for a in all_data:
    print(f'{a["name"]} {a["id"]}')
# Save all the data to a JSON file
with open(fout, 'w') as json_file:
    json.dump(all_data, json_file, indent=4)
