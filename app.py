import os
from flask import Flask, request, redirect, session, jsonify, render_template, url_for, flash
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import requests
from dotenv import load_dotenv
import sqlite3
import pandas as pd
from datetime import datetime, timedelta
import json

# Load environment variables
load_dotenv()

# Create Flask app
app = Flask(__name__)

# Configure app for Vercel deployment
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'your-secret-key-here')

# Spotify API credentials
SPOTIFY_CLIENT_ID = os.environ.get('SPOTIFY_CLIENT_ID')
SPOTIFY_CLIENT_SECRET = os.environ.get('SPOTIFY_CLIENT_SECRET')
SPOTIFY_REDIRECT_URI = os.environ.get('SPOTIFY_REDIRECT_URI', 'https://your-app.vercel.app/callback')

# Spotify OAuth configuration
SCOPE = 'user-read-private user-read-email user-top-read user-read-recently-played playlist-read-private user-library-read user-read-currently-playing user-read-playback-state'

def create_spotify_oauth():
    return SpotifyOAuth(
        client_id=SPOTIFY_CLIENT_ID,
        client_secret=SPOTIFY_CLIENT_SECRET,
        redirect_uri=SPOTIFY_REDIRECT_URI,
        scope=SCOPE,
        show_dialog=True
    )

def get_token():
    token_info = session.get('token_info')
    if not token_info:
        return None
    
    now = int(datetime.now().timestamp())
    is_expired = token_info['expires_at'] - now < 60
    
    if is_expired:
        sp_oauth = create_spotify_oauth()
        token_info = sp_oauth.refresh_access_token(token_info['refresh_token'])
        session['token_info'] = token_info
    
    return token_info

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login')
def login():
    sp_oauth = create_spotify_oauth()
    auth_url = sp_oauth.get_authorize_url()
    return redirect(auth_url)

@app.route('/callback')
def callback():
    sp_oauth = create_spotify_oauth()
    session.clear()
    code = request.args.get('code')
    
    if not code:
        return redirect(url_for('index'))
    
    token_info = sp_oauth.get_access_token(code)
    session['token_info'] = token_info
    
    return redirect(url_for('dashboard'))

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

@app.route('/dashboard')
def dashboard():
    token_info = get_token()
    if not token_info:
        return redirect(url_for('login'))
    
    sp = spotipy.Spotify(auth=token_info['access_token'])
    
    try:
        user_info = sp.current_user()
        return render_template('dashboard.html', user=user_info)
    except Exception as e:
        flash(f'Error loading dashboard: {str(e)}', 'error')
        return redirect(url_for('index'))

@app.route('/top-tracks')
def top_tracks():
    token_info = get_token()
    if not token_info:
        return redirect(url_for('login'))
    
    sp = spotipy.Spotify(auth=token_info['access_token'])
    time_range = request.args.get('time_range', 'medium_term')
    
    try:
        top_tracks = sp.current_user_top_tracks(time_range=time_range, limit=20)
        return render_template('top_tracks.html', tracks=top_tracks['items'], time_range=time_range)
    except Exception as e:
        flash(f'Error loading top tracks: {str(e)}', 'error')
        return redirect(url_for('dashboard'))

@app.route('/top-artists')
def top_artists():
    token_info = get_token()
    if not token_info:
        return redirect(url_for('login'))
    
    sp = spotipy.Spotify(auth=token_info['access_token'])
    time_range = request.args.get('time_range', 'medium_term')
    
    try:
        top_artists = sp.current_user_top_artists(time_range=time_range, limit=20)
        return render_template('top_artists.html', artists=top_artists['items'], time_range=time_range)
    except Exception as e:
        flash(f'Error loading top artists: {str(e)}', 'error')
        return redirect(url_for('dashboard'))

@app.route('/playlists')
def playlists():
    token_info = get_token()
    if not token_info:
        return redirect(url_for('login'))
    
    sp = spotipy.Spotify(auth=token_info['access_token'])
    
    try:
        playlists = sp.current_user_playlists()
        return render_template('playlists.html', playlists=playlists['items'])
    except Exception as e:
        flash(f'Error loading playlists: {str(e)}', 'error')
        return redirect(url_for('dashboard'))

@app.route('/recently-played')
def recently_played():
    token_info = get_token()
    if not token_info:
        return redirect(url_for('login'))
    
    sp = spotipy.Spotify(auth=token_info['access_token'])
    
    try:
        recent_tracks = sp.current_user_recently_played(limit=50)
        return render_template('recently_played.html', tracks=recent_tracks['items'])
    except Exception as e:
        flash(f'Error loading recently played tracks: {str(e)}', 'error')
        return redirect(url_for('dashboard'))

@app.route('/recommendations')
def recommendations():
    token_info = get_token()
    if not token_info:
        return redirect(url_for('login'))
    
    sp = spotipy.Spotify(auth=token_info['access_token'])
    
    try:
        # Get user's top tracks for seed tracks
        top_tracks = sp.current_user_top_tracks(limit=5, time_range='short_term')
        seed_tracks = [track['id'] for track in top_tracks['items']]
        
        # Get recommendations
        recommendations = sp.recommendations(seed_tracks=seed_tracks[:5], limit=20)
        return render_template('recommendations.html', tracks=recommendations['tracks'])
    except Exception as e:
        flash(f'Error loading recommendations: {str(e)}', 'error')
        return redirect(url_for('dashboard'))

@app.route('/profile')
def profile():
    token_info = get_token()
    if not token_info:
        return redirect(url_for('login'))
    
    sp = spotipy.Spotify(auth=token_info['access_token'])
    
    try:
        user_info = sp.current_user()
        return render_template('profile.html', user=user_info)
    except Exception as e:
        flash(f'Error loading profile: {str(e)}', 'error')
        return redirect(url_for('dashboard'))

@app.route('/api/health')
def health_check():
    return jsonify({'status': 'healthy', 'timestamp': datetime.now().isoformat()})

# Error handlers
@app.errorhandler(404)
def not_found(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    return render_template('500.html'), 500

# For Vercel deployment
if __name__ == '__main__':
    app.run(debug=False)

# Export the Flask app for Vercel
app = app
