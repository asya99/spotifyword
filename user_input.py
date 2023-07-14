import requests

artist_name = input("Enter the name of the artist: ")
num_words = int(input("Enter the number of top words to retrieve: "))

url = 'http://127.0.0.1:5000/api/top-words'
params = {
    'artistName': artist_name,
    'numWords': num_words
}

response = requests.get(url, params=params)
data = response.json()

if data.get('success'):
    top_words = data.get('topWords')
    count = min(len(top_words), num_words)  # Limit the count to num_words or the length of top_words, whichever is smaller
    for i in range(count):
        word_info = top_words[i]
        word = word_info.get('word')
        count = word_info.get('count')
        print(f"{word}: {count}")
else:
    message = data.get('message')
    print(f"Error: {message}")
