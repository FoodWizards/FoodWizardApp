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
        pass
        # Call the API with the provided URL
        try:
            print("Starting authentication")
            
            user_info = st.session_state.get('user_info')
            user_email = None
            user_name = None
            if user_info:
                user_email = user_info['email']
                user_name = user_info['name']
            print(user_name)
            print(user_email)
            if (user_email is None) or (user_name is None):
                st.write("You may not be authenticated. Please login and try again")
                return
            response = requests.post(API_URL, json={"url": url, "email": user_email, "name": user_name})
            if(response.status_code == 200):
                st.write("You can check the result on your favourite links page later!")
            else:
                st.write("Something went wrong. Try again later")
            print(response)
        except requests.exceptions.RequestException as e:
            st.error(f"Streamlit Error: An error occurred while calling the API: {e}")

    else:
        st.warning("Please enter a URL to process.")