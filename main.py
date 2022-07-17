"""
Sound Tunnel
@kuro_lytes
"""

import argparse
from os.path import abspath
from src.ytfuncs import *
from src.spfyfuncs import *
from src.tidalfuncs import *
from src.mainfuncs import *
from src.applefuncs import *

def tunnel(source_playlist_name, source, destination, core_sessions):
   # Carry out basic checks and tunnel
   if " sound-tunnel" in source_playlist_name:
      dest_playlist_name = source_playlist_name
   else:
      dest_playlist_name = source_playlist_name + " sound-tunnel"
   if 'spotify' in source+destination:
      spotify = core_sessions['s'][0]
      spfy_lists = core_sessions['s'][1]
      spfy_id = core_sessions['s'][2]
   if 'youtube' in source+destination:
      ytmusic = core_sessions['y'][0]
      yt_lists = core_sessions['y'][1]
   if 'tidal' in source+destination:
      tidal = core_sessions['t'][0]
      tidl_lists = core_sessions['t'][1]
   if 'apple' in source+destination:
      apple = core_sessions['a'][0]
      apple_lists = core_sessions['a'][1]
            
   if source == 'spotify':
      if source_playlist_name.lower() == "your likes":
         playlist_info = get_spfy_likes(spotify)
      else:
         source_playlist_id = confirm_playlist_exist(source_playlist_name, spfy_lists)
         playlist_info = get_spfy_playlist_content(spotify, source_playlist_id)
   elif source == 'youtube':
      source_playlist_id = confirm_playlist_exist(source_playlist_name, yt_lists)
      playlist_info = get_yt_playlist_content(ytmusic, source_playlist_id)
   elif source == 'tidal':
      source_playlist_id = confirm_playlist_exist(source_playlist_name, tidl_lists)
      playlist_info = get_tidal_playlist_content(tidal, source_playlist_id)
   elif source == 'apple':
      source_playlist_id = confirm_playlist_exist(source_playlist_name, apple_lists)
      playlist_info = get_apple_playlist_content(apple, source_playlist_id)
   else:
      print("[-]: {} is an unrecognized source. Use 'spotify', 'tidal' or 'youtube'".format(source))
      sys.exit(1)

   if destination == 'youtube':
      dest_playlist_id = yt_dest_check(ytmusic, yt_lists, dest_playlist_name)
      not_found = move_to_ytmusic(ytmusic, playlist_info, dest_playlist_id)
   elif destination == 'spotify':
      dest_playlist_id = spfy_dest_check(spfy_lists, spotify, spfy_id, dest_playlist_name)
      not_found = move_to_spfy(spotify, playlist_info, dest_playlist_id)
   elif destination == 'tidal':
      dest_playlist_id = tidal_dest_check(tidl_lists, tidal, dest_playlist_name)
      not_found = move_to_tidal(tidal, playlist_info, dest_playlist_id)
   elif destination == 'apple':
      dest_playlist_id = apple_dest_check(apple_lists, apple, dest_playlist_name)
      not_found = move_to_apple(apple, playlist_info, dest_playlist_id)
   else:
      print("[-]: {} is an unrecognized destination. Use 'spotify', 'tidal' or 'youtube'".format(destination))
      sys.exit(1)

   write_to_file(source_playlist_name, not_found, source, destination)


def main():
   args = options()
   if args.source == args.destination:
      print("[-]: Nice try but no you can't move from {} to {}, they are the same platform".format(args.source, args.source))
      sys.exit(1)
   argz = [args.source, args.destination]
   core_sessions = {}
   if 'youtube' in argz:
      ytmusic = ytmusic_auth()
      yt_lists = get_youtube_playlists(ytmusic)
      change_name(ytmusic, yt_lists)
      core_sessions['y'] = [ytmusic, yt_lists]
   if 'spotify' in argz:
      spotify = spotify_auth()
      spfy_id = spotify.me()['id']
      spfy_lists = get_spotify_playlists(spotify)
      core_sessions['s'] = [spotify, spfy_lists, spfy_id]
   if 'tidal' in argz:
      tidal = tidal_auth()
      tidl_lists = get_tidal_playlists(tidal)
      core_sessions['t'] = [tidal, tidl_lists]
   if 'apple' in argz:
      apple = apple_auth()
      apple_lists = get_apple_playlists(apple)
      core_sessions['a'] = [apple, apple_lists]
   if args.L:
      if args.source == "spotify":
         message("s+","Displaying Playlists\n")
         print("Your Likes")
         display_playlists(spfy_lists)
      elif args.source == "youtube":
         message("y+","Displaying Playlists\n")
         display_playlists(yt_lists)
      elif args.source == "tidal":
         message("t+","Displaying Playlists\n")
         display_playlists(tidl_lists)
      elif args.source == 'apple':
         message("a+","Displaying Playlists\n")
         display_playlists(apple_lists)
      else:
         print("-s {} is unrecognized. Use '-s youtube', '-s spotify' etc".format(args.source))
         sys.exit(0)
   elif args.p:
      tunnel(args.p, args.source, args.destination, core_sessions)
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
         tunnel(playlist, args.source, args.destination, core_sessions)
   elif args.A:
      if args.source == 'spotify':
         tunnel("your likes", args.source, args.destination, core_sessions)
         for playlist in spfy_lists:
            tunnel(playlist, args.source, args.destination, core_sessions)
      elif args.source == 'youtube':
         for playlist in yt_lists:
            tunnel(playlist, args.source, args.destination, core_sessions)
      elif args.source == 'tidal':
         for playlist in tidl_lists:
            tunnel(playlist, args.source, args.destination, core_sessions)
      elif args.source == 'apple':
         for playlist in apple_lists:
            tunnel(playlist, args.source, args.destination, core_sessions)
       
def options():     
   parser = argparse.ArgumentParser(description="Sound Tunnel. Move playlists back and forth between YTmusic, Spotify, Apple and Tidal")
   parser.add_argument('-s','--source',required=True, help="Select source platform (spotify, apple, tidal or youtube) e.g -s spotify")
   parser.add_argument('-d','--destination', help="Select destination platform (spotify,apple, tidal or youtube) e.g -d youtube")

   group = parser.add_mutually_exclusive_group()
   group.add_argument('-p', help="Move playlists with name specified in stdin")
   group.add_argument('-P', help="Move playlists with name stored in file")
   group.add_argument('-A',action='store_true', help="Move all playlists")
   group.add_argument('-L',action='store_true', help="Show user Playlists for Spotify, Tidal or Youtube")
   args = parser.parse_args()
   return args

if __name__ == "__main__":
   main()   
