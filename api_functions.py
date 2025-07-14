import os
from dotenv import load_dotenv
import urllib.parse
from dotenv import load_dotenv
from base64 import b64encode
import sqlite3
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.preprocessing import StandardScaler
from playlist_ai import cos_sim
from datetime import datetime
import tzlocal
from zoneinfo import ZoneInfo
import requests
from bs4 import BeautifulSoup
import nlpcloud
from flask import redirect, render_template, session
from functools import wraps
from email.message import EmailMessage
import ssl
import smtplib


# environment variables
load_dotenv()
CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")

# urls
REDIRECT_URI = 'http://127.0.0.1:5000/callback'
AUTH_URL = 'https://accounts.spotify.com/authorize'
TOKEN_URL = 'https://accounts.spotify.com/api/token'
API_BASE_URL = 'https://api.spotify.com/v1/'

# load in database
con = sqlite3.connect("spotify_data.db", check_same_thread=False)
cur = con.cursor()

con_2 = sqlite3.connect('music_news.db', check_same_thread=False)
cur_2 = con_2.cursor()

def convert_time(iso_string):
    local_tz = tzlocal.get_localzone_name()
    dt_utc = datetime.fromisoformat(iso_string.replace('Z', '+00:00'))
    local_dt = dt_utc.astimezone(ZoneInfo(local_tz))
    return local_dt.strftime("%B %d, %Y @ %I:%M %p").lstrip("0").replace(" 0", " ")


def apology(message, code=400):
    """Render message as an apology to user."""

    def escape(s):
        """
        Escape special characters.

        https://github.com/jacebrowning/memegen#special-characters
        """
        for old, new in [
            ("-", "--"),
            (" ", "-"),
            ("_", "__"),
            ("?", "~q"),
            ("%", "~p"),
            ("#", "~h"),
            ("/", "~s"),
            ('"', "''"),
        ]:
            s = s.replace(old, new)
        return s

    return render_template("error.html", top=code, bottom=escape(message)), code


def get_auth_url():
    scope = '' \
    'user-read-private ' \
    'user-read-email ' \
    'user-top-read ' \
    'user-library-read ' \
    'user-read-currently-playing ' \
    'user-read-playback-state ' \
    'user-read-recently-played ' \
    'playlist-read-private ' \
    'playlist-modify-public ' \
    'playlist-modify-private ' \
    'user-read-playback-position ' \
    'user-modify-playback-state' 

    params = {
        'client_id' : CLIENT_ID,
        'response_type': 'code',
        'scope' : scope,
        'redirect_uri' : REDIRECT_URI,
        'show_dialog' : True # FOR TESTING!! forces us to login every time
    }
    auth_url = f"{AUTH_URL}?{urllib.parse.urlencode(params)}"
    return auth_url


def get_token_info(code):
    request_body = {
        'code': code,
        'redirect_uri' : REDIRECT_URI,
        'grant_type' : 'authorization_code',
    }

    auth_string = CLIENT_ID + ":" + CLIENT_SECRET
    auth_bytes = auth_string.encode() # defaults to utf-8
    auth_base64 = str(b64encode(auth_bytes), "utf-8")
    headers = {
        "Authorization": "Basic " + auth_base64,
        "Content-Type": "application/x-www-form-urlencoded"
    }
    response = requests.post(TOKEN_URL, headers=headers, data=request_body)
    return response.json()


def custom_refresh_token(new_token):
    request_body = {
        'grant_type' : 'refresh_token',
        'refresh_token' : new_token,
        'client_id' : CLIENT_ID, 
        'client_secret' : CLIENT_SECRET
    }
    response = requests.post(TOKEN_URL, data=request_body)
    new_token_info = response.json()
    return new_token_info

def get_user_id(headers):
    response = requests.get(API_BASE_URL + "me", headers=headers)
    try:
        return response.json()['id']
    except:
        return None

def login_required(f):
    """
    Decorate routes to require login.

    https://flask.palletsprojects.com/en/latest/patterns/viewdecorators/
    """

    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)

    return decorated_function


# ---- GET REQUESTS TO API ----
def get_account_info(headers):
    response = requests.get(API_BASE_URL + 'me', headers=headers)
    return response.json()

