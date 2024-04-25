// Logic for submit button
const submitBtn = document.getElementById('submitBtn');
const urlInput = document.getElementById('urlInput');

async function sendDataToServer(url) {
    try {
        const tokenData = await chrome.storage.local.get('foodWizard_token');
        const token = tokenData.foodWizard_token;
            const response = await fetch('http://0.0.0.0:8000/process_url', {
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
    if (!url) {
      alert('Please enter a valid URL.');
      return;
    }
  
    try {
      const data = await sendDataToServer(url);
      console.log('Response from FastAPI endpoint:', data); // Handle the response data as needed
  
      // Optionally, clear the input field after successful submission
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
  