"""
Spotify to YT
@kuro_lytes
"""

import argparse
import time
from spotipy.oauth2 import SpotifyOAuth
import spotipy
import config as cfg
import sys
from os.path import abspath
from ytmusicapi import YTMusic
from math import ceil
from datetime import datetime
from difflib import SequenceMatcher
import json
import tidalapi
import requests

### Authenticate on Platforms
def spotify_auth():
# Attempt to authenticate Spotify
   try:
      spotify = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=cfg.CLIENT_ID, client_secret=cfg.CLIENT_SECRET, redirect_uri=cfg.REDIRECT_URI, scope=cfg.SCOPE))
      print("[+] Spotify: Successfully Authenticated")
      return spotify
   except Exception:
      print("[-] Spotify: Authentication failed")
      sys.exit(0)
   # had to add print(auth_url) to line 435 of /usr/local/lib/python3.10/dist-packages/spotipy/oauth2.py so that the script would print the link
   # why? because wsl2 sucks

def ytmusic_auth():
   # Attempt to authenticate Youtube music
   try:
      ytmusic = YTMusic(cfg.ytfile)
      print("[+] Youtube: Successfully Authenticated")
      return ytmusic
   except:
      print("[-] Youtube: Authentication failed")
      sys.exit(0)

def tidal_auth():
   # Attempt to authenticate Tidal
   try:
      tidal = tidalapi.Session()
      try:
         with open(cfg.tidalfile, 'r') as file:
            cred = [line.rstrip() for line in file]
         if datetime.strptime(cred[3], "%m/%d/%Y, %H:%M:%S") > datetime.now():
            # Nesting the if for better readability
            if tidal.load_oauth_session(cred[0], cred[1], cred[2]):
               print("[+] Tidal: Successfully Authenticated")
               return tidal
      except:
         pass
      tidal.login_oauth_simple()
      if tidal.check_login():
         print("[+] Tidal: Successfully Authenticated")
         creds = [tidal.session_id, tidal.token_type, tidal.access_token, tidal.expiry_time.strftime("%m/%d/%Y, %H:%M:%S")]
         with open(cfg.tidalfile, 'w') as file:
            file.write('\n'.join(creds))
         return tidal
      else:
         var_error_out
   except:
      print("[-] Tidal: Authentication failed")
      sys.exit(0)


### Get a list of all user playlists
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

def get_youtube_playlists(youtube):
   # Gets user youtube music playlists
   user_playlists = ytmusic.get_library_playlists(1000)
   yt_lists = {}
   for i in user_playlists:
      playlist_name = i['title']
      playlist_id = i['playlistId']
      yt_lists[playlist_name] = playlist_id
   return yt_lists

def get_tidal_playlists(tidal):
   # Gets user tidal playlists
   user_playlists = tidal.user.playlists()
   tidl_lists = {}
   for i in user_playlists:
      playlist_name = i.name
      playlist_id = i.id
      # Add playlist name and ids to dictionary
      tidl_lists[playlist_name] = playlist_id
   return tidl_lists


### Make sure user selected playlist exists
def spfy_source_check(source_playlist_name):
   # Checks if selected spotify playlist exists
   if source_playlist_name not in spfy_lists:
      print("[-] Spotify: Selected {} Playlist does not exist".format(source_playlist_name))
      return None
   source_playlist_id = spfy_lists[source_playlist_name]
   return source_playlist_id

def yt_source_check(source_playlist_name):
   # Checks if selected youtube music playlist exists
   if source_playlist_name not in yt_lists:
      print("[-] Youtube: Selected {} Playlist does not exist".format(source_playlist_name))
      return None
   source_playlist_id = yt_lists[source_playlist_name]
   return source_playlist_id

def tidal_source_check(source_playlist_name):
   # Checks if selected youtube music playlist exists
   if source_playlist_name not in tidl_lists:
      print("[-] Tidal: Selected {} Playlist does not exist".format(source_playlist_name))
      return None
   source_playlist_id = tidl_lists[source_playlist_name]
   return source_playlist_id



