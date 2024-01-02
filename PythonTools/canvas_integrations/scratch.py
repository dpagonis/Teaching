import json

# Load the JSON data from a file
with open("Assignment_Submissions.json", "r") as file:
    data = json.load(file)

# Target assignment_id and user_id
# TARGET_ASSIGNMENT_ID = 5908046
# TARGET_USER_ID = 1901229

user_ids = []

# Iterate over the JSON data to find matching entries
for entry in data["assignment_submissions"]:
    if 'user_id' in entry:
        user_ids.append(entry['user_id'])
        print(entry["id"],entry["graded_at"])

# sorted_list = sorted(user_ids)

# for id in sorted_list:
#     print(id)