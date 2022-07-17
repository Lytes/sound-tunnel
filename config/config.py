# Client_ID and Client_secret from Spotify Developers Dashboard
CLIENT_ID = ""
CLIENT_SECRET = ""

# Option 1
# REDIRECT_URI can be set to localhost
# the spotipy module should automatically get the access code by setting up a simple server at specified port
#
# Option 2
# REDIRECT_URI can be set to a random website (make sure it's a nonexistent website else the website's owner
# will probably see your access code in their logs, not a smart move)
# 
# MAKE SURE THE SAME REDIRECT URI SET HERE IS ALSO SET ON YOUR SPOTIPY DASHBOARD
REDIRECT_URI = "http://localhost:9000/callback/"

# The permissions needed to access all your spotify playlists
SCOPE = "playlist-read-collaborative playlist-read-private user-library-read playlist-modify-private"

# File containing your youtubemusic cookies
ytfile = ".creds/headers_auth.json"

# File containing your tidal cookies
tidalfile = ".creds/creds_auth.txt"

# File containing your applemusic cookies
applefile = ".creds/i_auth.txt"
