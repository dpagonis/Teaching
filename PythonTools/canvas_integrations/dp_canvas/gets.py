import requests
import json
import time 
import os
import csv
import re
from difflib import SequenceMatcher

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

def create_gradebook():
    # Function to handle pagination
    def fetch_paginated_data(url):
        while url:
            response = requests.get(url, headers=HEADERS)
            if response.status_code == 200:
                data = response.json()
                for item in data:
                    yield item
                # Check for next page link
                links = response.links
                url = links['next']['url'] if 'next' in links else None
            else:
                raise Exception(f"Failed to fetch data: {response.status_code}")

    # Endpoint for fetching students
    initial_url = f"{BASE_URL}/courses/{course_id}/enrollments?type[]=StudentEnrollment&per_page=100"

    # Fetch and parse student data
    student_data = []
    for student in fetch_paginated_data(initial_url):
        student_info = {
            'id': student.get('user_id'),
            'name': student.get('user', {}).get('name'),
            'email': student.get('user', {}).get('email')
        }
        student_data.append(student_info)

    # Saving data to CSV
    csv_file = "gradebook.csv"
    with open(csv_file, 'w', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=['id', 'name', 'email'])
        writer.writeheader()
        writer.writerows(student_data)

def get_assignments(course_id=course_id, force_download=False, skip_download=False):
    
    filename = f"data/{course_id}_assignments.json"
    data_folder_exists = os.path.isdir("data")

    if data_folder_exists: 
        if os.path.exists(filename) and not force_download:
            file_mod_time = os.path.getmtime(filename)
            if (time.time() - file_mod_time < 3600) or skip_download:  # 3600 seconds = 1 hour
                with open(filename, 'r') as file:
                    assignments = json.load(file)
                return assignments
    else:
        os.makedirs("data")
    

    # if not using local copy, hit API
    assignments = []
    endpoint = f"{BASE_URL}/courses/{course_id}/assignments"
    while endpoint:
        response = requests.get(endpoint, headers=HEADERS)

        if response.status_code == 200:
            assignments.extend(response.json())

            # Check for pagination 'next' link
            links = requests.utils.parse_header_links(response.headers['Link'])
            next_link = [link for link in links if link["rel"] == "next"]
            endpoint = next_link[0]["url"] if next_link else None
        else:
            raise ValueError(f"Error {response.status_code}: {response.text}")
    

    with open(filename, 'w') as file:
        json.dump(assignments, file)

    return assignments

def get_quizzes(course_id=course_id, force_download=False, skip_download=False):
    
    filename = f"data/{course_id}_quizzes.json"
    data_folder_exists = os.path.isdir("data")

    if data_folder_exists: 
        if os.path.exists(filename) and not force_download:
            file_mod_time = os.path.getmtime(filename)
            if (time.time() - file_mod_time < 3600) or skip_download:  # 3600 seconds = 1 hour
                with open(filename, 'r') as file:
                    quizzes = json.load(file)
                return quizzes
    else:
        os.makedirs("data")

    # if not using local copy, hit API
    endpoint = f"{BASE_URL}/courses/{course_id}/quizzes"
    quizzes = []

    while endpoint:
        response = requests.get(endpoint, headers=HEADERS)

        if response.status_code == 200:
            quizzes.extend(response.json())

            # Check for pagination 'next' link
            links = requests.utils.parse_header_links(response.headers['Link'])
            next_link = [link for link in links if link["rel"] == "next"]
            endpoint = next_link[0]["url"] if next_link else None
        else:
            raise ValueError(f"Error {response.status_code}: {response.text}")
    
    with open(filename, 'w') as file:
        json.dump(quizzes, file)

    return quizzes

def get_assignment_submissions(assignment_id, course_id=course_id, force_download=False, skip_download=False):
    """
        Uses the assignments/.../submissions endpoint to get the submission for each student **AT THE ASSIGNMENT LEVEL**
        This is to get at grades, not actual student submissions. Use get_submissions to use the quizzes/.../submissions endpoint
    """

    filename = f"data/{assignment_id}_submissions.json"
    data_folder_exists = os.path.isdir("data")

    if data_folder_exists: 
        if os.path.exists(filename) and not force_download:
            file_mod_time = os.path.getmtime(filename)
            if (time.time() - file_mod_time < 3600) or skip_download:  # 3600 seconds = 1 hour
                with open(filename, 'r') as file:
                    assignment_submissions = json.load(file)
                return assignment_submissions
    else:
        os.makedirs("data")

    endpoint = f"{BASE_URL}/courses/{course_id}/assignments/{assignment_id}/submissions"
    submissions = []

    while endpoint:
        response = requests.get(endpoint, headers=HEADERS)

        if response.status_code == 200:
            submissions.extend(response.json())

            # Check for pagination 'next' link
            links = requests.utils.parse_header_links(response.headers['Link'])
            next_link = [link for link in links if link["rel"] == "next"]
            endpoint = next_link[0]["url"] if next_link else None
        else:
            raise ValueError(f"Error {response.status_code}: {response.text}")


    if data_folder_exists:
        with open(filename, 'w') as file:
            json.dump(submissions, file)

    return submissions

