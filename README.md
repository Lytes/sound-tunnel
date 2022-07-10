# sound-tunnel
Python3 script to transfer playlists across Spotify, Tidal and Youtube-Music using [spotipy](https://github.com/plamere/spotipy), [tidalapi](https://github.com/tamland/python-tidal) and [ytmusicapi](https://github.com/sigma67/ytmusicapi) respectively

---
## Setup
### Requirements
1. Install dependencies using `pip install -r requirements.txt`

### Spotify
1. Generate a new app at [https://developer.spotify.com/dashboard/applications)](https://developer.spotify.com/dashboard/applications)
2. Fill the `redirect_uri` from [config.py](./config.py) into the new app's settings
3. Fill in your `client_id` and `client_secret` from your Spotify app into [config.py](./config.py) file 

### YouTubeMusic
1. Open a new tab
2. Open the developer tools (Ctrl-Shift-I) and select the “Network” tab
3. Go to [https://music.youtube.com](https://music.youtube.com) and ensure you are logged in
4. Find an authenticated POST request.
5. Copy your cookies
6. Paste copied cookies in [headers_auth.json](headers_auth.json). Should look something like this
![example image](./image.png "Example img")

### Tidal Music
1. Easiest one. Run `main.py`. It provides a link link. 
2. Follow link to authorize the script.

---
## Commands
1. Display all flags with `python3 main.py --help`
2. Specify playlist source platform and destination platform with `--source`/`-s` and `--destination`/`-d` respectively
3. Display user playlists for source platfrom using `-L` e.g Display tidal playlists with
```
python3 main.py --source tidal -L
```
4. Copy a playlist (specify name in stdin) from one platform to the other using `-p` e.g Copy my "1am drive" playlists from spotify to ytmusic
```
python3 main.py -s spotify -d youtube -p "1am drive"
```
5. Playlist names can be specified from a file with each playlist name occupying a line
```
python3 main.py --source spotify --destination youtube -P ./myplaylists.txt
```
6. Transfer all playlists from one platform to the other using `-p` e.g Transfer all playlists from spotify to ytmusic (this includes Spotify liked songs)
```
python3 main.py --source spotify --destination youtube -A
```
---

### To-do
- [x] Allow users send specific playlists
- [x] Allow users send playlists specified in file
- [x] Add ytmusic to spotify
- [x] Add function to properly compare song names
- [x] Add a file to log songs not found
- [x] Clean code and make it easy to add platforms
- [x] Handle Spotify's liked songs (It's not considered a playlist by the api)
- [x] Integrate TidalMusic
- [ ] Handle TidalMusic's liked songs (It's not considered a playlist by the api)
- [ ] ~Add Applemusic to the mix~ On hold since [apple-music-python](https://github.com/mpalazzolo/apple-music-python] has no write features, will attempt to bypass with cookies
- [ ] Add Deezer?
