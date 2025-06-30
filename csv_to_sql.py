import sqlite3
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.preprocessing import StandardScaler
import numpy as np


database_name = 'tracks_features.csv'
df = pd.read_csv(f'datasets/{database_name}')
df['custom_index'] = df.index


con = sqlite3.connect("spotify_data.db", check_same_thread=False)
cur = con.cursor()


'''
# MAILING LIST DATABASE
try:
    cur.execute("CREATE TABLE mailing_list (id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, email_address TEXT NOT NULL, hash TEXT NOT NULL)")
    cur.execute("CREATE UNIQUE INDEX email_address ON mailing_list (email_address)")
except Exception as e:
    print(f"\n\n{e}\n\n")


# MUSIC DATA DATABASE
try:
    cur.execute("CREATE TABLE music_data (custom_index INTEGER, id INTEGER, name TEXT, album TEXT, album_id TEXT, artists ARRAY, artist_ids ARRAY, track_number INTEGER, disc_number INTEGER, explicit BOOLEAN, danceability REAL, energy REAL, key INTEGER, loudness REAL, mode INTEGER, speechiness REAL, acousticness REAL, instrumentalness REAL, liveness REAL, valence REAL, tempo REAL, duration_ms INTEGER, time_signature REAL, year INTEGER, release_date TEXT)")

    data = []
    for _, row in df.iterrows():
        data.append((
            row['custom_index'],
            row['id'], # 0
            row['name'], # 1
            row['album'], # 2
            row['album_id'], # 3
            row['artists'], # 4
            row['artist_ids'], # 5
            row['track_number'], # 6
            row['disc_number'], # 7
            row['explicit'], # 8
            row['danceability'], # 9
            row['energy'], # 10
            row['key'], # 11
            row['loudness'], # 12
            row['mode'], # 13
            row['speechiness'], # 14
            row['acousticness'], # 15
            row['instrumentalness'], # 16
            row['liveness'], # 17
            row['valence'], # 18
            row['tempo'], # 19
            row['duration_ms'], # 19
            row['time_signature'], # 20
            row['year'], # 21
            row['release_date'] # 22
        ))

    cur.executemany("""
        INSERT INTO music_data (
            custom_index, id, name, album, album_id, artists, artist_ids, track_number, disc_number, explicit,
            danceability, energy, key, loudness, mode, speechiness, acousticness,
            instrumentalness, liveness, valence, tempo, duration_ms, time_signature,
            year, release_date
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, data)
    con.commit()
except Exception as e:
    print(f"\n\n{e}\n\n")
'''

# --------------------------------------------------------
features = ['danceability', 'energy', 'loudness', 'mode', 'speechiness',
            'acousticness', 'instrumentalness', 'liveness', 'valence']

query = f"SELECT {', '.join(features)} FROM music_data"
df_features = pd.read_sql_query(query, con)

# Drop rows with missing values just in case
df_features.dropna(inplace=True)

# === Step 3: Scale features and compute cosine similarity ===
scaler = StandardScaler()
X_scaled = scaler.fit_transform(df_features)


def cos_sim(song_index, top_n = 5):
    parent_vector = X_scaled[song_index:song_index+1]  # shape: (1, num_features)
    
    # Compute similarity only between the parent and all others
    similarities = cosine_similarity(X_scaled, parent_vector).flatten()  # shape: (num_songs,)

    # Get indices of top N most similar songs excluding itself
    top_indices = np.argsort(similarities)[::-1]
    top_indices = top_indices[top_indices != song_index][:top_n]  # exclude the song itself

    # Return DataFrame of top similar songs
    return df.iloc[top_indices].values.tolist()


