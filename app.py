from flask import Flask, request, render_template, redirect, jsonify, url_for, session, flash
from flask_session import Session
from init import *
from scrape_news import *
from datetime import datetime
from werkzeug.security import generate_password_hash
import re
from api_functions import *

app = Flask(__name__)

app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

app.jinja_env.filters["convert_time"] = convert_time

@app.route("/")
def index():
    session.clear()
    top_news = get_news(3)
    return render_template("index.html", top_news=top_news)

@app.route("/login")
def login():
    auth_url = get_auth_url()
    return redirect(auth_url)

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

# refine this to have error messaging on the same page/div
@app.route("/mailing_list_signup", methods=["POST"])
def mailing_list_signup():
    email_address = request.form.get("email_address")
    latitude = request.form.get("latitude")
    longitude = request.form.get("longitude")

    if not email_address:
        return jsonify({"message": "must provide email address"}), 400
    if not re.match(r"[^@]+@[^@]+\.[^@]+", email_address):
        return jsonify({"message": "please enter a proper email address"}), 400

    coords = [latitude, longitude]
    user_message = add_to_mailing_list(email_address, coords)
    email_user(email_address, coords)
    return redirect('/')

@app.route('/terms_and_conditions')
def terms_and_conditions():
    return render_template("terms-and-conditions.html")

@app.route('/music_news')
def music_news():
    top_news = get_news(100)
    return render_template('music_news.html', top_news=top_news)

@app.route('/user_music_news')
@login_required
def logged_music_news():
    _, current_track = check_token()
    top_news = get_news(100)
    return render_template('user_music_news.html', top_news=top_news, current_track=current_track)

@app.route("/callback")
def callback():
    if 'error' in request.args:
        return jsonify({"error": request.args['error']})
    
    # going to request an access token here
    if 'code' in request.args:
        token_info = get_token_info(request.args['code'])
        session['access_token'] = token_info['access_token']
        session['refresh_token'] = token_info['refresh_token']
        session['expires_at'] = token_info['expires_in'] + datetime.now().timestamp()
        
        headers = {
            'Authorization' : f"Bearer {session['access_token']}"
        }
        session['user_id'] = get_user_id(headers)
        return redirect('/tracks')
        
    
    return redirect('/')

def check_token():
    if 'access_token' not in session:
        return None, redirect('/login' if 'access_token' not in session else '/refresh-token')

    if datetime.now().timestamp() > session['expires_at']:
        return redirect('/refresh-token')
    
    headers = {
        'Authorization' : f"Bearer {session['access_token']}"
    }
    try:
        track_id = get_current_track(headers)['item']['id']
    except:
        track_id = get_recently_played(headers)['items'][0]['track']['id']
    current_track = f"https://open.spotify.com/embed/track/{track_id}"

    return headers, current_track

# ---------- JS ROUTES ----------
@app.route('/current-track')
def current_track():
    _, current_track = check_token()
    return jsonify({'embed_url' : current_track})

@app.route('/recently-played')
def recently_played():
    headers, _ = check_token()
    return jsonify(get_recently_played(headers))

@app.route('/fav-tracks-short-term')
def fav_tracks_route_short():
    headers, _ = check_token()
    return jsonify(get_top_items(headers, 'short_term', 'tracks'))

@app.route('/fav-tracks-medium-term')
def fav_tracks_medium():
    headers, _ = check_token()
    return jsonify(get_top_items(headers, 'medium_term', 'tracks'))

@app.route('/fav-tracks-long-term')
def fav_tracks_route_long():
    headers, _ = check_token()
    return jsonify(get_top_items(headers, 'long_term', 'tracks'))

@app.route('/fav-artists-short-term')
def fav_artists_short():
    headers, _ = check_token()
    return jsonify(get_top_items(headers, 'short_term', 'artists'))

@app.route('/fav-artists-medium-term')
def fav_artist_medium():
    headers, _ = check_token()
    return jsonify(get_top_items(headers, 'medium_term', 'artists'))

@app.route('/fav-artists-long-term')
def fav_artists_long():
    headers, _ = check_token()
    return jsonify(get_top_items(headers, 'long_term', 'artists'))


# ---------- PAGES ----------

@app.route('/account')
@login_required
def account():
    headers, current_track = check_token()
    account = get_account_info(headers)
    return render_template("account.html", account=account)

@app.route('/tracks')
@login_required
def tracks():
    headers, current_track = check_token()
    fav_tracks = get_top_items(headers, 'short_term', 'tracks')['items']
    return render_template('tracks.html', fav_tracks=fav_tracks, current_track=current_track)

@app.route('/artists')
@login_required
def artists():
    headers, current_track = check_token()
    fav_artists = get_top_items(headers, 'short_term', 'artists')['items']
    return render_template('artists.html', fav_artists=fav_artists, current_track=current_track)


@app.route('/playlists')
@login_required
def playlists():
    headers, current_track = check_token()
    playlists = {
        'short_term_rec' : rec_top_item_playlist(headers, 'short_term', 'Top Tracks From the Past 4 Weeks'),
        'medium_term_rec' : rec_top_item_playlist(headers, 'medium_term', 'Top Tracks From the Past 6 Months'),
        'long_term_rec' : rec_top_item_playlist(headers, 'long_term', 'Top Tracks From the Past Year'),
        'ai_short_term_rec' : rec_feature_playlist(headers, 'short_term', 'Similar Songs From the Past 4 Weeks'),
        'ai_medium_term_rec' : rec_feature_playlist(headers, 'medium_term', 'Similar Songs From the Past 6 Months'),
        'ai_long_term_rec' : rec_feature_playlist(headers, 'long_term', 'Similar Songs From the Past Year')
    }
    return render_template('playlists.html', playlists=playlists, current_track=current_track)

@app.route('/history')
@login_required
def history():
    headers, current_track = check_token()
    recently_played = get_recently_played(headers)['items']
    return render_template('history.html', recently_played=recently_played, current_track=current_track)

@app.route('/library')
@login_required
def library():
    headers, current_track = check_token()
    user_playlists = get_user_playlists(headers)['items']
    user_audiobooks = get_audiobooks(headers)['items']
    user_shows = get_shows(headers)['items']
    user_episodes = get_episodes(headers)['items']
    
    return render_template('library.html', user_playlists=user_playlists, user_audiobooks=user_audiobooks, user_shows=user_shows, user_episodes=user_episodes, current_track=current_track)

@app.route('/json_current_playlist')
def json_current_playlist():
    headers, _ = check_token()
    user_playlists = get_user_playlists(headers)['items']
    reduced = [{'id': p['id'], 'name': p['name']} for p in user_playlists]
    return jsonify(reduced)

@app.route('/mailing_list')
def mailing_list():
    _, current_track = check_token()
    return render_template('mailing_list.html', current_track=current_track)


# ---------- PAGES END ----------
@app.route('/refresh-token')
def refresh_token():
    if 'refresh_token' not in session:
        return redirect('/login')
    
    # checking if access token is expired
    if datetime.now().timestamp() > session['expires_at']:
        new_token_info = custom_refresh_token(session['refresh_token'])

        session['access_token'] = new_token_info['access_token']
        session['expires_at'] = new_token_info['expires_in'] + datetime.now().timestamp()

        return redirect('/tracks')
    
if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