def get_current_track(headers):
    response = requests.get(API_BASE_URL + 'me/player/currently-playing', headers=headers)
    return response.json()

# MAX LIMIT = 50 TRACKS
def get_top_items(headers, term, content_type, *args):
    if len(args) == 0:
        response = requests.get(API_BASE_URL + f'me/top/{content_type}?time_range={term}', headers=headers)
    else:
        response = requests.get(API_BASE_URL + f'me/top/{content_type}?time_range={term}&limit={args[0]}', headers=headers)
    return response.json()


# !!!! YIELDS FORBIDDEN 403 ERROR, JUST IGNORE IT 
def get_queued_tracks(headers):
    response = requests.get(API_BASE_URL + 'me/player/queue', headers=headers)
    return response.json()


def get_recently_played(headers):
    response = requests.get(API_BASE_URL + 'me/player/recently-played?limit=50', headers=headers)
    return response.json()


def get_user_playlists(headers):
    response = requests.get(API_BASE_URL + 'me/playlists', headers=headers)
    return response.json()


def get_audiobooks(headers):
    response = requests.get(API_BASE_URL + 'me/audiobooks', headers=headers)
    return response.json()


def get_episodes(headers):
    response = requests.get(API_BASE_URL + 'me/episodes', headers=headers)
    return response.json()


def get_shows(headers):
    response = requests.get(API_BASE_URL + 'me/shows', headers=headers)
    return response.json()


def get_wikipedia_about(fav_artists):
    wiki_about = []
    for artist in fav_artists:
        name = artist['name']
        url = f"https://en.wikipedia.org/wiki/{name.replace(' ', '_')}"
        response = requests.get(url)
        
        if response.status_code != 200:
            wiki_about.append('No info found...')
        
        soup = BeautifulSoup(response.text, 'html.parser')
        paragraphs = soup.select('p')  # First paragraphs after infobox
        
        for para in paragraphs:
            text = para.get_text().strip()
            if text:  # Skip empty paragraphs
                client = nlpcloud.Client("bart-large-cnn", "378c152ef2478d5db238e96a125c1b01e703220f")
                try:
                    server_call = client.summarization(text)
                    wiki_about.append(server_call['summary_text'])
                except Exception as e:
                    print(e)
                    wiki_about.append("Too many server requests")

    return wiki_about


def resume_playback(headers):
    headers['Content-Type'] = 'application/json'
    data = {
        'offset' : {
            'position' : 0
        },
        'position_ms' : 0
    }
    response = requests.put(API_BASE_URL + 'me/player/play', headers=headers, json=data)
    return response.json()


def playlist_checker(headers, title):
    current_library = get_user_playlists(headers)['items']
    current_library_names = []
    for x in current_library:
        current_library_names.append(x['name'])

    headers['Content-Type'] = 'application/json'
    playlist_id = ''

    #  or playlist['name'] == 'Top Tracks From the Past 6 Months' or playlist['name'] == 'Top Tracks From the Past Year':
    if title in current_library_names: # remove items from that playlist
        # find the playlist id
        for playlist in current_library:
            if playlist['name'] == title:
                playlist_id = playlist['id']
                break
        
        # get items
        response = requests.get(API_BASE_URL + f'playlists/{playlist_id}/tracks', headers=headers).json()
        track_list = response.get('items', [])
        
        # create a list with each track uri
        playlist_items = []
        for track in track_list:
            track_data = track.get('track')
            if track_data and 'uri' in track_data:
                playlist_items.append({'uri' : track['track']['uri']})

        if playlist_items:
            # create data list
            data = {
                'tracks' : playlist_items,
                'snapshot_id' : playlist['snapshot_id']
            }
            
            # deletes tracks
            delete_response = requests.delete(API_BASE_URL + f'playlists/{playlist_id}/tracks', headers=headers, json=data)
        else:
            print("no tracks found to delete")
    else:
        # get current user id
        current_user_id = get_account_info(headers)['id']

        # change header info
        headers['Content-Type'] = 'application/json'

        # data
        data = {
            'name' : title,
            'description' : 'Playlist containing 100 of your top tracks from the past 4 weeks',
            'public' : False
        }

        # create playlist with that name
        response = requests.post(API_BASE_URL + f'users/{current_user_id}/playlists', headers=headers, json=data)
        playlist_id = response.json()['id']

    return playlist_id


