import requests
import json
import sys
import re
from math import ceil
from time import sleep
from src.mainfuncs import message, what_to_move, compare
from config.config import applefile

def apple_auth():
   try:
      with open(applefile, 'r') as f:
         cookies = json.load(f)
      headers = apple_is_logged_in(cookies['authorization'], cookies['media-user-token'])
      if headers:
         message("a+", "Successfully Authenticated")
         return headers
   except:
      pass
   message("a-", "Authentication failed")
   sys.exit(0)

def apple_is_logged_in(bearer, media):
   url = "https://amp-api.music.apple.com:443/v1/me/library/songs?limit=100&l=en-gb&platform=web"
   headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:102.0) Gecko/20100101 Firefox/102.0", "Accept": "*/*", "Accept-Language": "en-US,en;q=0.5", "Accept-Encoding": "gzip, deflate", "Referer": "https://music.apple.com/", "Authorization": bearer, "Media-User-Token": media, "Origin": "https://music.apple.com", "Sec-Fetch-Dest": "empty", "Sec-Fetch-Mode": "cors", "Sec-Fetch-Site": "same-site", "Te": "trailers"}
   r = requests.get(url, headers=headers)
   if r.status_code == 200:
      return headers
   else:
      return False

def appleapi_user_playlists(headers):
   url = "https://amp-api.music.apple.com/v1/me/library/playlists"
   r = requests.get(url, headers=headers)
   if r.status_code == 200:
      return r.json()

def get_apple_playlists(apple):
   user_playlists = appleapi_user_playlists(apple)
   apple_lists = {}
   for i in user_playlists['data']:
      playlist_name = i['attributes']['name']
      playlist_id = i['id']
      apple_lists[playlist_name] = playlist_id
   return apple_lists

def apple_dest_check(apple_lists, apple, dest_playlist_name):
   if dest_playlist_name in apple_lists:
      dest_playlist_id = apple_lists[dest_playlist_name]
      message("a+","Playlist exists, adding missing songs: \"{}\"".format(dest_playlist_name))
   else:
      dest_playlist_id = appleapi_create_playlist(dest_playlist_name, apple)
      message("a+","Playlist created: \"{}\"".format(dest_playlist_name))
   return dest_playlist_id

def appleapi_create_playlist(playlist_name, headers):
   url = "https://amp-api.music.apple.com:443/v1/me/library/playlists"
   data={"attributes": {"name": playlist_name}}
   r = requests.post(url, headers=headers, json=data)
   playlist_id = r.json()['data'][0]['id']
   return playlist_id

def get_apple_playlist_content(apple, source_id):
   playlist_content = appleapi_get_playlist_content(source_id, apple)
   result = []
   for song in playlist_content:
      artist = []
      artist.append(song['attributes']['artistName'])
      song_name = song['attributes']['name']
      if "(feat. " in song_name:
         artist_name = song_name.split("(feat. ")[1].split(')')[0]
         artist.append(artist_name)
      album_name = song['attributes']['albumName']
      artist = ' '.join(artist)
      result.append(album_name+"&@#72"+song_name+"&@#72"+artist)
   return result

def appleapi_get_playlist_content(source_id, headers):
   url = "https://amp-api.music.apple.com:443/v1/me/library/playlists/{}/tracks?l=en-GB".format(source_id)
   r = requests.get(url, headers=headers)
   if "errors" in r.json().keys():
      return []
   total = r.json()['meta']['total']
   return_data = r.json()['data']
   if total <= 100:
      return return_data
   total_requests = ceil(total/100)
   for i in range(1, total_requests):
      uri = url+"&offset={}".format(i * 100)
      r = requests.get(uri, headers=headers)
      return_data = set(return_data + r.json()['data'])
   return return_data

def move_to_apple(apple, playlist_info, dest_id):
   not_found = []
   present_song = get_apple_playlist_content(apple, dest_id)
   playlist_info = what_to_move(present_song, playlist_info)
   try:
      for i in playlist_info:
         i = i.replace("&@#72"," ")
         search = appleapi_music_search(i, apple)
         if len(list(search['results'].keys())) == 0:
            bk = i
            i = re.sub("\(.*?\)","",i)
            search = appleapi_music_search(i, apple)
            if len(list(search['results'].keys())) == 0:
               not_found.append(bk)
               continue
         for song in search['results']['song']['data']:
            artist = []
            artist.append(song['attributes']['artistName'])
            song_name = song['attributes']['name']
            if "(feat. " in song_name:
               artist_name = song_name.split("(feat. ")[1].split(')')[0]
               artist.append(artist_name)
            album_name = song['attributes']['albumName']
            artist = ' '.join(artist)
            songid = song['id']
            found = album_name+" "+song_name+" "+artist
            if compare(found, i):
               sleep(0.5)
               appleapi_add_playlist_item(dest_id, songid, apple)
               break
         else:
            not_found.append(i)
      return not_found
   except Exception:
      return not_found

def appleapi_music_search(query, headers):
   url = "https://amp-api.music.apple.com:443/v1/catalog/ng/search?term={}&l=en-gb&platform=web&types=songs&limit=5&relate%5Beditorial-items%5D=contents&include[editorial-items]=contents&include[albums]=artists&include[songs]=artists&include[music-videos]=artists&extend=artistUrl&fields[artists]=url%2Cname%2Cartwork%2Chero&fields%5Balbums%5D=artistName%2CartistUrl%2Cartwork%2CcontentRating%2CeditorialArtwork%2Cname%2CplayParams%2CreleaseDate%2Curl&with=serverBubbles%2ClyricHighlights&art%5Burl%5D=c%2Cf&omit%5Bresource%5D=autos".format(query)
   r = requests.get(url, headers=headers)
   return r.json()

def appleapi_add_playlist_item(dest_id, songid, headers):
   url = "https://amp-api.music.apple.com:443/v1/me/library/playlists/{}/tracks".format(dest_id)
   data={"data": [{"id": songid, "type": "songs"}]}
   r = requests.post(url, headers=headers, json=data)