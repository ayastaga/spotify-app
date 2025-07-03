async function updateCurrentTrack() {
    try {
        const response = await fetch('/current-track');
        const data = await response.json();

        const player = document.getElementById('spotify-player');
        if (player.src != data.embed_url) {
            player.src = data.embed_url;
        }
    } catch (error){
        console.error('cannot fetch current track', error);
    }
};


async function updateTracks(contentType, term, title_name){
    const response = await fetch(`/fav-${contentType}-${term}`);
    const data = await response.json();

    const title = document.getElementById(`${contentType}-title`);
    title.innerText = contentType === 'tracks' ? `Top Tracks (${title_name})` : `Top Artists (${title_name})`;
    
    const list = document.getElementById(`${contentType}-list`);
    list.innerHTML = '';

    const shortTermBtn = document.getElementById('custom-btn-short-term');
    const mediumTermBtn = document.getElementById(`custom-btn-medium-term`);
    const longTermBtn  = document.getElementById(`custom-btn-long-term`);

    shortTermBtn.style.backgroundColor = 'white';
    shortTermBtn.style.color = 'black';
    mediumTermBtn.style.backgroundColor = 'white';
    mediumTermBtn.style.color = 'black';
    longTermBtn.style.backgroundColor = 'white';
    longTermBtn.style.color = 'black';

    const btnPressed = document.getElementById(`custom-btn-${term}`)
    btnPressed.style.backgroundColor = 'black';
    btnPressed.style.color = 'white';
    
    let counter = 0;

    if (contentType === 'tracks'){
        data.items.forEach(track => {
            counter += 1;
            list.innerHTML += `
            <div class="container border custom-card">
            <div class="container d-flex" style="align-content: center; align-items: center;">
                <div style="width: 100px; max-width: 100px; min-width: 100px;">
                    <h1 class="display-1 user-select-none text-muted" style="text-align: center; align-content: center;">${counter}</h1>
                </div>
                <img id="img-styling" src="${track.album.images[0].url}" class="track-image">
                <div class="custom-card-body">
                    <!-- href="${track.external_urls.spotify}" -->
                    <h4><a id="play_song" onclick="setTrack('${track.id}')" target="_blank">${track.name}</a></h4>
                    <p>by ${track.artists.map(artist => artist.name).join(', ')}</p>
                </div>
            </div>
            <div class="float-end border p-2 mx-3 user-select-none" style="width: 80px; text-align: center;">
                <h2>${track.popularity}</h2>
                <p style="padding: 0; margin: 0; font-size: 12px;"><small>popularity</small></p>
            </div>
        </div>
            `;
        })
    } else {
        data.items.forEach(artist => {
            counter += 1;
            list.innerHTML += `
            <div class="container border custom-card">
                <div class="container d-flex" style="align-content: center; align-items: center;">
                    <div style="width: 100px; max-width: 100px; min-width: 100px;">
                        <h1 class="display-1 text-muted" style="text-align: center; align-content: center;">${counter}</h1>
                    </div>
                    <img id="img-styling" src="${artist.images[0].url}">
                    <div class="custom-card-body">
                        <h4>${artist.name}</h4>
                        ${artist.genres.length > 0 ? `
                            <div id="tags" class="mr-2" style="color: white;">
                                ${artist.genres.map(genre => `<p>${genre}</p>\n`).join('')}
                            </div>
                        ` : ''}
                    </div>
                </div>
                <div class="float-end border p-2 mx-3" style="width: 6em; text-align: center;">
                    <h2>${artist.popularity}</h2>
                    <p style="padding: 0; margin: 0; font-size: 12px;"><small>popularity</small></p>
                </div>
            </div>
            `;
        })
    }
    
};

/// REWRITE THIS FOR TABLE
async function updateRecentlyPlayed(){
    try {
        const response = await fetch('/recently-played');
        const data = await response.json();

        const list = document.getElementById('recently-played');
        list.innerHTML = '';
        
        data.items.forEach(track => {
            list.innerHTML += `<li>${track.track.name}</li>`
        })
    } catch(error){
        console.error('cannot fetch most recent tracks', error);
    }
}

async function setTrack(track_id){
    let spotify_player = document.getElementById('spotify-player');
    spotify_player.src = `https://open.spotify.com/embed/track/${track_id}`;
}

