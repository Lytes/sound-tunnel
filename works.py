"""
Spotify
"""

from spotipy.oauth2 import SpotifyOAuth
import spotipy
import config as cfg
spotify = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=cfg.CLIENT_ID, client_secret=cfg.CLIENT_SECRET, redirect_uri=cfg.REDIRECT_URI, scope=cfg.SCOPE))
# added print(auth_url) to line 435 of /usr/local/lib/python3.10/dist-packages/spotipy/oauth2.py so that the script would print the link
# Why? Because wsl2 can't open  sucks 
user_deet = spotify.me() #gets user details
user_playlists = spotify.current_user_playlists() #gets user playlists

for i in user_playlists['items']:
   playlist_name = i['name']
   playlist_id = i['id']
   playlist_content = spotify.playlist_items('spotify:playlist:{}'.format(playlist_id))

   for song in playlist_content['items']:
      song_name = song['track']['name']
      artist_name = []
      for i in song['track']['artists']:
         artist = i['name']
         artist_name.append(artist)




"""
Youtube music
"""

import ytmusicapi
