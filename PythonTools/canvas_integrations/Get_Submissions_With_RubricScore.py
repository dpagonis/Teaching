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

assignment_id = 5908007  # Replace with your assignment ID

# Create a session
session = requests.Session()
session.headers.clear()
session.headers.update(HEADERS)

params = {
    "include[]": ["rubric_assessment"],
    "per_page": 100  # Adjust as needed
}

url = f"{BASE_URL}/courses/{course_id}/assignments/{assignment_id}/submissions"

while url:
    response = session.get(url, params=params)

    if response.status_code == 200:
        data = response.json()

        with open('Submissions_With_Rubric_Score.json', 'w') as file:
            json.dump(data, file, indent=4)


        if not data:
            break  # Break the loop if there is no data

        print(len(data))

        for i in data:
            print('assignment:', i.get('id'))
            rubric = i.get('rubric_assessment')
            if rubric:
                for key, value in rubric.items():
                    print(f"Key: {key}, Points: {value['points']}")

        # Get the next page URL from the link header
        next_link = response.links.get('next')
        url = next_link['url'] if next_link else None
    else:
        print(f"Error {response.status_code}: {response.text}")
        break