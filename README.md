# ECOUTE

This is a web application designed for music-junkies who love to know _everything_ about their music. Within this website, you can login (done by usign uAuth2.0), after which you can see your:

- Top artists (4 weeks, 6 months, 1 year)
- Top tracks (4 weeks, 6 months, 1 year)
- Your current playlists
- Your current audiobooks
- Your current shows
- Your recently played tracks
- Your spotify account
- All different types of news related to spotify

In addition to this, you can also sign up to our **mailing list**, where you will be recommended upcomig local shows near you. Morevoer, the website has a playlist component, in which using a database of song attributes (since the Spotify API depreciated it's own song attributes), the website will try it's best to recommend you songs that you might like! 

The application is still underdevelopment and in the future, you can expect the following changes:

- Integration of React; currently, the code uses Jinja and HTML as the primary front-end, and most of the rendering occurs on the server-side which will be improved upon.
- Improved functionality of track recommendation function
  - Currently, the AI model is not the most accurate as a result of the lackluster data, therefore a larger database is being consolidated and a better model is being developed using cosine similarity and item-based recommendation machine learning. 
