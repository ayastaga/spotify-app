import sqlite3
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.preprocessing import StandardScaler
import numpy as np

# change this to whatever you want
database_name = 'tracks_features_medium.csv'

df = pd.read_csv(f'./datasets/{database_name}')
df['custom_index'] = df.index


con = sqlite3.connect("spotify_data.db", check_same_thread=False)
cur = con.cursor()


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
