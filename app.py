import requests
from flask import Flask, request, jsonify, render_template
#from flask_ngrok import run_with_ngrok
import lyricsgenius
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
import string
from langdetect import detect
from nltk import pos_tag
import base64

app = Flask(__name__)
#run_with_ngrok(app)  # For running the app on ngrok

genius_token = 'MpWYjafBK5dmuZ3w_gEd3x1HoWuBI2LD7ZI5foptU01tyw-w_CsMw6je_7mMh3_M'
genius = lyricsgenius.Genius(genius_token)

nltk.download('stopwords')
nltk.download('punkt')
nltk.download('maxent_ne_chunker')
nltk.download('averaged_perceptron_tagger')
nltk.download('words')

CLIENT_ID = "9c2bf5fc8cf44b9f826b56adda060785"
CLIENT_SECRET = "f356e5321b9548f39bba9bb7d3046f51"


@app.route('/')
def home():
    return render_template('top_words.html')


@app.route('/api/top-words', methods=['GET', 'POST'])
def top_words():
    if request.method == 'POST':
        artist_name = request.form.get('artistName')
        num_words = request.form.get('numWords')
    elif request.method == 'GET':
        artist_name = request.args.get('artistName')
        num_words = request.args.get('numWords')
    else:
        return jsonify({'success': False, 'message': 'Method not allowed.'}), 405

    if artist_name is None or num_words is None:
        return jsonify({'success': False, 'message': 'Invalid parameters.'}), 400

    access_token = get_spotify_access_token()
    if not access_token:
        return jsonify({'success': False, 'message': 'Failed to retrieve Spotify access token.'}), 500

    headers = {
        'Authorization': 'Bearer ' + access_token
    }

    search_url = f'https://api.spotify.com/v1/search?q=artist:{artist_name}&type=artist&limit=1'
    response = requests.get(search_url, headers=headers)
    results = response.json()

    items = results['artists']['items']

    if len(items) > 0:
        artist = items[0]
        artist_id = artist['id']

        top_tracks_url = f'https://api.spotify.com/v1/artists/{artist_id}/top-tracks?country=US'
        response = requests.get(top_tracks_url, headers=headers)
        top_tracks = response.json()['tracks']

        lyrics = ''

        for track in top_tracks[:int(num_words)]:
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
                            "pre-chorus", "na", "gon", "mmm", "1", "2", "3", "4", "5", "6", "7", 'memoria', "'ve",
                            "post-chorus", "roger", "waters", "david", "gilmour", "intro", "lyrics", "solo",
                            "instrumental", "ca", "—", "outro", "january", "march", "may", "february", "april", "june",
                            "july", "ai", "feat", '’', "lamar-", "ft.", "ta", "remix", "n", "weeknd", "x3", "cody", "wo"}
        stop_words.update(extra_stop_words)

        words = [word for word in words if word not in stop_words and not all(char in string.punctuation for char in word)]

        word_count = {}
        for word in words:
            word_count[word] = word_count.get(word, 0) + 1

        sorted_words = sorted(word_count.items(), key=lambda x: x[1], reverse=True)

        top_words = [{'word': word, 'count': count} for word, count in sorted_words[:int(num_words)]]

        return jsonify({'success': True, 'topWords': top_words})
    else:
        return jsonify({'success': False, 'message': 'Artist not found.'}), 404


def get_spotify_access_token():
    auth_url = 'https://accounts.spotify.com/api/token'
    headers = {
        'Authorization': 'Basic ' + base64.b64encode((CLIENT_ID + ':' + CLIENT_SECRET).encode()).decode(),
    }
    data = {
        'grant_type': 'client_credentials'
    }
    response = requests.post(auth_url, headers=headers, data=data)
    if response.status_code == 200:
        return response.json().get('access_token')
    else:
        return None


def remove_featured_artists(lyrics):
    tokens = word_tokenize(lyrics)
    tagged_tokens = pos_tag(tokens)
    cleaned_tokens = []
    for word, tag in tagged_tokens:
        if tag != 'NNP':
            cleaned_tokens.append(word)
    return ' '.join(cleaned_tokens)


if __name__ == '__main__':
    app.run()
