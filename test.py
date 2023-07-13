import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import lyricsgenius
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
import string
from langdetect import detect
from nltk import pos_tag, word_tokenize

nltk.download('stopwords')
nltk.download('punkt')
nltk.download('maxent_ne_chunker')
nltk.download('words')

CLIENT_ID = "9c2bf5fc8cf44b9f826b56adda060785"
CLIENT_SECRET = "f356e5321b9548f39bba9bb7d3046f51"

genius_token = 'YOUR_GENIUS_API_TOKEN'

genius = lyricsgenius.Genius(genius_token)

client_credentials_manager = SpotifyClientCredentials(client_id=CLIENT_ID, client_secret=CLIENT_SECRET)
sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

def get_top_words(artist_name, num_words):
    results = sp.search(q='artist:' + artist_name, type='artist', limit=1)
    items = results['artists']['items']

    if len(items) > 0:
        artist = items[0]
        artist_id = artist['id']

        top_tracks = sp.artist_top_tracks(artist_id)['tracks']

        lyrics = ''

        for track in top_tracks[:num_words]:
            song = genius.search_song(track['name'], artist_name)
            if song is not None:
                if detect(song.lyrics) == 'en':
                    cleaned_lyrics = song.lyrics.replace(artist_name, '')
                    cleaned_lyrics = remove_featured_artists(cleaned_lyrics)
                    lyrics += cleaned_lyrics

        lyrics = lyrics.replace('\n', ' ').replace('\r', ' ').replace('\t', ' ').replace("'", ' ').replace("-", ' ')
        lyrics = ' '.join(lyrics.split())

        words = word_tokenize(lyrics.lower())

        stop_words = set(stopwords.words('english'))
        extra_stop_words = {'word1', 'word2', 'word3', "i'm", "'s", "'m", "'ll", "n't", "'re", "wan", "chorus", "verse",
                            "pre-chorus", "na", "gon", "mmm", "1", "2", "3", "4", "5", "6", "7", "memoria", "'ve",
                            "post-chorus", "roger", "waters", "david", "gilmour", "intro", "lyrics", "solo",
                            "instrumental", "ca", "—", "outro", "january", "march", "may", "february", "april", "june",
                            "july", "ai", "feat", "’", "lamar-", "ft.", "ta", "remix","n","weeknd","x3","cody","wo"}
        stop_words.update(extra_stop_words)

        words = [word for word in words if
                 word not in stop_words and not all(char in string.punctuation for char in word)]

        word_count = {}
        for word in words:
            word_count[word] = word_count.get(word, 0) + 1

        sorted_words = sorted(word_count.items(), key=lambda x: x[1], reverse=True)

        print("Top Used Words of", artist_name)
        for word, count in sorted_words[:num_words]:
            print(f"{word}: {count}")
    else:
        print("Artist not found.")

def remove_featured_artists(lyrics):
    tokens = word_tokenize(lyrics)
    tagged_tokens = pos_tag(tokens)
    cleaned_tokens = []
    for word, tag in tagged_tokens:
        if tag != 'NNP':
            cleaned_tokens.append(word)
    return ' '.join(cleaned_tokens)

while True:
    artist_name = input("Enter the name of the artist: ")
    num_words = int(input("Enter the number of top words to retrieve: "))
    
    get_top_words(artist_name, num_words)
    
    retry = input("Do you want to try another artist? (y/n): ")
    if retry.lower() != 'y':
        break
