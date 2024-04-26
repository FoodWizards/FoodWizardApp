import streamlit as st
import requests
import os

BASE_URL = os.getenv('BASE_URL')

API_URL = f"http://{BASE_URL}/process_url"

def process_url():
    st.title("Process URL")

    # Get the input URL from the user
    url = st.text_input("Enter the URL:", "")

    # Check if the user has entered a URL
    if url:
        # Call the API with the provided URL
        try:
            response = requests.post(API_URL, json={"url": url})
            response.raise_for_status()  # Raise an exception for non-2xx status codes
            result = response.json()

            # Display the result from the API
            st.write("API Response:")
            st.write(result)

        except requests.exceptions.RequestException as e:
            st.error(f"An error occurred while calling the API: {e}")

    else:
        st.warning("Please enter a URL to process.")