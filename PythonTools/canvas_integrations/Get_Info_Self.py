import requests

BASE_URL = "https://weber.instructure.com/api/v1"
with open("config.txt", "r") as file:
    API_TOKEN = file.readline().strip()

HEADERS = {
    "Authorization": f"Bearer {API_TOKEN}"
}

# Endpoint for fetching current user's details
endpoint = f"{BASE_URL}/users/self"

# Make the request
response = requests.get(endpoint, headers=HEADERS)
if response.status_code == 200:
    user_data = response.json()
    user_id = user_data.get("id")
    print(f"Your Canvas user ID is: {user_id}")
else:
    print(f"Failed to fetch user data: {response.status_code}, {response.text}")
