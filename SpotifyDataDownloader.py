import json
import os
import re
import time
import spotipy
import tqdm as tqdm
from dotenv import load_dotenv

load_dotenv()
CLIENT_ID = os.getenv('SPOTIPY_CLIENT_ID')
CLIENT_SECRET = os.getenv('SPOTIPY_CLIENT_SECRET')
from spotipy.oauth2 import SpotifyClientCredentials

client_credentials_manager = SpotifyClientCredentials(client_id=CLIENT_ID, client_secret=CLIENT_SECRET)
spotify = spotipy.Spotify(client_credentials_manager=client_credentials_manager)


def search_for_tracks(item):
    tracks_found = []
    if isinstance(item, list):
        found = _list_search(item)
        if found:
            tracks_found += found
    if isinstance(item, dict):
        found = _dict_search(item)
        if found:
            tracks_found += found
    return tracks_found


def _list_search(l):
    tracks_found = []
    for item in l:
        found = search_for_tracks(item)
        if found:
            tracks_found += found
    return tracks_found


def _dict_search(o):
    tracks_found = []
    for key in o:
        if isinstance(o[key], list):
            search_for_tracks(o[key])
        else:
            if isinstance(o[key], str) and re.search('spotify:track', o[key]):
                tracks_found.append(o[key])
    return tracks_found


if __name__ == '__main__':

    with open('SpotifyData/AllURIs.csv') as f:
        song_uris_unique = f.read().split()

    batch_size = 50

    batches, partial_batch = divmod(len(song_uris_unique), batch_size)
    if partial_batch:
        batches += 1
    progress_bar = tqdm.tqdm(range(batches), total=batches)
    for i in progress_bar:
        progress_bar.write(f'Batch: {i}, Folder: {i % 15}')
        try:
            current_batch = song_uris_unique[i * batch_size:(i + 1) * batch_size]
        except IndexError:
            current_batch = song_uris_unique[(i - 1) * batch_size:-1]
        r = spotify.tracks(current_batch)
        f = spotify.audio_features(current_batch)
        results = r['tracks']
        features = f

        full_song_information_list = []
        for result, feature in zip(results, features):
            full_song_information = {
                'track_information': {},
                'track_features': {}
            }
            for rkey in result:
                full_song_information['track_information'][rkey] = result[rkey]
            for fkey in feature:
                full_song_information['track_features'][fkey] = feature[fkey]
            full_song_information_list.append(full_song_information)

        with open(f'SpotifyData/CombinedData/FullSongInformation_{i % 15}.json', 'a') as f:
            f.write(json.dumps(full_song_information_list, indent=2))

        time.sleep(1)
