# tvheadend-movie-wishlist
*tvheadend-movie-wishlist* is a program that automatically records movies from a [TheMovieDB.org](https://themoviedb.org) list to your TVHeadend server.
It does this by pulling all the desired movies from TMDB and comparing it against your TVHeadend EPG. If it finds a match, it automatically schedules a recording and sends you a notification using [ntfy](https://ntfy.sh).

## Important information
TheMovieDB applied some (currently undocumented) changes to their API, which cause this script to only retrieve the first 20 entries from the list, which can have some pretty inconvenient consequences. This script has been updated to account for these changes, please make sure to pull the lastet version from GitHub.

## Setting it up

First of all, download the code for this project:
`git clone https://github.com/skittlesvampir/tvheadend-movie-wishlist`

Then copy `default_config.toml` to `config.toml`.

### Preparing TVHeadend

*tvheadend-movie-wishlist* requires all channels that could potentially air an interesting movie to be mapped.

1. Go to *Configuration > DVB Inputs > Services*
2. In the bottom right corner, make sure 'Per Page' is set to 'All'
3. Ctrl-Click all channels that could show a movie.
4. When done, click *Map Selected > Map Selected Services*
5. Wait until all services are mapped.

In order for the mapped channels to be useful, you need a good EPG provider. Theorically, any EPG should do the trick, but this program is optimized for Gracenote/TMS EPG data. A good EPG program that does this is [New EasyEPG](https://github.com/sunsettrack4/script.service.easyepg-lite#easyepg-lite) [(Docker)](https://github.com/DeBaschdi/docker.new-easyepg).

1. Install one of the mentioned programs.
2. When promted for a Gracenote/TMS API key, use this one: n829qtk58c7ym5pxdch5smup
3. In the EasyEPG web interface click '+', then 'TMS'.
4. Search for a TV channel.
5. Select the result that matches your channels the most.
6. Repeat 4. and 5. until you've added every channel that you also have in TVHeadend.
7. Click the cloud symbol, then 'Start'.
8. Once finished, select 'XML file' and click 'Copy link'.
9. Install [tv_grab_file](https://github.com/b-jesch/tv_grab_file).
10. Setup up as descript in the README, use the copied link as filename.
11. Re-run Interal EPG Grabbers
12. Go to *Configuration > Channel/EPG > Channels*.
13. In the column 'EPG Source' select the matching EPG source.
14. Click 'Save' when done for all channels.

Great, now you have prorper EPG. Next you need to enable DIGEST auth:
1. Go to *Configuration > General > Base*.
2. Set Authentication type to either 'Digest' or 'Both Plain and Digest'.

Almost done, now you only need a DVR profile:
1. Go to *Configuration > Recording > Digital Video Recorder Profiles*.
2. Create a new profile if you want or just remember the name of your default profile.

Open `config.toml` and edit the TVHeadend so it matches your server.

### Preparing TheMovieDB
In order for this script to work, you need a list:
1. Go to [TheMovieDB.org](https://www.themoviedb.org) and create an account.
2. Click on your profile icon, then 'Lists' and create a new list.
3. Add all your favourite movies to the list, these are the ones that will be recorded automatically.
4. Copy the id of your list from the URL and paste in your `config.toml`.

Well done, now you need to enable API access:
1. Visit [the API section](https://www.themoviedb.org/settings/api)
2. Create an API key, use 'tvheadend-movie-wishlist' as application name.
3. Copy the 'API Read Access Token' into the `config.toml`.

Lastly, you need a User Session ID. This is a bit complicated but don't worry, I wrote I script to make this step easier:
1. In the repository go to 'wishlist/tools'.
2. Execute `generate_user_session_id.py` and follow the instructions.
3. If you did everything correctly, you should receive a User Session ID, copy into `config.toml`.

### Setting up ntfy (optional)
I find it convenient to be notified when a movie was scheduled. I've decided on using [ntfy](https://ntfy.sh) because it works well and can be selfhosted. Adding ntfy to tvheadend-movie-wishlist is pretty straight forward, just fill in the necessary values in `config.toml`.

## Running the program
Once everything is setup, execute 'wishlist/main.py'. I would recommend to add a movie to your wishlist where you know it will soon be on TV, to verify everything works.

I've prepared a systemD timer for automatic execution, just edit them to match the location of the repo, copy them to '~/.config/systemd/user/' and do `systemctl --user enable --now tvheadend-movie-wishlist.timer`.

## Reliabilty
Reliability was a big concern when designining this program. Most movies aren't show very often, so missing one would be devastating. Assuming TVHeadend is set up correctly, the main weakness of this program is matching movies from TMDB with movies from your EPG. For this I've written a 'normalizer' function that tries to convert movie titles to something that will most likely match with each other. I've written several unit tests to make sure this function works correctly and I'm updating it everytime I encounter a movie that might not match.

If you want to make sure, that a movie will get matched properly, use the script 'wishlist/tools/check_movie_title.py' which matches TMDB movies with Gracenote movie titles. If this script reports a mismatch, please file an issue so I can fix it.

## Multiple streams simultaneously
I only have one single tuner, so this script assumes that you can't record different channels at the same time. However, if the channels are on the same frequency (mux/transponder), then you can still stream them at the same time, even with only one tuner available.

To test this, I recommend going into your TVHeadend settings under "Configuration" > "DVB Inputs" > "Services" and looking for channels with the same "Mux". Play two or more at the same time. If all can be played back in parallel, your tuner supports it and you can set `mux_multiple_channels` to `true` in your `config.toml`.

Note that the channels that share a frequency are usually from the same network, so it's unlikely that e.g. Prosieben would be on same frequency as the Disney Channel.

![Ten simultaneous streams](https://raw.githubusercontent.com/skittlesvampir/tvheadend-movie-wishlist/main/10%20Recordings%20on%20the%20Same%20Mux%20using%20Only%20One%20Tuner.png "Ten simultaneous streams")
*Ten simultaneous streams on the same tuner*

## Support
If you have problems setting this program up, don't hesitate to file an issue.