def get_submissions(quiz_id, course_id=course_id):
    """
        Uses the submissions endpoint to get the ***LATEST*** submission for each student for the given quiz
        Don't use this function to get all submissions. use get_all_submissions instead
    """

    endpoint = f"{BASE_URL}/courses/{course_id}/quizzes/{quiz_id}/submissions"
    submissions = []

    while endpoint:
        response = requests.get(endpoint, headers=HEADERS)

        if response.status_code == 200:
            submissions.extend(response.json()['quiz_submissions'])

            # Check for pagination 'next' link
            links = requests.utils.parse_header_links(response.headers['Link'])
            next_link = [link for link in links if link["rel"] == "next"]
            endpoint = next_link[0]["url"] if next_link else None
        else:
            raise ValueError(f"Error {response.status_code}: {response.text}")

    return submissions

def get_all_submissions(quiz_id, course_id=course_id, force_download=False, skip_download=False):

    filename = f"data/{quiz_id}_submissions.json"
    data_folder_exists = os.path.isdir("data")

    # Check if the file exists and is updated within the last hour, if so: no new API call. just return the local data
    dp_submission_ids=set()
    all_submissions=[]
    if data_folder_exists: 
        if os.path.exists(filename):
            with open(filename, 'r') as file:
                all_submissions = json.load(file)
            if not force_download:
                file_mod_time = os.path.getmtime(filename)
                if (time.time() - file_mod_time < 3600) or skip_download:  # 3600 seconds = 1 hour
                    return all_submissions
            for s in all_submissions:
                dp_submission_ids.add(s['dp_submission_id'])
    else:
        os.makedirs("data")

    latest_submissions = get_submissions(quiz_id)

    for entry in latest_submissions:
        sub_id = entry['id']
        sub_attempt = entry['attempt']

        if not entry['workflow_state']=='complete':
            if sub_attempt == 1: #student has no completed attempts
                continue
            elif sub_attempt is None:
                continue
            else:
                sub_attempt -= 1 #exclude the current sub
        
        attempt_range = list(range(1,sub_attempt+1))
        for attempt in attempt_range:
            dp_submission_id = f'{sub_id}_{attempt}'
            if dp_submission_id not in dp_submission_ids:

                params = {'quiz_submission_id':sub_id,'quiz_submission_attempt':attempt} 
                endpoint = f'{BASE_URL}/courses/{course_id}/quizzes/{quiz_id}/questions'
                all_questions = []
                while endpoint:
                    response = requests.get(endpoint, headers=HEADERS, params=params)

                    if response.status_code == 200:
                        all_questions.extend(response.json())
                        links = requests.utils.parse_header_links(response.headers['Link'])
                        next_link = [link for link in links if link["rel"] == "next"]
                        endpoint = next_link[0]["url"] if next_link else None
                    else:
                        raise ValueError(f"Error {response.status_code}: {response.text}")

                # Process the collected questions
                sub = {
                    'dp_submission_id': dp_submission_id,
                    'attempt': attempt,
                    'quiz_submission_questions': all_questions,
                    'user_id': entry['user_id']
                }
                all_submissions.append(sub)

    # Save the data to a file only if the data folder exists
    if data_folder_exists:
        with open(filename, 'w') as file:
            json.dump(all_submissions, file)

    return all_submissions

