#!/usr/bin/python3
import requests
import json
import re
import unicodedata
import warnings

import tomli

from ntfy import send_notification

# This function is used to efficiently (faster than fuzzy matching)
# compare EPG movie name and TMDB movie names
# 
# This function is not perfect but everytime I see a movie name that could
# fail, I will update this function
#
# There are testcases (unit_tests.py) for this function to ensure it's working properly
# as it's the most important function in the whole codebase
def normalize_title(title):
    title = title.strip()
    title = title.lower()
    title = title.replace("&", "und")
    umlaut_replacers = {'ä': 'ae', 'ö': 'oe', 'ü': 'ue', 'ß': 'ss'}
    for before, after in umlaut_replacers.items():
        title = title.replace(before, after)
    title = title.replace(u"½", " 1/2")    # Fractions are nearly impossible to get right. I just used
    title = title.replace(u"⅓", " 1/3")    # 'The Naked Gun' movies and TMS api as a reference
    title = title.replace('()', 'o')
    nfkd_form = unicodedata.normalize('NFKD', title)
    title = u"".join([c for c in nfkd_form if not unicodedata.combining(c)])
    title = re.sub(r'\(\d{4}\)', '', title)
    title = re.sub(r'[/!@#$%^&*:\-—\'.,?]', '', title)
    title = " ".join(title.split())
    
    return title

def retrieve_tmdb_list():
    with open("config.toml", "rb") as f:
        toml_dict = tomli.load(f)

    api_bearer_token = toml_dict["themoviedb"]["api_read_access_token"]
    user_session_id = toml_dict["themoviedb"]["user_session_id"]
    list_id = toml_dict["themoviedb"]["list_id"]
    language_code = toml_dict["language"]
    
    headers = {
        "accept": "application/json",
        "Authorization": f"Bearer {api_bearer_token}",
    }
    
    response = requests.get(f"https://api.themoviedb.org/4/list/{list_id}?language={language_code}", headers=headers)
    if response.status_code != 200:
        send_notification("Could not query TheMovieDB: " + response.text,error=True)
        raise ConnectionError("Could not query TheMovieDB: " + response.text)
    
    movie_list_complete = []

    num_pages = json.loads(response.text)["total_pages"]
    for page in range(1, num_pages+1):
        response = requests.get(f"https://api.themoviedb.org/4/list/{list_id}?page={page}&language={language_code}", headers=headers)
        if response.status_code != 200:
            send_notification("Could not query TheMovieDB: " + response.text,error=True)
            raise ConnectionError("Could not query TheMovieDB: " + response.text)
        
        movie_list_page = response.text
        movie_list_page = json.loads(movie_list_page)["results"]
        movie_list_page = remove_non_movies_tmdb(movie_list_page)
        
        movie_list_complete.extend(movie_list_page)

    for i, _ in enumerate(movie_list_complete):
        movie_list_complete[i]["normalized_title"] = normalize_title(movie_list_complete[i]["title"])
        print(movie_list_complete[i]["title"])

    # Both scenarios are perfectly fine but they are indicators for
    # something going wrong and I really don't want something to
    # go wrong
    if len(movie_list_complete) <= 0: 
        send_notification("There are no movies in the list",warning=True)
        warnings.warn("There are no movies in the list")
    elif len(movie_list_complete) <= 1:
        send_notification("There's only one movie in the list",warning=True)
        warnings.warn("There's only one movie in the list")
        
    return movie_list_complete

# This script only searches for movies
def remove_non_movies_tvheadend(epg_list):
    sanitized_epg_list = []
    for programm in epg_list:
        if "seasonNumber" in programm:
            continue
        sanitized_epg_list.append(programm)
    return sanitized_epg_list

def remove_non_movies_tmdb(tmdb_list):
    sanitized_tmdb_list = []
    for media in tmdb_list:
        if "media_type" in media:
            if media["media_type"] != "movie":
                continue
        sanitized_tmdb_list.append(media)
    return sanitized_tmdb_list

def get_config_path():
    return os.path.join(Path(__file__).parent, 'config.toml')
