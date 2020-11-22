
import json
import os
from urllib.parse import quote, urlencode
import re
import time

import spotipy
from dotenv import load_dotenv

load_dotenv()
CLIENT_ID = os.getenv('SPOTIPY_CLIENT_ID')
CLIENT_SECRET = os.getenv('SPOTIPY_CLIENT_SECRET')
from spotipy.oauth2 import SpotifyClientCredentials

client_credentials_manager = SpotifyClientCredentials(client_id=CLIENT_ID, client_secret=CLIENT_SECRET)
spotify = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

tracks = []

for i in range(10):
    with open(f'SpotifyData/FullHistory/MyData/endsong_{i}.json') as f:
        songs = json.load(f)
        tracks += songs
print(len(tracks))
unique_songs = list({v['master_metadata_track_name'] :v for v in tracks}.values())

unique_songs_len = len(unique_songs)
song_uris = []
keep_going = True
current_index = 0

while keep_going:
    song = unique_songs[current_index]
    res = spotify.search(q=f"{song['master_metadata_track_name']} {song['master_metadata_album_artist_name']}", type='track', limit=1)
    for r in res['tracks']['items']:
        if song['master_metadata_album_artist_name'] == r['artists'][0]['name'] and song['master_metadata_track_name'] == r['name']:
            song_uris.append(r['uri'])
            with open(f'SpotifyData/AllURIs.csv', 'a') as f:
                f.write(f'{r["uri"]}\n')
        else:
            current_index += 1
    if current_index == unique_songs_len - 1:
        break
    elif current_index == len(song_uris) - 1:
        # print(song)
        # print(res)
        if song['episode_name']:
            current_index += 1
            unique_songs_len -= 1
        if song['master_metadata_album_artist_name'] != r['artists'][0]['name'] or song['master_metadata_track_name'] != r['name']:
            current_index += 1
    else:
        current_index += 1
        print(song_uris[-1])
