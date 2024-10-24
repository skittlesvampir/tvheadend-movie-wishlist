#!/usr/bin/python3
import os
from pathlib import Path
from datetime import datetime

from ntfy import send_notification
from tvheadend import schedule_recording, ts_make_request
from tvheadend import ts_retrieve_movie_list, get_image_url
from util import retrieve_tmdb_list

if __name__ == '__main__':
    tmdb_movie_list = retrieve_tmdb_list()
    
    ts_movie_list = ts_retrieve_movie_list()
    
    # the user has already been notified about the inavailability of these events
    current_working_dir = Path(__file__).parent.absolute()
    ignored_events_filename = os.path.join(current_working_dir, '.ignored_events')

    if not os.path.exists(ignored_events_filename):
        os.mknod(ignored_events_filename)
    else:
        with open(ignored_events_filename) as file:
            ignored_events = [line.rstrip() for line in file]

    ignored_events_file_handle = open(ignored_events_filename, "w")
    ignored_events = []
    
    for movie in tmdb_movie_list:
        movie_norm = movie["normalized_title"]
        
        movie_pretty = movie["title"]
        programmings = []
        already_scheduled = False
        for ts_programming in ts_movie_list:
            if movie_norm == ts_programming["normalized_title"]:
                programmings.append(ts_programming)

                if "dvrState" in ts_programming: # dvrState only exists if programming was/is scheduled
                    print(f'"{movie_pretty}" is already scheduled')
                    already_scheduled = True
                    break
                    
        successfully_scheduled = False
        if len(programmings) >= 1 and not already_scheduled:
            for programming in programmings:
                success, extra_start, extra_stop = schedule_recording(programming)
                if success:
                    image = None
                    if 'image' in programming:
                        image = get_image_url(programming['image'])

                    date = datetime.fromtimestamp(programming["start"]).strftime("%d.%m.%Y %H:%M")
                    channelName = programming["channelName"]
                    send_notification(f"Name: {movie_pretty}\nDate: {date}\nPadding: {extra_start} minutes before and {extra_stop} minutes after\nChannel: {channelName}",image_url=image)
                    successfully_scheduled = True
                    break # don't check the other slots, as one is enough
                        
                event_identity = '%s %s %s %s' % (
                   programming["eventId"],
                   programming["channelUuid"],
                   programming["start"],
                   programming["stop"]
                )

                if not successfully_scheduled and event_identity not in ignored_events:
                    send_notification(f"Couldn't schedule {movie_pretty} because other recordings already exist") # send notification once and only once
                    ignored_events.append(event_identity)

                            
    ignored_events_file_handle.write('\n'.join(ignored_events))
    ignored_events_file_handle.close()