# short term title = 'Top Tracks From the Past 4 Weeks'
def rec_top_item_playlist(headers, term, title):

    # checks if playlist exists or creates one
    playlist_id = playlist_checker(headers, title)

    # get top 100 tracks from past 4 weeks
    headers.pop('Content-Type', None)
    fav_short_tracks = get_top_items(headers, term, 'tracks', 20)['items']
    
    # add items requests pre-requisties 
    headers['Content-Type'] = 'application/json'
    uri_list = []
    for track in fav_short_tracks:
        uri_list.append(f'spotify:track:{track["id"]}')

    data = {
        'uris' : uri_list,
        'position' : 0
    }

    # adds items to the playlist
    requests.post(API_BASE_URL + f'playlists/{playlist_id}/tracks', headers=headers, json=data)

    # return that playlist's id for embed
    return playlist_id

# playlist with their fav artists (5 songs randomly picked from each of their discography)
def rec_feature_playlist(headers, term, title):
    # 1. extract user's top 100 songs
    fav_tracks = get_top_items(headers, term, 'tracks', 50)['items']
    
    # 2. get track id of each track
    track_ids = [track['id'] for track in fav_tracks]

    # 3. look up the songs in the music_data database
    placeholders = ','.join(['?'] * len(track_ids))
    rows = cur.execute(f'SELECT * FROM music_data WHERE id IN ({placeholders})', track_ids).fetchall()
    
    # 4. call ai function to find suggestions
    rec_set = []
    for row in rows:
        rec_set.append(cos_sim(row[0]))
    
    # 5. create a playlist using those suggestions
    # check if playlist exists already and does according stuff
    playlist_id = playlist_checker(headers, title)

    # format data for request
    headers['Content-Type'] = 'application/json'
    uri_list = []
    for song_set in rec_set:
        for song in song_set:
            uri_list.append(f'spotify:track:{song[0]}')
    data = {
        'uris' : uri_list,
        'position' : 0
    }

    # adds items to the playlist
    requests.post(API_BASE_URL + f'playlists/{playlist_id}/tracks', headers=headers, json=data)

    # return that playlist's id for embed
    return playlist_id

def add_to_mailing_list(email_address, password):
    try:
        rows = cur.execute("SELECT * FROM mailing_list WHERE email_address = ?", (email_address, )).fetchall()

        if rows:
            return "EXISTS"
        
        # insert new entry
        cur.execute("INSERT INTO mailing_list (email_address, hash) VALUES (?, ?)", (email_address, password))
        con.commit()

    except Exception as e:
        print(e)
        try:
            print(cur.execute("SELECT * FROM mailing_list").fetchall())
        except Exception as e:
            print(e)
    
    try:
        print(cur.execute("SELECT * FROM mailing_list").fetchall())
    except Exception as e:
        print(e)
    
    return "ADDED"

# NEED TO IMPLEMENT AN EMAIL AUTOMATION SYSTEM WHICH SUGGESTS SHOWS NEARBY
def email_user(email_address, coords):
    email_sender = 'ayavasu@gmail.com'
    subject = 'Thank you for signing up to Ecoute!'
    body = """
    We here at Ecoute just wanted to thank you for signing up!
    In the coming weeks you can expect news letters and the sort so stay tuned! 

    Sincerely,
    ayxstaga from Ecoute
    """
    em = EmailMessage()
    em['From'] = email_sender
    em['To'] = email_address
    em['Subject'] = subject
    em.set_content(body)
    context = ssl.create_default_context()

    with smtplib.SMTP_SSL('smtp.gmail.com', 465, context=context) as smtp:
        smtp.login(email_sender, EMAIL_PASSWORD)
        smtp.sendmail(email_sender, email_address, em.as_string())

def get_news(num):
    return cur_2.execute("SELECT * FROM music_news ORDER BY random() LIMIT ?", (num, )).fetchall()

def close_connection():
    con.close()
