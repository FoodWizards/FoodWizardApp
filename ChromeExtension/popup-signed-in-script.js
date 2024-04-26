// Logic for submit button
const submitBtn = document.getElementById('submitBtn');
const urlInput = document.getElementById('urlInput');

const youtubeUrlRegex = /^(https?:\/\/)?(www\.)?(youtube\.com\/(watch\?(.*&)?v=|embed\/|v\/)|youtu\.be\/)([a-zA-Z0-9_-]{11})/;
const BASE_URL = 'localhost:8080/api/v1'
async function sendDataToServer(url) {
    try {
        const tokenData = await chrome.storage.local.get('foodWizard_token');
        const token = tokenData.foodWizard_token;
            const response = await fetch('http://' + BASE_URL + '/process_url_extension', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}` },
        body: JSON.stringify({ 'url': url })
      });
  
      if (!response.ok) {
        throw new Error(`${response.status} - ${response.statusText}`);
      }
  
      return await response.json();
    } catch (error) {
      console.log('Error sending URL to FastAPI endpoint:', error);
      alert('An error occurred while processing the URL. Please try again.');
    }
  }
  
  submitBtn.addEventListener('click', async function () {
    const url = urlInput.value.trim(); // Get the trimmed URL from the input field
  
    // Basic validation (can be enhanced)
    if (!url || !youtubeUrlRegex.test(url)) {
      alert('Please enter a valid YouTube URL.');
      return;
    }
  
    try {
      const data = await sendDataToServer(url);
      alert("URL put successfully on queue. You can check back later on your favourite recipes tab.")
      console.log('Response from FastAPI endpoint:', data); // Handle the response data as needed
  
      urlInput.value = '';
    } catch (error) {
      console.error(error);
      alert('An error occurred while processing the URL. Please try again.');
    }
  });

document.querySelector('#sign-out').addEventListener('click', function () {
    chrome.runtime.sendMessage({ message: 'logout' }, function (response) {
        if (response === 'success') window.close();
    });
});
document.querySelector('#statusBtn').addEventListener('click', function () {
    chrome.runtime.sendMessage({ message: 'isUserSignedIn' }, function (response) {
        alert(response);
    });
});
  