def get_student_report(quiz_id,course_id=course_id,quiet=False, force_download=False, skip_download=False):
    
    report_filename = f"data/{quiz_id}_StudentReport.csv"
    data_folder_exists = os.path.isdir("data")

    # Check if the report file exists and is updated within the last hour
    if data_folder_exists and os.path.exists(report_filename) and not force_download:
        file_mod_time = os.path.getmtime(report_filename)
        if (time.time() - file_mod_time < 3600) or skip_download:  # 3600 seconds = 1 hour
            if not quiet:
                print(f"Using existing report file: {report_filename}")
            return report_filename
    
    params = {
        "quiz_report[report_type]":"student_analysis",
        "include":["file"],
        "quiz_report[includes_all_versions]":"true"
    }

    response = requests.post(f"{BASE_URL}/courses/{course_id}/quizzes/{quiz_id}/reports", params=params, headers=HEADERS)

    if response.status_code == 200:
        data = response.json()
        if data['report_type'] == 'student_analysis':
            progress_url = data['progress_url']
            report_id = data['id']
        # with open('data/Quiz_Report.json', 'w') as json_file:
        #     json.dump(data, json_file, indent=4)
    else:
        raise ValueError(f"Error {response.status_code} while attempting to generate student report: {response.text}")

    while True:
        progress_response = requests.get(progress_url, headers=HEADERS)
        if progress_response.status_code == 200:
            progress = progress_response.json()
            status = progress['completion']
            if status==100:
                response = requests.get(f"{BASE_URL}/courses/{course_id}/quizzes/{quiz_id}/reports/{report_id}", params=params, headers=HEADERS)
                data = response.json()
                if 'file' in data and 'url' in data['file']:
                    download_url = data['file']['url']
                else:
                    # Handle the case where the keys are missing
                    raise KeyError("No download url found when generating student report")
                break
            else:
                if not quiet:
                    print(f'Report generation {status} % complete')
                time.sleep(0.2) 
        else:
            raise ValueError(f"Error {progress_response.status_code}: {progress_response.text}")

    response = requests.get(download_url, stream=True, headers=HEADERS)

    # Check if the request was successful
    if response.status_code == 200:

        # Save the content to the local file
        with open(report_filename, 'wb') as file:
            for chunk in response.iter_content(chunk_size=8192):
                file.write(chunk)
        if not quiet:
            print(f'File saved to {report_filename}.')
    else:
        raise ValueError(f"Failed to download the file. Status code: {response.status_code}")
    
    return report_filename

def get_submission_questions(submission_id, quiz_id=None):
    sub_qs = None  # Initialize the variable to store the questions

    if quiz_id is not None:
        quiz_folder = f"data/{quiz_id}"
        file_path = os.path.join(quiz_folder, f"{submission_id}.json")

        # Check if the folder exists, if not, create it
        if not os.path.isdir(quiz_folder):
            os.makedirs(quiz_folder)

        # Check if the file exists
        if os.path.exists(file_path):
            with open(file_path, 'r') as file:
                sub_qs = json.load(file)
        else:
            # If the file doesn't exist, make the API call
            try:
                response = requests.get(f"{BASE_URL}/quiz_submissions/{submission_id}/questions", headers=HEADERS)
                if response.status_code == 200:
                    rjson = response.json()
                    sub_qs = rjson.get('quiz_submission_questions', [])
                    # Save the response to a file
                    with open(file_path, 'w') as file:
                        json.dump(sub_qs, file, indent=4)
                else:
                    raise ValueError(f"Error {response.status_code}: {response.text}")
            except requests.RequestException as e:
                raise ConnectionError(f"Request failed: {e}")

    return sub_qs
    
def get_question_group_info(quiz_id,group_id,course_id=course_id):
    
    filename = f"data/{quiz_id}_qgroup_info.json"
    
    if not os.path.isdir("data"):
        os.makedirs("data")

    if os.path.exists(filename):
        with open(filename, 'r') as file:
            cache = json.load(file)
        # Check if the group_id exists in the cache and is fresh
        if group_id in cache and (time.time() - cache[group_id]["cache_time"] < 24*3600):  # 1 day
            return cache[group_id]["data"]
    
    # If the data is not in the cache or is outdated, fetch from the API
    response = requests.get(f"{BASE_URL}/courses/{course_id}/quizzes/{quiz_id}/groups/{group_id}", headers=HEADERS)
    if response.status_code == 200:
        data = response.json()
        # Update the cache with the new data
        if os.path.exists(filename):
            with open(filename, 'r') as file:
                cache = json.load(file)
        else:
            cache = {}
        cache[group_id] = {"data": data, "cache_time": time.time()}
        with open(filename, 'w') as file:
            json.dump(cache, file)
        return data
    else:
        raise ValueError(f"Error {response.status_code}: {response.text}")
    
def search_for_assignment(searchstr = None, autoselect_best=True):
    # returns assignment id
    
    assignments_json= get_assignments()

    assignments_dict = {assignment['name']: assignment['id'] for assignment in assignments_json}

    if searchstr is None:
        searchstr = input("Enter the name of the assignment you are looking for: ")
    
    matches = custom_match(searchstr, assignments_dict.keys())

    if autoselect_best:
        match_choice = 1
    else:
        print("Top matches:")
        for i, (name, score) in enumerate(matches, start=1):
            print(f"{i}. {name} (Score: {score})")
        match_choice = int(input("Enter the number of the correct assignment: "))

    # Validate user input
    if 1 <= match_choice <= len(matches):
        selected_name = matches[match_choice - 1][0]
        assignment_id = assignments_dict[selected_name]
        print(f"You selected: {selected_name} with ID {assignment_id}")
        return assignment_id
    else:
        print(f"Invalid selection: {match_choice}")
        return search_for_assignment(searchstr, autoselect_best=False) #recursively try again
    
