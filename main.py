from datetime import date
from bs4 import BeautifulSoup
import requests
import spotipy
from spotipy.oauth2 import SpotifyOAuth

years_alive = []
top_songs = []

# Create list of years user has been alive

def list_years_alive() -> list[int]: 
    """
    output: list of years user has been alive
    """
    current_year = date.today().year
    for year in range(int(birth_year), current_year + 1):
        years_alive.append(year)
    return years_alive

def list_top_songs() -> list[dict]:
    """
    output: a list of the top Billboard 100 song for every year in list_years_alive
    """
    for year in years_alive:
        response = requests.get(f'https://www.billboard.com/charts/hot-100/{year}-{birth_month}-{birth_day}')
        soup = BeautifulSoup(response.text, 'html.parser')
        
        top_song = soup.find('a', attrs={'href':'#', 'class':'c-title__link lrv-a-unstyle-link'})
        top_song_name = top_song.text.strip() if top_song else None
        top_songs.append({'name': top_song_name, 'year': year}) if top_song_name else None


def make_playlist():
    """
    output: creates a spotify playlist in the user's Spotify account based on the top_songs list"""
    # Spotify authentication
    sp = spotipy.Spotify(
        auth_manager = SpotifyOAuth(
            scope = "playlist-modify-private",
            redirect_uri = "http://example.com",
            client_id = '#',
            client_secret = '#',
            show_dialog = True,
            cache_path = "token.txt"
        )
    )
    user_id = sp.current_user()["id"]

    # Find songs
    song_uris = []
    for song in top_songs:
        resulting = sp.search(q=f"track:{song['name']} year:{song['year']}", type = "track")
        try:
            uri = resulting["tracks"]["items"][0]["uri"]
            song_uris.append(uri)
        except IndexError:
            print(f"Song {song['name']} from {song['year']} doesn't exist in Spotify's library. It will be skipped.")
        

    # Create playlist
    playlist = sp.user_playlist_create(user=user_id, name='My Birthday Playlist', public=False)
    sp.user_playlist_add_tracks(user=user_id, playlist_id = playlist["id"], tracks=song_uris)
    print('Your playlist has been created and is available in your Spotify account.')


birthdate = input('When is your birthdate in the format MM-DD-YYYY? ')
birth_month, birth_day, birth_year = birthdate.split('-')
list_years_alive()
list_top_songs()
make_playlist()