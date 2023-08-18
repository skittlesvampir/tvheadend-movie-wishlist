#!/usr/bin/python3
import requests
import json
# this script follows the steps described under: https://developer.themoviedb.org/reference/authentication-how-do-i-generate-a-session-id

# step 1, see:
# https://developer.themoviedb.org/reference/authentication-create-request-token
api_key = str(input("Please enter your TMDB API Read Access Token: "))
url = "https://api.themoviedb.org/3/authentication/token/new"

headers = {
    "accept": "application/json",
    "Authorization": f"Bearer {api_key}",
}

request_token = requests.get(url, headers=headers).text
request_token = json.loads(request_token)["request_token"]

# step 2
print()
print(f"Please open the following link in a web browser:\nhttps://www.themoviedb.org/authenticate/{request_token}")
input("Press enter to continue...")

# step 3
url = "https://api.themoviedb.org/3/authentication/session/new"
params = {
    "api_key": api_key,
    "request_token": request_token    
}

user_session_id = requests.get(url, params=params, headers=headers).text
user_session_id = json.loads(user_session_id)["session_id"]
print()
print("Your TMDB User Session ID is:")
print(user_session_id)
print()
print("You can revoked this ID under https://www.themoviedb.org/settings/sessions/api")