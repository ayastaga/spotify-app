import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.preprocessing import StandardScaler
import numpy as np


df = pd.read_csv('datasets/tracks_features_medium.csv')


# extract featuresa and clean them up
features = ['danceability', 'energy', 'loudness', 'mode', 'speechiness', 'acousticness', 'instrumentalness', 'liveness', 'valence']
X = df[features]
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

# calculate cosine similarity matrix
cos_sim = cosine_similarity(X_scaled)

# Pick a song index (e.g., the 10th song) and get its top 5 similar songs
song_index = 23 # $$ iterate this through every song $$
similarities = cos_sim[song_index]
top_indices = np.argsort(similarities)[::-1][1:6]  # exclude itself

# Show top similar songs
recommended_songs = df.iloc[top_indices]
#print(recommended_songs[['name', 'artists']])


# 1. extract user's top 100 songs
# 2. look up the songs in the 1.2 million dataset, and if found, use the top 10 for recommendation
# 3. for each of the top 10, recommend 5 similar songs by calling ai_function