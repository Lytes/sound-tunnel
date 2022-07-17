import sys
import re
import spotipy
from src.mainfuncs import message, what_to_move, compare
from math import ceil
from time import sleep
from config.config import CLIENT_SECRET, CLIENT_ID, REDIRECT_URI, SCOPE

def spotify_auth():
# Attempt to authenticate Spotify
   try:
      spotify = spotipy.Spotify(auth_manager=spotipy.oauth2.SpotifyOAuth(client_id=CLIENT_ID, client_secret=CLIENT_SECRET, redirect_uri=REDIRECT_URI, scope=SCOPE))
      message("s+","Successfully Authenticated")
      return spotify
   except Exception:
      message("s+","Authentication failed")
      sys.exit(0)
   # had to add print(auth_url) to line 435 of /usr/local/lib/python3.10/dist-packages/spotipy/oauth2.py so that the script would print the link
   # why? because wsl2 sucks
   
def get_spotify_playlists(spotify):
   # Gets user spotify playlists
   user_playlists = spotify.current_user_playlists()
   spfy_lists = {}
   try:
      for i in user_playlists['items']:
         playlist_name = i['name']
         playlist_id = i['id']
         # Add playlist name and ids to dictionary
         spfy_lists[playlist_name] = playlist_id
   except:
      # Triggered for non-songs
      pass
   return spfy_lists

def get_spfy_likes(spotify):
   # Gets track on spotify liked list
   test_likes = spotify.current_user_saved_tracks(limit=50)
   no_of_liked_songs = test_likes['total']
   total_requests = ceil(no_of_liked_songs/50)
   result = []
   for i in range(total_requests):
      like = spotify.current_user_saved_tracks(limit=50, offset=50*i)
      for song in like['items']:
         song_name = song['track']['name']
         album_name = song['track']['album']['name']
         artist_name = []
         for i in song['track']['artists']:
            artist = i['name']
            artist_name.append(artist)
         artist = ' '.join(artist_name)
         result.append(album_name+"&@#72"+song_name+"&@#72"+artist)
   return result

def get_spfy_playlist_content(spotify, source_id):
   # Gets track on spotify playlist
   playlist_content = spotify.playlist_items('spotify:playlist:{}'.format(source_id))
   result = []
   for song in playlist_content['items']:
      song_name = song['track']['name']
      album_name = song['track']['album']['name']
      artist_name = []
      for i in song['track']['artists']:
         artist = i['name']
         artist_name.append(artist)
      artist = ' '.join(artist_name)
      result.append(album_name+"&@#72"+song_name+"&@#72"+artist)
   return result

def spfy_dest_check(spfy_lists, spotify, spfy_id, dest_playlist_name):
   if dest_playlist_name in spfy_lists:
      dest_playlist_id = spfy_lists[dest_playlist_name]
      message("s+","Playlist exists, adding missing songs")
   else:
      create_playlist = spotify.user_playlist_create(spfy_id, dest_playlist_name, public=False, collaborative=False, description='Sound Tunnel Playlist')
      dest_playlist_id = create_playlist['id']
      message("s+","Playlist created")
   return dest_playlist_id

def move_to_spfy(spotify, playlist_info, dest_id):
   not_found = []
   present_song = get_spfy_playlist_content(spotify, dest_id)
   playlist_info = what_to_move(present_song, playlist_info)
   try:
      for i in playlist_info:
         i = i.replace("&@#72", " ")
         try:
            search = spotify.search(i, limit=5, type="track")
         except:
            bk = i
            i = re.sub("\(.*?\)","",i)
            try:
               search = spotify.search(i, limit=5, type="track")
            except:
               not_found.append(bk)
               continue
         for song in search['tracks']['items']:
            album_name = song['album']['name']
            song_name = song['name']
            artist_name = []
            for j in song['artists']:
               artist = j['name']
               artist_name.append(artist)
            artist = ' '.join(artist_name)
            found = album_name+" "+song_name+" "+artist
            songid = [song['id']]
            if compare(found, i):
               sleep(0.5)
               spotify.playlist_add_items(dest_id, songid)
               break
         else:
            not_found.append(i)
      return not_found
   except:
      return not_found