### Check if destination playlist exists, creates new one if not
def yt_dest_check(dest_playlist_name):
   if dest_playlist_name in yt_lists:
      dest_playlist_id = yt_lists[dest_playlist_name]
      print("[+] Youtube: Playlist exists, adding missing songs")
   else:
      dest_playlist_id = ytmusic.create_playlist(dest_playlist_name,"Sound Tunnel playlist")
      print("[+] Youtube: Playlist created")
   return dest_playlist_id

def spfy_dest_check(dest_playlist_name):
   if dest_playlist_name in spfy_lists:
      dest_playlist_id = spfy_lists[dest_playlist_name]
      print("[+] Spotify: Playlist exists, adding missing songs")
   else:
      create_playlist = spotify.user_playlist_create(spfy_id, dest_playlist_name, public=False, collaborative=False, description='Sound Tunnel Playlist')
      dest_playlist_id = create_playlist['id']
      print("[+] Spotify: Playlist created")
   return dest_playlist_id

def tidal_dest_check(dest_playlist_name):
   if dest_playlist_name in tidl_lists:
      dest_playlist_id = tidl_lists[dest_playlist_name]
      print("[+] Tidal: Playlist exists, adding missing songs")
   else:
      dest_playlist_id = tidal_create_playlist(dest_playlist_name,"Sound Tunnel playlist", tidal.access_token)
      print("[+] Tidal: Playlist created")
   return dest_playlist_id


### Get tracks on selected playlist
def get_spfy_playlist_content(source_id):
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
      result.append(album_name+"&"+song_name+"&"+artist)
   return result

def get_yt_playlist_content(source_id):
   playlist_content = ytmusic.get_playlist(source_id)
   result = []
   for song in playlist_content['tracks']:
      song_name = song['title']
      try:
         album_name = song['album']['name']
      except:
         album_name = ""
      artist_name = []
      for i in song['artists']:
         artist = i['name']
         artist_name.append(artist)
      artist = ' '.join(artist_name)
      result.append(album_name+"&"+song_name+"&"+artist)
   return result

def get_tidal_playlist_content(source_id):
   playlist_content = tidal.get_playlist_items(source_id)
   result = []
   for song in playlist_content:
      song_name = song.name
      album_name = song.album.name
      artist_name = []
      for i in song.artists:
         artist = i.name
         artist_name.append(artist)
      artist = ' '.join(artist_name)
      result.append(album_name+"&"+song_name+"&"+artist)
   return result



### Move tracks to playlist
def move_to_ytmusic(playlist_info, dest_id):
   not_found = []
   try:
      for i in playlist_info:
         i = i.replace("&", " ")
         search = ytmusic.search(i, "songs")
         songid = [search[0]['videoId']]
         time.sleep(0.5)
         add_success = ytmusic.add_playlist_items(dest_id, songid)
         # Didn't add compare since yt has everything and has good search algo
         if "song is already in the playlist" in add_success or "SUCCEEDED" in add_success:
            pass
         else:
            not_found.append(i)
      return not_found
   except Exception:
      return not_found

def move_to_spfy(playlist_info, dest_id):
   not_found = []
   try:
      for i in playlist_info:
         i = i.replace("&", " ")
         search = spotify.search(i, limit=5, type="track")
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
               time.sleep(0.5)
               spotify.playlist_add_items(dest_id, songid)
               break
         else:
            not_found.append(i)
      return not_found
   except:
      return not_found

def move_to_tidal(playlist_info, dest_id):
   not_found = []
   try:
      for i in playlist_info:
         op = i.replace("&", " ")
         i = ' '.join(i.split("&")[1:])
         search = tidal_search_playlist(i, tidal.access_token)
         for song in search['tracks']['items']:
            album_name = song['album']['title']
            song_name = song['title']
            artist_name = []
            for j in song['artists']:
               artist = j['name']
               artist_name.append(artist)
            artist = ' '.join(artist_name)
            found = album_name+" "+song_name+" "+artist
            songid = song['id']
            if compare(found, op):
               time.sleep(0.5)
               tidal_add_song_to_playlist(dest_id, songid, tidal.access_token)
               break
         else:
            not_found.append(i)
      return not_found
   except:
      return not_found




### Move Spotify playlists to Youtube music
# Will edit to fit code structure
def get_spfy_likes():
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
         result.append(album_name+"&"+song_name+"&"+artist)
   return result


