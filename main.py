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


def change_name():
   # Changes spfy2yt Sound-tunnel
   for i in yt_lists:
      if "spfy2yt" in i:
         new_name = i.replace("spfy2yt","sound-tunnel")
         id = yt_lists[i]
         success = ytmusic.edit_playlist(id,new_name)
         if success == 'STATUS_SUCCEEDED':
            print("Renamed {} to {} to fit new script".format(i,new_name))

def spotify_auth():
# Attempt to authenticate Spotify
   try:
      spotify = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=cfg.CLIENT_ID, client_secret=cfg.CLIENT_SECRET, redirect_uri=cfg.REDIRECT_URI, scope=cfg.SCOPE))
      print("[+][S] Spotify: Successfully Authenticated")
      return spotify
   except Exception:
      print("[-][S] Spotify: Authentication failed")
      sys.exit(0)
   # added print(auth_url) to line 435 of /usr/local/lib/python3.10/dist-packages/spotipy/oauth2.py so that the script would print the link
   # why? because wsl2 sucks

def get_spotify_playlists(spotify):
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

def ytmusic_auth():
   # Attempt to authenticate Youtube music
   try:
      ytmusic = YTMusic(cfg.ytfile)
      print("[+] YouTube: Successfully Authenticated")
      return ytmusic
   except:
      print("[-] Youtube: Authentication failed")
      sys.exit(0)

def get_youtube_playlists(youtube):
   user_playlists = ytmusic.get_library_playlists(1000)
   yt_lists = {}
   for i in user_playlists:
      playlist_name = i['title']
      playlist_id = i['playlistId']
      yt_lists[playlist_name] = playlist_id
   return yt_lists

def display_playlists(lists):
   for name in lists:
      print(name)

def get_ytid_from_spfy(source_playlist_name):
   transfer_info = []
   if source_playlist_name not in spfy_lists:
      print("[-] Spotify: Selected {} Playlist does not exist".format(source_playlist_name))
      return None
   source_playlist_id = spfy_lists[source_playlist_name]
   dest_playlist_name = source_playlist_name + " sound-tunnel"
   if dest_playlist_name in yt_lists:
      dest_playlist_id = yt_lists[dest_playlist_name]
      print("[+] Youtube: Playlist exists, adding missing songs")
   else:
      dest_playlist_id = ytmusic.create_playlist(dest_playlist_name,"Spotify Playlist ported to Youtube")
      print("[+] Youtube: Playlist created")
   transfer_info.append(source_playlist_id)
   transfer_info.append(dest_playlist_id)
   return transfer_info

def spfy_liked_to_yt():
   dest_playlist_name = "Spotify Liked Songs sound-tunnel"
   if dest_playlist_name in yt_lists:
      dest_playlist_id = yt_lists[dest_playlist_name]
      print("[+] Youtube: {} exists, adding missing songs".format(dest_playlist_name))
   else:
      dest_playlist_id = ytmusic.create_playlist(dest_playlist_name,"Spotify Playlist ported to Youtube")
      print("[+] Youtube: Created {} ".format(dest_playlist_name))
   test_likes = spotify.current_user_saved_tracks(limit=50)
   no_of_liked_songs = test_likes['total']
   total_requests = ceil(no_of_liked_songs/50)
   for i in range(total_requests):
      print("working on {} iteration".format(i))
      like = spotify.current_user_saved_tracks(limit=50, offset=50*i)
      for song in like['items']:
         song_name = song['track']['name']
         album_name = song['track']['album']['name']
         artist_name = []
         for i in song['track']['artists']:
            artist = i['name']
            artist_name.append(artist)
         artist = ' '.join(artist_name)
         time.sleep(1)
         search = ytmusic.search("{} {}".format(song_name, artist), "songs")
         songid = [search[0]['videoId']]
         ytmusic.add_playlist_items(dest_playlist_id, songid)
         

def spfy_to_yt(transfer_info):
   # transfer_info = [source_id, dest_id]
   source_id = transfer_info[0]
   dest_id = transfer_info[1]
   playlist_content = spotify.playlist_items('spotify:playlist:{}'.format(source_id))
   for song in playlist_content['items']:
      song_name = song['track']['name']
      album_name = song['track']['album']['name']
      artist_name = []
      for i in song['track']['artists']:
         artist = i['name']
         artist_name.append(artist)
      artist = ' '.join(artist_name)
      search = ytmusic.search("{} {}".format(song_name, artist), "songs")
      songid = [search[0]['videoId']]
      ytmusic.add_playlist_items(dest_id, songid)

def main():
   global ytmusic
   global spotify
   global spfy_lists
   global yt_lists
   global spfy_id
   ytmusic = ytmusic_auth()
   spotify = spotify_auth()
   spfy_id = spotify.me()['id']
   change_name()
   spfy_lists = get_spotify_playlists(spotify)
   yt_lists = get_youtube_playlists(ytmusic)
   if args.S:
      if args.source == "spotify":
         print("[+][S] Spotify: Displaying Playlists\n")
         display_playlists(spfy_lists)
      elif args.source == "youtube":
         print("[+][S] Youtube: Displaying Playlists\n")
         display_playlists(yt_lists)
      else:
         print("-s {} is unrecognized. Use '-s youtube' or '-s spotify'".format(args.source))
         sys.exit(0)
   elif args.p:
      if args.source == 'spotify' and args.destination == 'youtube':
         source_playlist_name = args.p
         transfer_info = get_ytid_from_spfy(source_playlist_name)
         if transfer_info == None:
            sys.exit(1)
         spfy_to_yt(transfer_info)
   elif args.P:
      if args.source == 'spotify' and args.destination == 'youtube':
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
            transfer_info = get_ytid_from_spfy(playlist)
            if transfer_info == None:
               print("[-] Spotify: {} does not exist. Skipping to next".format(playlist))
            else:
               spfy_to_yt(transfer_info)
   elif args.A:
      if args.source == 'spotify' and args.destination == 'youtube':
         for playlist in spfy_lists:
            print("[-] Spotify: Transferring {} to Youtube".format(playlist))
            transfer_info = get_ytid_from_spfy(playlist)
            spfy_to_yt(transfer_info)
            spfy_liked_to_yt()
   elif args.L:
      spfy_liked_to_yt()
   elif args.source == 'youtube' or args.destination == 'spotify':
       print("Haven't added that yet. Just Spotify -> Youtube... for now.")

parser = argparse.ArgumentParser(description="Sound Tunnel. Move playlists back and forth between YTmusic and Spotify")
parser.add_argument('-S',action='store_true', help="Show user Playlists for Spotify or Youtube")
parser.add_argument('-s','--source',required=True, help="Select source platform (spotify or youtube) e.g -s spotify")
parser.add_argument('-d','--destination', help="Select destination platform (spotify or youtube) e.g -d youtube")

group = parser.add_mutually_exclusive_group()
group.add_argument('-p', help="Move playlists with name specified in stdin")
group.add_argument('-P', help="Move playlists with name stored in file")
group.add_argument('-A',action='store_true', help="Move all playlists")
group.add_argument('-L',action='store_true', help="Move Users Liked List")

args = parser.parse_args()
main()
