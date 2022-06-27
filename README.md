# sound-tunnel
Python3 script to transfer playlists back and forth between Spotify and Youtube-Music using [spotipy](https://github.com/plamere/spotipy) and [ytmusicapi](https://github.com/sigma67/ytmusicapi)

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
5. Paste copied cookies in [headers_auth.json](headers_auth.json). Should look something like this
![example image](./image.png "Example img")

### Commands
1. Display all flags with `python3 main.py --help`
2. Specify playlist source platform and destination platform with `--source` and `--destination` respectively
3. Display user playlists for source platfrom using `-S` e.g Display ytmusic playlists with
```
python3 main.py --source youtube -S
```
4. Copy a playlist (specify name in stdin) from one platform to the other using `-p` e.g Copy my "1am drive" playlists from spotify to ytmusic
```
python3 main.py --source spotify --destination youtube -p "1am drive"
```
5. Playlist names can be specified from a file with each playlist name occupying a line
```
python3 main.py --source spotify --destination youtube -P ./myplaylists.txt
```
6. Transfer user's spotify playlist to ytmusic... for some reason, spotify does not consider Liked Songs to be a playlist 
```
python3 main.py --source spotify --destination youtube -L
```
7. Transfer all playlists from one platform to the other using `-p` e.g Transfer all playlists from spotify to ytmusic (this includes Spotify liked songs)
```
python3 main.py --source spotify --destination youtube -A
```
---

### To-do
- [ ] Add YTmusic to Spotify transfer
- [ ] Add Applemusic to the mix
