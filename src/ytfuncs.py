from ytmusicapi import YTMusic
from src.mainfuncs import message, what_to_move
import sys
from time import sleep
from config.config import ytfile

def ytmusic_auth():
    # Attempt to authenticate Youtube music
    try:
        ytmusic = YTMusic(ytfile)
        message("y+","Successfully Authenticated")
        return ytmusic
    except:
        message("y+","Authentication failed")
        sys.exit(0)
      
def get_youtube_playlists(ytmusic):
   # Gets user youtube music playlists
   user_playlists = ytmusic.get_library_playlists(1000)
   yt_lists = {}
   for i in user_playlists:
      playlist_name = i['title']
      playlist_id = i['playlistId']
      yt_lists[playlist_name] = playlist_id
   return yt_lists

def change_name(ytmusic, yt_lists):
   # Changes spfy2yt to sound-tunnel for users of old script
   for i in yt_lists:
      if "spfy2yt" in i:
         new_name = i.replace("spfy2yt","sound-tunnel")
         id = yt_lists[i]
         success = ytmusic.edit_playlist(id,new_name)
         if success == 'STATUS_SUCCEEDED':
            message("y+","Renamed {} to {} to fit new script".format(i,new_name))
            
def get_yt_playlist_content(ytmusic, source_id):
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

def yt_dest_check(ytmusic, yt_lists, dest_playlist_name):
   if dest_playlist_name in yt_lists:
      dest_playlist_id = yt_lists[dest_playlist_name]
      message("y+","Playlist exists, adding missing songs")
   else:
      dest_playlist_id = ytmusic.create_playlist(dest_playlist_name,"Sound Tunnel playlist")
      message("y+", "Playlist created")
   return dest_playlist_id

def move_to_ytmusic(ytmusic, playlist_info, dest_id):
   not_found = []
   present_song = get_yt_playlist_content(ytmusic, dest_id)
   playlist_info = what_to_move(present_song, playlist_info)
   not_found = []
   try:
      for i in playlist_info:
         i = i.replace("&", " ")
         search = ytmusic.search(i, "songs")
         songid = [search[0]['videoId']]
         sleep(0.5)
         add_success = ytmusic.add_playlist_items(dest_id, songid)
         # Didn't add compare since yt has everything and has good search algo
         if "song is already in the playlist" in add_success or "SUCCEEDED" in add_success:
            pass
         else:
            not_found.append(i)
      return not_found
   except Exception:
      return not_found
