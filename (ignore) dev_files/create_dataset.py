import pandas as pd

df = pd.read_csv('datasets/tracks_features.csv')
df[:10000].to_csv('datasets/tracks_features_medium.csv')