### Tidal API functions
def tidal_create_playlist(playlist_name, playlist_desc, access_token):
   tidal_create_playlist_url = 'https://listen.tidal.com/v2/my-collection/playlists/folders/create-playlist?description={}&folderId=root&name={}&countryCode=NG&locale=en_US&deviceType=BROWSER'.format(playlist_desc, playlist_name)
   headers = {'authority': 'listen.tidal.com', 'authorization': 'Bearer {}'.format(access_token), 'origin': 'https://listen.tidal.com', 'referer': 'https://listen.tidal.com/my-collection/playlists'}
   r = requests.put(tidal_create_playlist_url, headers = headers)
   playlist_id = r.json()['data']['uuid']
   return playlist_id

def tidal_search_playlist(search_query, access_token):
   tidal_search_playlist_url = 'https://listen.tidal.com/v1/search/top-hits?query={}&limit=5&offset=0&types=TRACKS&includeContributors=true&countryCode=NG&locale=en_US&deviceType=BROWSER'.format(search_query)   headers = {'authority': 'listen.tidal.com', 'authorization': 'Bearer {}'.format(access_token), 'origin': 'https://listen.tidal.com', 'referer': 'https://listen.tidal.com/my-collection/playlists'}
   r = requests.get(tidal_search_playlist_url, headers = headers)
   return r.json()

def tidal_add_song_to_playlist(playlist_id, song_id, access_token):
   tidal_get_request = "https://listen.tidal.com/v1/playlists/{}?countryCode=NG&locale=en_US&deviceType=BROWSER".format(playlist_id)
   get_headers = {'Host': 'listen.tidal.com','User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:102.0) Gecko/20100101 Firefox/102.0' ,'Accept':'*/*','Accept-Language': 'en-US,en;q=0.5', 'Accept-Encoding':'gzip,deflate','Sec-Fetch-Dest': 'empty', 'Sec-Fetch-Mode': 'cors','Sec-Fetch-Site': 'same-origin','authorization': 'Bearer {}'.format(access_token), 'origin': 'https://listen.tidal.com', 'referer': 'https://listen.tidal.com/my-collection/playlists'}
   rasd = requests.get(tidal_get_request, headers=get_headers)
   etag = rasd.headers['Etag']
   tidal_add_song_url = "https://listen.tidal.com/v1/playlists/{}/items?countryCode=NG&locale=en_US&deviceType=BROWSER".format(playlist_id)
   headers = {'authority': 'listen.tidal.com', 'authorization': 'Bearer {}'.format(access_token), 'origin': 'https://listen.tidal.com', 'referer': 'https://listen.tidal.com/playlist/{}'.format(playlist_id),'dnt':'1', 'if-none-match':etag}
   data = {'onArtifactNotFound':'FAIL','onDupes':'FAIL','trackIds':'{}'.format(song_id)}
   r = requests.post(tidal_add_song_url, headers = headers, data=data)

### General functions
def change_name():
   # Changes spfy2yt to sound-tunnel for users of old script
   for i in yt_lists:
      if "spfy2yt" in i:
         new_name = i.replace("spfy2yt","sound-tunnel")
         id = yt_lists[i]
         success = ytmusic.edit_playlist(id,new_name)
         if success == 'STATUS_SUCCEEDED':
            print("[+] Youtube: Renamed {} to {} to fit new script".format(i,new_name))

def compare(first, second):
   # Compare 2 song info to make sure it's the same song
   match = SequenceMatcher(None, first, second).ratio()
   #if match is less than 45%, not a match
   if match > 0.45:
      return True
   else:
      return False

def display_playlists(lists):
   # Display user playlists for selected platform
   for name in lists:
      print(name)

