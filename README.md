![Sound-tunnel gif](sound--tunnel.gif)
# Sound-tunnel
Python3 script to transfer playlists across Spotify, Tidal, AppleMusic and Youtube-Music

## Supported Platfrom
1. Youtube Music -> specify with `youtube`
2. Spotify -> specify with `spotify`
3. Tidal -> specify with `tidal`
4. Apple Music -> specify with `apple`

---
## Setup
### Requirements
1. Install dependencies using `pip install -r requirements.txt`

### Spotify
1. Generate a new app at [https://developer.spotify.com/dashboard/applications)](https://developer.spotify.com/dashboard/applications)
2. Fill the `redirect_uri` from [config.py](config/config.py) into the new app's settings
3. Fill in your `client_id` and `client_secret` from your Spotify app into [config.py](config/config.py) file 

### YouTubeMusic
1. Create the oauth.json file in the `.creds` folder
```sh
cd .creds && ytmusicapi oauth
```
> Ensure ytmusicapi location is added to PATH

### Tidal Music
1. Attempting to use Tidal will auto-set it up

### Apple Music
1. Open a new tab in browser
2. Open the developer tools (Ctrl-Shift-I) and select the “Network” tab
3. Go to [https://music.apple.com](https://music.apple.com) and ensure you are logged in
4. Find any authenticated POST request.
5. Copy out the value of the `authorization header` and `media-user-token` request headers
6. Create and paste copied values in `.creds/i_auth.txt` (Example structure in [.creds/i_auth.example.txt](.creds/i_auth.example.txt)).
   It should look something like this ![example image](./image_2.png "Example img")

---
## Commands
1. Display all flags with `python3 main.py --help`
2. Specify playlist source platform and destination platform with `--source`/`-s` and `--destination`/`-d` respectively
   - Specify Youtube Music -> specify with `youtube`
   - Spotify -> specify with `spotify`
   - Tidal -> specify with `tidal`
   - Apple Music -> specify with `apple`
3. Display user playlists for source platfrom using `-L` e.g Display tidal playlists with
```sh
python3 main.py --source tidal -L
```
4. Copy a playlist (specify name in stdin) from one platform to the other using `-p` e.g Copy my "1am drive" playlists from spotify to ytmusic
```sh
python3 main.py -s spotify -d youtube -p "1am drive"
```
5. Playlist names can be specified from a file with each playlist name occupying a line
```sh
python3 main.py --source spotify --destination youtube -P ./myplaylists.txt
```
6. Transfer all playlists from one platform to the other using `-p` e.g Transfer all playlists from spotify to ytmusic (this includes Spotify liked songs)
```sh
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
- [x] Add Applemusic to the mix
- [ ] Handle TidalMusic's liked songs (It's not considered a playlist by the api)
- [ ] Add Deezer?
