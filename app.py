from flask import Flask, request, session, redirect, render_template, flash
from flask_session import Session
from auth_spot import create_spotify_oauth, get_spotify_user, time_play, time_track

app = Flask(__name__)
app.jinja_env.filters["track_time"] = time_track
app.jinja_env.filters["play_time"] = time_play

app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)


@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/spotify_playlists')
def sp_playlist():
    sp = get_spotify_user()  
    if not sp:
        flash('Spotify account authorization needed!')
        return redirect('/')
    
    playlists = []

    for list in sp.current_user_playlists()['items']:
        playlist = {'id': list['id'], 'name': list['name'],'description': list['description'] 
                    ,'image': sp.playlist_cover_image(list['id'])[0]['url'], 'count': list['tracks']['total']}
        playlists.append(playlist)

    return render_template('playlist.html', playlists=playlists)

@app.route('/authspotify')
def authspotify():
    sp_oauth = create_spotify_oauth()
    auth_url = sp_oauth.get_authorize_url()
    return redirect(auth_url)


@app.route('/redirect')
def redirectPage():
    sp_oauth = create_spotify_oauth()
    code = request.args.get('code')
    session['spot_token_info'] = sp_oauth.get_access_token(code)
    return redirect('/')
    

@app.route('/auth')
def auth():
    spot_auth = session.get('spot_token_info', None) != None
    yt_auth = session.get('yt_token_info', None) != None
    return render_template('auth.html', spot_auth=spot_auth, yt_auth=yt_auth)

@app.route('/view')
def view():
    sp = get_spotify_user()
    if not sp:
        flash('Spotify account authorization needed')
        return redirect('/auth')
    
    playlist_id =  request.args.get('playlist_id')
    name = request.args.get('name')
    req = sp.playlist_items(playlist_id=playlist_id, fields='items.track(name, duration_ms, preview_url, artists(name))')['items']
    playlist = []
    time = 0
    for item in req:
        track = item.get('track')
        if not track:
            continue
        time += track['duration_ms']
        song = {'name': track['name'], 'duration': track['duration_ms'], 'url': track['preview_url']}
        artists = []
        for artist in track['artists']:
            artists.append(artist['name'])
            
        song['artists'] = ', '.join(artists)
        playlist.append(song)

    return render_template("view.html", playlist=playlist, name=name, time=time)


@app.route('/delete')
def delete():
    sp = get_spotify_user()
    if not sp:
        flash('Spotify account authorization needed')
        return redirect('/auth')
    
    playlist_id = request.args.get('playlist_id')
    sp.current_user_unfollow_playlist(playlist_id=playlist_id)

    return redirect('/')

@app.route('/disconnect')
def disconnect():
    dis = request.args.get('disconnect')
    if dis == 'Spotify':
        session['spot_token_info'] = None
    elif dis == 'YouTube':
        session['yt_token_info'] = None

    flash(f'Successfully disconnected from {dis}!')
    return redirect('/')





