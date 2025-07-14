<img width="1900" align="center" height="633" alt="image" src="https://github.com/user-attachments/assets/2a62694f-d03e-458a-bfa1-97e58f5c527f" />


# ECOUTE <img width="32" height="32" alt="image" src="https://github.com/user-attachments/assets/d46b7944-78df-48f6-ac18-e142d8e4ec75" />


This is a web application designed for music-junkies who love to know _everything_ about their music. Within this website, you can login (done by usign uAuth2.0), after which you can see your:

- Top artists (4 weeks, 6 months, 1 year)
- Top tracks (4 weeks, 6 months, 1 year)
- Your current playlists
- Your current audiobooks
- Your current shows
- Your recently played tracks
- Your spotify account
- All different types of news related to spotify

In addition to this, you can also sign up to our **mailing list**, where you will be recommended upcoming local shows near you. Morevoer, the website has a playlist component, in which using a database of song attributes (since the Spotify API depreciated it's own song attributes), the website will try it's best to recommend you songs that you might like! 

<p align="center">
  <a href="https://www.youtube.com/watch?v=rWWk0AjyVKE">
    <img src="https://img.youtube.com/vi/rWWk0AjyVKE/0.jpg" alt="Watch the video" />
  </a>
</p>

## Future Plans
The application is still underdevelopment and in the future, you can expect the following changes:

- Implementing an email automation system through geolocation to suggest local nearby shows 
- Improved functionality of track recommendation function
  - Currently, the AI model is not the most accurate as a result of the lackluster data, therefore a larger database is being consolidated and a better model is being developed using cosine similarity and item-based recommendation machine learning.
- Deploying the app and making it more accessible
  - The app, as of now, can be downloaded and work locally but in order to make it more accessible it needs to be deployed on an app such as Vercel. Right now, I am tryign to figure out:
    - how to outsource the database so it doesn't store locally
    - how to add env variables without making them client-side/public
    - replacing all the initialization calls with possibly an api to make the website less bulky
