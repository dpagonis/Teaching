import requests
import json

# Constants
BASE_URL = "https://weber.instructure.com/api/v1"

# Read the API token from the configuration file
with open("config.txt", "r") as file:
    API_TOKEN = file.readline().strip()

HEADERS = {
    "Authorization": f"Bearer {API_TOKEN}"
}

with open("COURSE_ID.txt", "r") as file:
    COURSE_ID = file.readline().strip()

def fetch_grades_for_course(course_id):
    """Fetch grade data for a specific course."""
    endpoint = f"{BASE_URL}/courses/{course_id}/students/submissions"
    params = {
        "student_ids[]": "all",
    }
    
    all_grades = []
    
    while endpoint:
        response = requests.get(endpoint, headers=HEADERS, params=params)
        if response.status_code == 200:
            all_grades.extend(response.json())
            
            # Check for pagination and set the next endpoint
            links = response.headers.get('Link', '').split(',')
            endpoint = None
            for link in links:
                if 'rel="next"' in link:
                    endpoint = link.split(';')[0].strip('<>')
                    break

        else:
            print(f"Error {response.status_code}: {response.text}")
            break

    return all_grades

if __name__ == "__main__":
    course_id = COURSE_ID

    print(f"Fetching grades for course ID: {course_id}")
    grades = fetch_grades_for_course(course_id)
    
    # Save the grades in a local JSON file
    with open(f"course_{course_id}_grades.json", "w") as file:
        json.dump(grades, file, indent=4)

    print(f"Grades for course ID {course_id} have been saved to 'course_{course_id}_grades.json'!")
