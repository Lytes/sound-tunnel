"""
Spotify to YT
@kuro_lytes
"""
import time
from spotipy.oauth2 import SpotifyOAuth
import spotipy
import config as cfg
import sys
from ytmusicapi import YTMusic

def spotify_auth():
   try:
      spotify = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=cfg.CLIENT_ID, client_secret=cfg.CLIENT_SECRET, redirect_uri=cfg.REDIRECT_URI, scope=cfg.SCOPE))
      print("[+] Spotify: Successfully Authenticated")
      return spotify
   except Exception:
      print("[-] Spotify: Authentication failed")
      sys.exit(0)
   # added print(auth_url) to line 435 of /usr/local/lib/python3.10/dist-packages/spotipy/oauth2.py so that the script would print the link
   # why? because wsl2 sucks


def get_spotify_playlists(spotify):
   user_deet = spotify.me() #gets user details
   user_playlists = spotify.current_user_playlists() #gets user playlists
   print("[+] Spotify: Getting playlists")
   spott = []
   for i in user_playlists['items']:
      playlist_name = i['name']
      playlist_id = i['id']
      play_info = [playlist_name, playlist_id]
      time.sleep(0.3)
      playlist_content = spotify.playlist_items('spotify:playlist:{}'.format(playlist_id))
      playy = []
      playy.append(play_info)
      for song in playlist_content['items']:
         try:
            song_name = song['track']['name']
            album_name = song['track']['album']['name']
            artist_name = []
            for i in song['track']['artists']:
               artist = i['name']
               artist_name.append(artist)
            songg = [song_name, artist_name, album_name]
            playy.append(songg)
         except:
            pass
      spott.append(playy)
   return spott

def add_spot_to_youtube(spotdeets, ytmusic):
   notfound = []
   userplaylists = {}
   uplaylists = ytmusic.get_library_playlists(1000)
   for i in uplaylists:
      userplaylists[i['title']] = i['playlistId']

   for playlist in spotdeets:
      playlist_name = playlist[0][0]+" spfy2yt"
      try:
         if playlist_name in userplaylists.keys():
            ytplay_id = userplaylists[playlist_name]
            print("[+] Youtube: {} playlist exists. Adding any missing song.".format(playlist_name))
         else:
            ytplay_id = ytmusic.create_playlist(playlist_name,"Spotify Playlist ported to Youtube")
            # create yt playlist with name
            print("[+] Youtube: Created {} playlist".format(playlist_name))
      except Exception:
         print("[-] Youtube: Error creating Playlist")
         write_to_file(notfound)
         sys.exit(0)
      for i in range(1, len(playlist)):
         song = playlist[i]
         songname = song[0]
         artist = ' '.join(song[1])
         albumname = song[2]
         search = ytmusic.search("{} {}".format(songname, artist), "songs")
         try:
            time.sleep(0.3)
            songid = [search[0]['videoId']]
            add_success = ytmusic.add_playlist_items(ytplay_id, songid)
            if "song is already in the playlist" in add_success or "SUCCEEDED" in add_success:
               print("[+] Youtube: Added {} by {} to {}".format(songname, artist, playlist_name))
            else:
               random_variable_that_doesnt_exist_so_script_will_error_out
         except Exception:
            notsong = [playlist_name, songname, artist, albumname]
            notfound.append(notsong)
   writer.write(notfound)

def write_to_file(writethis):
   with open("notfound.txt", "a") as writer:
      writethis ="{}".format(writethis)
      writer.write(writethis)

def ytmusic_auth():
   try:
      ytmusic = YTMusic(cfg.ytfile)
      print("[+] YouTube: Successfully Authenticated")
      return ytmusic
   except:
      print("[-] Youtube: Authentication failed")
      sys.exit(0)


def main():
   spotify = spotify_auth()
   ytmusic = ytmusic_auth()
   spotdeets = get_spotify_playlists(spotify)
   add_spot_to_youtube(spotdeets, ytmusic)

main()
