#!/usr/bin/python3
import requests
import json

import tomli

import sys
sys.path.append('wishlist')
from util import normalize_title

with open("config.toml", "rb") as f:
    toml_dict = tomli.load(f)
    

TMS_API_KEY = 'n829qtk58c7ym5pxdch5smup' # source: https://twitter.com/DailyNickNews/status/1405291520962437122

movie_title_input = str(input("Enter movie title: "))
normalized_title_input = normalize_title(movie_title_input)

lang = toml_dict["language"].split('-')[0]
data = {
    "q": movie_title_input,
    "includeAdult": True,
    "queryFields": "title",
    "entityType": "movie",
    "titleLang": lang,
    "api_key": TMS_API_KEY,
}
response = requests.get("http://data.tmsapi.com/v1.1/programs/search", params=data)
if response.status_code != 200:
    raise ConnectionError(f"Could error from TMS api (code {response.status_code}): {response.text}")

hits = json.loads(response.text)["hits"]
if len(hits) <= 0:
    print("No results")
    
for i, _ in enumerate(hits):
    if i >= 10:
        break
    title = hits[i]["program"]["title"]
    print(f"{i}: {title}")

print()
number = int(input("Enter title number: "))

movie_title_tms = hits[number]["program"]["title"]
normalized_title_tms = normalize_title(movie_title_tms)

if normalized_title_input == normalized_title_tms:
    print("Inputted title and Gracenote title seem compatible, your recording will most likely work :)")
else:
    print("Titles aren't compatible! :(")
    print()
    print("Inputted title:", movie_title_input)
    print("Inputted title (normalized):", normalized_title_input)
    print("Gracenote title:", movie_title_tms)
    print("Gracenote title (normalized):", normalized_title_tms)
    print()
    print("It's highly likely that an automated recording for this movie will FAIL!")
    print("This is a BUG and should be reported immediately to https://github.com/skittlesvampir/tvheadend-movie-wishlist")