def search_for_quiz(searchstr = None, autoselect_best=True, force_download=False, skip_download=False):
    # returns assignment id
    
    quizzes_json= get_quizzes(force_download=force_download, skip_download=skip_download)

    quiz_dict = {quiz['title']: quiz['id'] for quiz in quizzes_json}

    if searchstr is None:
        searchstr = input("Enter the name of the quiz you are looking for: ")
    
    matches = custom_match(searchstr, quiz_dict.keys())

    
    if autoselect_best:
        match_choice = 1
    else:
        print("Top matches:")
        for i, (name, score) in enumerate(matches, start=1):
            print(f"{i}. {name} (Score: {score})")
        match_choice = int(input("Enter the number of the correct quiz: "))

    # Validate user input
    if 1 <= match_choice <= len(matches):
        selected_name = matches[match_choice - 1][0]
        assignment_id = quiz_dict[selected_name]
        print(f"You selected: {selected_name} with ID {assignment_id}")
        return assignment_id
    else:
        print(f"Invalid selection: {match_choice}")
        return search_for_quiz(searchstr, autoselect_best=False) #recursively try again
    
def get_quiz(quiz_id,course_id=course_id, force_download=False, skip_download=False):
    #returns a quiz object
    
    filename = f"data/{quiz_id}.json"
    data_folder_exists = os.path.isdir("data")

    if data_folder_exists: 
        if os.path.exists(filename) and not force_download:
            file_mod_time = os.path.getmtime(filename)
            if (time.time() - file_mod_time < 3600) or skip_download:  # 3600 seconds = 1 hour
                with open(filename, 'r') as file:
                    quiz = json.load(file)
                return quiz
    
    response = requests.get(f"{BASE_URL}/courses/{course_id}/quizzes/{quiz_id}", headers=HEADERS)
    if response.status_code != 200:
        raise ValueError(f"Error {response.status_code}: {response.text}")
    quiz = response.json()
    if data_folder_exists:
        with open(filename, 'w') as file:
            json.dump(quiz, file)
    return quiz
    
def get_assignment(assignment_id,course_id=course_id, force_download=False, skip_download=False):
    #returns an assignment object
    
    filename = f"data/{assignment_id}.json"
    data_folder_exists = os.path.isdir("data")

    if data_folder_exists: 
        if os.path.exists(filename) and not force_download:
            file_mod_time = os.path.getmtime(filename)
            if (time.time() - file_mod_time < 3600) or skip_download:  # 3600 seconds = 1 hour
                with open(filename, 'r') as file:
                    assignment = json.load(file)
                return assignment
    
    response = requests.get(f"{BASE_URL}/courses/{course_id}/assignments/{assignment_id}", headers=HEADERS)
    if response.status_code != 200:
        raise ValueError(f"Error {response.status_code}: {response.text}")
    
    assignment = response.json()

    if data_folder_exists:
        with open(filename, 'w') as file:
            json.dump(assignment, file)

    return assignment

def initiate_gradebook_export(course_id=course_id):
    endpoint = f"{BASE_URL}/courses/{course_id}/gradebook_export"
    response = requests.post(endpoint, headers=HEADERS)
    if response.status_code == 200:
        return response.json().get('progress_url')
    else:
        print(f"Failed to initiate gradebook export. Status Code: {response.status_code}")
        return None

def get_gradebook(course_id=course_id):
    export_url = initiate_gradebook_export(course_id)
    while True:
        response = requests.get(export_url, headers=HEADERS)
        if response.status_code == 200 and response.json().get('workflow_state') == 'completed':
            download_url = response.json().get('attachment', {}).get('url')
            if download_url:
                gradebook = requests.get(download_url)
                with open('canvas_gradebook.csv', 'wb') as file:
                    file.write(gradebook.content)
                print("Gradebook downloaded successfully.")
                break
        else:
            print("Waiting for gradebook export to be ready...")
            time.sleep(2)  # Wait for a few seconds before checking again



def custom_match(search_str, choices, weight_number=0.7, weight_text=0.3):
    """
    Custom matching function that places more weight on numerical parts of the strings.
    
    :param search_str: The string to search for.
    :param choices: A list of strings to search against.
    :param weight_number: The weight to place on matching numbers. Default is 0.7.
    :param weight_text: The weight to place on the rest of the text. Default is 0.3.
    :return: A list of tuples with the match and its score, sorted by score.
    """
    search_numbers = [int(num) for num in re.findall(r'\d+', search_str)]
    results = []

    for choice in choices:
        choice_numbers = [int(num) for num in re.findall(r'\d+', choice)]
        number_score = 1 if search_numbers == choice_numbers else 0
        text_score = SequenceMatcher(None, search_str, choice).ratio() 

        # Calculate final score with weighted sum of number and text similarities
        final_score = (weight_number * number_score) + (weight_text * text_score)
        results.append((choice, final_score))

    # Sort the results based on the score in descending order
    return sorted(results, key=lambda x: x[1], reverse=True)