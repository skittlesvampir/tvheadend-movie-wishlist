#!/usr/bin/python3
import requests
import json
import tomli
from ntfy import send_notification
from util import normalize_title
from util import remove_non_movies_tvheadend

def ts_make_request(ts_url,ts_data=None,ts_method='GET'):
    with open("config.toml", "rb") as f:
        toml_dict = tomli.load(f)
        
    ts_server = toml_dict["tvheadend"]["server"]
    ts_user = toml_dict["tvheadend"]["username"]
    ts_pass = toml_dict["tvheadend"]["password"]
    ts_query = '%s/%s' % (
        ts_server,
        ts_url,
    )
    
    if ts_method == 'GET':
        ts_response = requests.get(ts_query, auth=requests.auth.HTTPDigestAuth(ts_user, ts_pass), data=ts_data)
    elif ts_method == 'POST':
        ts_response = requests.post(ts_query, auth=requests.auth.HTTPDigestAuth(ts_user, ts_pass), data=ts_data)
    else:
        raise KeyError(f'Method "{ts_method}" is not supported')
        return {}

    if ts_response.status_code != 200:
        send_notification(f'Could not connect to TVHeadend (Error {ts_response.status_code}): {ts_response.text}', error=True)
        raise ConnectionError('Could not connect to TVHeadend: ' + ts_response.text)
        return {}
    
    return ts_response

def get_timers():
    ts_response = ts_make_request('api/dvr/entry/grid_upcoming?sort=start&limit=1000',ts_method='GET')

    ts_json = json.loads(ts_response.text, strict=False)
    return ts_json['entries']

# Assuming there is only one tuner available
# Expand this section if there's the need
# for more tuners
#
# For (hopefully) more insight on the logic of this
# function, see 'post-it-note.jpeg'
def is_block_empty(start_time, end_time, channel_uuid):
    for timer in get_timers():
        if not (end_time < timer["start_real"] or start_time > timer["stop_real"]): # overlapping :(
            # tvheadend can record two schedules on one tuner if they're on the same channel
            # schedules that are disabled can be ignored
            if timer["channel"] != channel_uuid and timer["enabled"]: 
                return False
    return True

def get_dvr_config_uuid(name):
    ts_response = ts_make_request('api/dvr/config/grid',ts_method='GET')
    dvr_configs = json.loads(ts_response.text)

    for entry in dvr_configs["entries"]:
        if entry["name"] == name:
            return entry["uuid"]
    
    # Error
    raise KeyError(f'DVR config {name} not found')
    return 0

# start, stop time is stated in minutes
#
# This function is (after normalize_title) the function most likely to break
# because it uses internal data structures. I have reverse-engineered it
# from the webui. Although I will update it when necessary, I would appreciate
# a more robust solution for tweaking recording paddings.
def add_padding_and_year_to_recording(uuid, start, stop):
    data = {
        "uuid": uuid,
        "grid": 1,
        "list": "enabled,copyright_year,disp_title,disp_extratext,channel,start,start_extra,stop,stop_extra,pri,config_name,comment,episode_disp,owner,creator,retention,removal",
    }
    ts_response = ts_make_request('api/idnode/load',ts_data=data,ts_method='POST')
    idnode_before = json.loads(ts_response.text)["entries"][0]
    
    idnode_after = {
        "start_extra": start,
        "stop_extra": stop,
        "comment": "Created by tvheadend-movie-wishlist",
        "uuid": uuid,
        "enabled": True,

        "disp_title": idnode_before["disp_title"],
        "disp_extratext": idnode_before["disp_extratext"],
        "channel": idnode_before["channel"],
        "start": idnode_before["start"],
        "stop": idnode_before["stop"],
        "episode_disp": idnode_before["episode_disp"],
        "pri": idnode_before["pri"],
        "config_name": idnode_before["config_name"],
        "owner": idnode_before["owner"] if "owner" in idnode_before else "", # owners don't see to work for me
        "creator": idnode_before["creator"],
        "removal": idnode_before["removal"],
        "retention": idnode_before["retention"],
    }

    if "copyright_year" in idnode_before:
        if idnode_before["copyright_year"] >= 0:
            disp_title = idnode_after["disp_title"]
            year = idnode_before["copyright_year"]
            idnode_after["disp_title"] = f"{disp_title} ({year})"
    
    data = {
        "node": json.dumps(idnode_after),
    }
    
    ts_make_request('api/idnode/save',ts_data=data,ts_method='POST')
    return

def schedule_recording(programming):
    possible_paddings = [15,10,5,4,3,2,1]

    for padding in possible_paddings: # 20 to 5
        if is_block_empty(programming["start"] - padding*60, programming["stop"], programming["channelUuid"]):
            start = padding
            break
    else:
        return (False, 0, 0)

    for padding in possible_paddings:
        if is_block_empty(programming["start"], programming["stop"] + padding*60, programming["channelUuid"]):
            stop = padding
            break
    else:
        return (False, 0, 0)

    with open("config.toml", "rb") as f:
        toml_dict = tomli.load(f)
    name_of_config = toml_dict["tvheadend"]["config"]
    data = {
        "event_id": programming["eventId"],
        "config_uuid": get_dvr_config_uuid(name_of_config)
    }
    
    ts_response = ts_make_request('api/dvr/entry/create_by_event',ts_data=data,ts_method='POST')
    recording_uuid = ts_response.json()["uuid"]
    
    add_padding_and_year_to_recording(recording_uuid, start, stop)
    
    return (True, start, stop)
    
def ts_retrieve_movie_list():
    ts_response = ts_make_request('api/epg/events/grid?limit=30000',ts_method='GET').text

    ts_movie_list = json.loads(ts_response)["entries"]
    ts_movie_list = remove_non_movies_tvheadend(ts_movie_list)
    for i, _ in enumerate(ts_movie_list):
        ts_movie_list[i]["normalized_title"] = normalize_title(ts_movie_list[i]["title"])
    
    return ts_movie_list

def get_image_url(source):
    if "https://ondemo.tmsimg.com/assets" in source:
        return source.split("?")[0]
