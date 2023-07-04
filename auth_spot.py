import os
import spotipy, time
from flask import session, url_for
from spotipy.oauth2 import SpotifyOAuth
from dotenv import load_dotenv

load_dotenv()

CLIENT_ID = os.getenv('SPOTIFY_ID')
CLIENT_SECRET = os.getenv('SPOTIFY_SECRET')

def time_track(ms):
    seconds, ms = divmod(ms, 1000)
    minutes, seconds = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)
    if hours < 1:
        return f'{int(minutes):01d}:{int(seconds):02d}'
    else:
        return f'{int(hours):1d}:{int(minutes):01d}:{int(seconds):02d}'
    

def time_play(ms):
    seconds, ms = divmod(ms, 1000)
    minutes, seconds = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)
    if hours < 1:
        return f'{int(minutes):01d}m {int(seconds):02d}s'
    else:
        return f'{int(hours):1d}h {int(minutes):01d}m'


def get_token():
    token_info = session.get('spot_token_info', None)
    if not token_info:
        raise 'exception'
    
    now = int(time.time())
    if token_info['expires_at'] - now < 60:
        sp_oauth =  create_spotify_oauth()
        token_info = sp_oauth.refresh_access_token(token_info['refresh-token'])
    
    return token_info


def get_spotify_user():
    try:
        token_info = get_token()
    except:
        return None
    return  spotipy.Spotify(auth=token_info['access_token'])
     

def create_spotify_oauth():
    return SpotifyOAuth(
                client_id=CLIENT_ID,
                client_secret=CLIENT_SECRET,
                redirect_uri=url_for('redirectSpotify', _external=True),
                scope='playlist-read-private playlist-modify-private playlist-modify-public')