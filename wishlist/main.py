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
    ignored_events_file_handle = open(ignored_events_filename, "w+")
    ignored_events = [x.strip() for x in ignored_events_file_handle.readlines()]

    for movie in tmdb_movie_list:
        movie_norm = movie["normalized_title"]
        movie_pretty = movie["title"]
        for programming in ts_movie_list:
            if movie_norm == programming["normalized_title"]:
                if "dvrState" in programming: # dvrState only exists if programming was/is scheduled
                    print(f'"{movie_pretty}" is already scheduled')
                    break
                else:
                    success, extra_start, extra_stop = schedule_recording(programming)
                    if success:
                        image = None
                        if 'image' in programming:
                            image = get_image_url(programming['image'])

                        date = datetime.fromtimestamp(programming["start"]).strftime("%d.%m.%Y %H:%M")
                        send_notification(f"Scheduled movie {movie_pretty} on the {date} with {extra_start} minutes before and {extra_stop} minutes after.",image_url=image)
                        break
                    else:
                        event_identity = '%s %s %s %s' % (
                                programming["eventId"],
                                programming["channelUuid"],
                                programming["start"],
                                programming["stop"]
                            )
                        if event_identity not in ignored_events:
                            send_notification(f"Couldn't schedule {movie_pretty} because other recordings already exist") # send notification once and only once
                            ignored_events.append(event_identity)
                            ignored_events_file_handle.write('\n'.join(ignored_events))

    ignored_events_file_handle.close()
