document.getElementById('artist-form').addEventListener('submit', function(event) {
    event.preventDefault(); // Prevent form submission
  
    // Get form values
    var artistName = document.getElementById('artist-name').value;
    var numWords = document.getElementById('num-words').value;
  
    // Call the getTopWords function to retrieve the top words
    getTopWords(artistName, numWords);
  });
  
  function getTopWords(artistName, numWords) {
    var apiUrl = 'https://example.com/api/top-words'; // Replace with the deployed backend API URL
  
    // Make an AJAX request to the backend API
    fetch(apiUrl, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        artistName: artistName,
        numWords: numWords
      })
    })
    .then(response => response.json())
    .then(data => {
      // Display the result
      var resultDiv = document.getElementById('result');
      resultDiv.innerHTML = '';
  
      if (data.success) {
        var topWords = data.topWords;
  
        if (topWords.length > 0) {
          var heading = document.createElement('h2');
          heading.textContent = 'Top Used Words of ' + artistName;
          resultDiv.appendChild(heading);
  
          var list = document.createElement('ul');
          topWords.forEach(function(word) {
            var listItem = document.createElement('li');
            listItem.textContent = word.word + ': ' + word.count;
            list.appendChild(listItem);
          });
  
          resultDiv.appendChild(list);
        } else {
          var message = document.createElement('p');
          message.textContent = 'No top words found for ' + artistName;
          resultDiv.appendChild(message);
        }
      } else {
        var message = document.createElement('p');
        message.textContent = data.message;
        resultDiv.appendChild(message);
      }
    })
    .catch(error => {
      console.error('Error:', error);
    });
  }
  