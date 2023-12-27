import requests
import json
from thefuzz import process


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

#assignment_id = 5908007  # Replace with your assignment ID

# Create a session
session = requests.Session()
session.headers.clear()
session.headers.update(HEADERS)

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

assignments_dict = {assignment['name']: assignment['id'] for assignment in assignments_json}

user_input = input("Enter the name of the assignment you are looking for: ")

matches = process.extract(user_input, assignments_dict.keys(), limit=5)

print("Top matches:")
for i, (name, score) in enumerate(matches, start=1):
    print(f"{i}. {name} (Score: {score})")

match_choice = int(input("Enter the number of the correct assignment: "))

# Validate user input
if 1 <= match_choice <= len(matches):
    selected_name = matches[match_choice - 1][0]
    assignment_id = assignments_dict[selected_name]
    print(f"You selected: {selected_name} with ID {assignment_id}")
else:
    print("Invalid selection.")
    assignment_id = None

############ Get rubrics ##############

params = {
    "include[]": ["assessments", "associations"],
    "per_page": 100  # Adjust as needed
}

response = session.get(f"{BASE_URL}/courses/{course_id}/rubrics", params=params)

if response.status_code == 200:
    rubrics_json = response.json()

    with open('Rubrics.json', 'w') as json_file:
        json.dump(rubrics_json, json_file, indent=4)
else:
    print(f"Error {response.status_code}: {response.text}")


rubric_id_to_description = {}
for rubric in rubrics_json:
    rubric_id = rubric.get("id")
    params = {
        "include[]": ["associations"],
        "per_page": 100  # Adjust as needed
    }
    response = session.get(f"{BASE_URL}/courses/{course_id}/rubrics/{rubric_id}", params=params)
    
    if response.status_code == 200:
        rubric_data = response.json()

        # Check if this rubric is associated with the assignment
        associations = rubric_data.get("associations", [])
        if any(assoc.get('association_id') == assignment_id for assoc in associations):
            # Save the rubric data to a file and abort
            with open('Rubric.json', 'w') as file:
                json.dump(rubric_data, file, indent=4)
            print(f"Found and saved rubric with ID {rubric_id}")
            my_rubric = rubric_id

            # Build rubric_id_to_description dictionary
            for item in rubric_data.get("data", []):
                rubric_id = item.get("id")
                description = item.get("description")
                rubric_id_to_description[rubric_id] = description

            break
    else:
        print(f"Error fetching rubric {rubric_id}: {response.status_code} - {response.text}")


##############Look up the selected assignment and get rubric data################

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

        # Get the next page URL from the link header
        next_link = response.links.get('next')
        url = next_link['url'] if next_link else None
    else:
        print(f"Error {response.status_code}: {response.text}")
        break


#capture class-wide performance by rubric
rubric_scores = {}

# Iterate over each submission
for submission in data:
    rubric_assessment = submission.get('rubric_assessment', {})
    
    # Iterate over each rubric item in the submission
    for rubric_id, assessment in rubric_assessment.items():
        if rubric_id not in rubric_scores:
            rubric_scores[rubric_id] = {'met_outcome': 0, 'total': 0}

        # Assuming that a non-zero score means the outcome was met
        if assessment.get('points', 0) > 0:
            rubric_scores[rubric_id]['met_outcome'] += 1
        
        rubric_scores[rubric_id]['total'] += 1

# Now print the class-wide performance for each rubric item
for rubric_id, scores in rubric_scores.items():
    description = rubric_id_to_description.get(rubric_id, "Unknown Rubric Item")
    print(f"{scores['met_outcome']*100/scores['total']:.0f}% ({scores['met_outcome']}/{scores['total']}), met outcome: {description}")
