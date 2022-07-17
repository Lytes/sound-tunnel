import json
from difflib import SequenceMatcher

def message(bit, msg):
   code = bit[1]
   plat = bit[0]
   output = "[{}] ".format(code)
   if plat.lower() == "s":
      output = output + "Spotify: "
   elif plat.lower() == "y":
      output = output + "Youtube: "
   elif plat.lower() == "t":
      output = output + "Tidal: "
   elif plat.lower() == "a":
      output = output + "Apple: "
   output = output + msg
   print(output) 
   
def display_playlists(lists):
   # Display user playlists for selected platform
   for name in lists:
      print(name)
      
def confirm_playlist_exist(source_playlist_name, plat_list):
   if source_playlist_name not in plat_list:
      message("s+","Selected {} Playlist does not exist".format(source_playlist_name))
      return None
   source_playlist_id = plat_list[source_playlist_name]
   return source_playlist_id

def what_to_move(old, new):
   new = list(set(new) - set(old))
   return new

def compare(first, second):
   # Compare 2 song info to make sure it's the same song
   match = SequenceMatcher(None, first, second).ratio()
   #if match is less than 45%, not a match
   if match > 0.45:
      return True
   else:
      return False
   
def write_to_file(play_name, songs, source, dest):
   # Write not found songs to file
   key = "{}->{} '{}'".format(source, dest, play_name)
   content = {key: songs}
   with open('notfound.txt', 'a') as file:
      file.write(json.dumps(content))
      file.write("\n")