def tunnel(source_playlist_name, source, destination):
   # Carry out basic checks and tunnel
   if " sound-tunnel" in source_playlist_name:
      dest_playlist_name = source_playlist_name
   else:
      dest_playlist_name = source_playlist_name + " sound-tunnel"

   if source == 'spotify':
      if source_playlist_name.lower() == "your likes":
         playlist_info = get_spfy_likes()
      else:
         source_playlist_id = spfy_source_check(source_playlist_name)
         playlist_info = get_spfy_playlist_content(source_playlist_id)
   elif source == 'youtube':
      source_playlist_id = yt_source_check(source_playlist_name)
      playlist_info = get_yt_playlist_content(source_playlist_id)
   elif source == 'tidal':
      source_playlist_id = tidal_source_check(source_playlist_name)
      playlist_info = get_tidal_playlist_content(source_playlist_id)
   else:
      print("[-]: {} is an unrecognized source. Use 'spotify', 'tidal' or 'youtube'".format(source))
      sys.exit(1)

   if destination == 'youtube':
      dest_playlist_id = yt_dest_check(dest_playlist_name)
      not_found = move_to_ytmusic(playlist_info, dest_playlist_id)
   elif destination == 'spotify':
      dest_playlist_id = spfy_dest_check(dest_playlist_name)
      not_found = move_to_spfy(playlist_info, dest_playlist_id)
   elif destination == 'tidal':
      dest_playlist_id = tidal_dest_check(dest_playlist_name)
      not_found = move_to_tidal(playlist_info, dest_playlist_id)
   else:
      print("[-]: {} is an unrecognized destination. Use 'spotify', 'tidal' or 'youtube'".format(destination))
      sys.exit(1)

   write_to_file(source_playlist_name, not_found, source, destination)

def write_to_file(play_name, songs, source, dest):
   # Write not found songs to file
   key = "{}->{} '{}'".format(source, dest, play_name)
   content = {key: songs}
   with open('notfound.txt', 'a') as file:
      file.write(json.dumps(content))
      file.write("\n")

def main():
   argz = [args.source, args.destination]
   if 'youtube' in argz:
      global ytmusic
      global yt_lists
      ytmusic = ytmusic_auth()
      yt_lists = get_youtube_playlists(ytmusic)
      change_name()

   if 'spotify' in argz:
      global spotify
      global spfy_lists
      global spfy_id
      spotify = spotify_auth()
      spfy_id = spotify.me()['id']
      spfy_lists = get_spotify_playlists(spotify)

   if 'tidal' in argz:
      global tidl_lists
      global tidal
      tidal = tidal_auth()
      tidl_lists = get_tidal_playlists(tidal)


   if args.L:
      if args.source == "spotify":
         print("[+] Spotify: Displaying Playlists\n")
         print("Your Likes")
         display_playlists(spfy_lists)
      elif args.source == "youtube":
         print("[+] Youtube: Displaying Playlists\n")
         display_playlists(yt_lists)
      elif args.source == "tidal":
         print("[+] Tidal: Displaying Playlists\n")
         display_playlists(tidl_lists)
      else:
         print("-s {} is unrecognized. Use '-s youtube', '-s spotify' etc".format(args.source))
         sys.exit(0)
   elif args.p:
      tunnel(args.p, args.source, args.destination)
   elif args.P:
      file_path = abspath(args.P)
      playlist_names = []
      try:
         with open(file_path, "r") as ff:
            for line in ff:
               playlist_names.append(line.strip())
      except:
         print("[-] : {} does not exist".format(file_path))
         sys.exit(1)
      for playlist in playlist_names:
         tunnel(playlist, args.source, args.destination)
   elif args.A:
      if args.source == 'spotify':
         tunnel("your likes", args.source, args.destination)
         for playlist in spfy_lists:
            tunnel(playlist, args.source, args.destination)
      elif args.source == 'youtube':
         for playlist in yt_lists:
            tunnel(playlist, args.source, args.destination)
      elif args.source == 'tidal':
         for playlist in tidl_lists:
            tunnel(playlist, args.source, args.destination)

parser = argparse.ArgumentParser(description="Sound Tunnel. Move playlists back and forth between YTmusic, Spotify and Tidal")
parser.add_argument('-s','--source',required=True, help="Select source platform (spotify, tidal or youtube) e.g -s spotify")
parser.add_argument('-d','--destination', help="Select destination platform (spotify, tidal or youtube) e.g -d youtube")

group = parser.add_mutually_exclusive_group()
group.add_argument('-p', help="Move playlists with name specified in stdin")
group.add_argument('-P', help="Move playlists with name stored in file")
group.add_argument('-A',action='store_true', help="Move all playlists")
group.add_argument('-L',action='store_true', help="Show user Playlists for Spotify, Tidal or Youtube")

args = parser.parse_args()
main()
