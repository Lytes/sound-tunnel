import sys
import re
import requests
import tidalapi
from time import sleep
from datetime import datetime
from src.mainfuncs import message, what_to_move, compare
from config.config import tidalfile

def tidal_auth():
   # Attempt to authenticate Tidal
   try:
      tidal = tidalapi.Session()
      try:
         with open(tidalfile, 'r') as file:
            cred = [line.rstrip() for line in file]
         expiry_time: datetime = datetime.strptime(cred[3], "%m/%d/%Y, %H:%M:%S.%f")
         if expiry_time > datetime.now() and tidal.load_oauth_session(cred[0], cred[1], cred[2], expiry_time):
            message("t+","Successfully Authenticated")
            return tidal
      except:
         pass
      tidal.login_oauth_simple()
      if tidal.check_login():
         message("t+","Successfully Authenticated")
         creds = [tidal.token_type, tidal.access_token, tidal.refresh_token, tidal.expiry_time.strftime("%m/%d/%Y, %H:%M:%S.%f")]
         with open(tidalfile, 'w') as file:
            file.write('\n'.join(creds))
         return tidal
      else:
         var_error_out
   except:
      message("t-","Authentication failed")
      sys.exit(0)
      
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

def get_tidal_playlist_content(tidal,source_id):
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
      result.append(album_name+"&@#72"+song_name+"&@#72"+artist)
   return result

def tidal_dest_check(tidl_lists, tidal, dest_playlist_name):
   if dest_playlist_name in tidl_lists:
      dest_playlist_id = tidl_lists[dest_playlist_name]
      message("t+","Playlist exists, adding missing songs")
   else:
      dest_playlist_id = tidal_create_playlist(dest_playlist_name,"Sound Tunnel playlist", tidal.access_token)
      message("t+","Playlist created")
   return dest_playlist_id

def move_to_tidal(tidal, playlist_info, dest_id):
   not_found = []
   present_song = get_tidal_playlist_content(tidal,dest_id)
   playlist_info = what_to_move(present_song, playlist_info)
   not_found = []
   try:
      for i in playlist_info:
         op = i.replace("&@#72", " ")
         i = ' '.join(i.split("&@#72")[1:])
         search = tidal_search_playlist(i, tidal.access_token)
         if len(str(search)) == 408:
            bk = i
            i = re.sub("\(.*?\)","",i)
            search = tidal_search_playlist(i, tidal.access_token)
            if len(list(search)) == 408:
               not_found.append(bk)
               continue
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
               sleep(0.5)
               tidal_add_song_to_playlist(dest_id, songid, tidal.access_token)
               break
         else:
            not_found.append(i)
      return not_found
   except:
      return not_found



def tidal_create_playlist(playlist_name, playlist_desc, access_token):
   tidal_create_playlist_url = 'https://listen.tidal.com/v2/my-collection/playlists/folders/create-playlist?description={}&folderId=root&name={}&countryCode=NG&locale=en_US&deviceType=BROWSER'.format(playlist_desc, playlist_name)
   headers = {'authority': 'listen.tidal.com', 'authorization': 'Bearer {}'.format(access_token), 'origin': 'https://listen.tidal.com', 'referer': 'https://listen.tidal.com/my-collection/playlists'}
   r = requests.put(tidal_create_playlist_url, headers = headers)
   playlist_id = r.json()['data']['uuid']
   return playlist_id

def tidal_search_playlist(search_query, access_token):
   tidal_search_playlist_url = 'https://listen.tidal.com/v1/search/top-hits?query={}&limit=5&offset=0&types=TRACKS&includeContributors=true&countryCode=NG&locale=en_US&deviceType=BROWSER'.format(search_query)
   headers = {'authority': 'listen.tidal.com', 'authorization': 'Bearer {}'.format(access_token), 'origin': 'https://listen.tidal.com', 'referer': 'https://listen.tidal.com/my-collection/playlists'}
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
