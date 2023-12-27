import requests
import json

# Constants
BASE_URL = "https://weber.instructure.com/api/v1"  # Replace with your Canvas domain

# Read the API token from the configuration file
with open("config.txt", "r") as file:
    API_TOKEN = file.readline().strip()

HEADERS = {
    "Authorization": f"Bearer {API_TOKEN}"
}

def fetch_courses():
    """Fetch all courses for the authenticated user."""
    endpoint = f"{BASE_URL}/courses"
    params = {
        "state[]": ["available", "active"]  # adjust the states as needed
    }
    
    all_courses = []
    
    while endpoint:
        response = requests.get(endpoint, headers=HEADERS, params=params)
        
        if response.status_code == 200:
            all_courses.extend(response.json())
            
            # Check for pagination 'next' link
            links = requests.utils.parse_header_links(response.headers['Link'])
            next_link = [link for link in links if link["rel"] == "next"]
            endpoint = next_link[0]["url"] if next_link else None

        else:
            print(f"Error {response.status_code}: {response.text}")
            endpoint = None

    return all_courses



# def fetch_grades_for_course(course_id):
#     """Fetch grade data for a specific course."""
#     endpoint = f"{BASE_URL}/courses/{course_id}/students/submissions"
#     params = {
#         "student_ids[]": "all",
#         "grouped": 1
#     }
#     response = requests.get(endpoint, headers=HEADERS, params=params)
    
#     if response.status_code == 200:
#         return response.json()
#     else:
#         print(f"Error {response.status_code}: {response.text}")
#         return []

if __name__ == "__main__":
    courses = fetch_courses()
    for course in courses:
        course_id = course.get("id")
        course_name = course.get("name")
        
        print(f"Name: {course_name}; ID: {course_id}")
        # grades = fetch_grades_for_course(course_id)
        
        # # Save the grades in a local JSON file
        # with open(f"{course_name}_grades.json", "w") as file:
        #     json.dump(grades, file, indent=4)

    print("Fetching process completed!")
