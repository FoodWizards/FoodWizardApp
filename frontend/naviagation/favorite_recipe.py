# favorite_recipe.py
import streamlit as st
import requests
from bs4 import BeautifulSoup
import os



BASE_URL = os.getenv('BASE_URL')
API_URL = f"http://{BASE_URL}/favorite-recipes"



def get_title(url):
    try:
        response = requests.get(url)
        soup = BeautifulSoup(response.text, "html.parser")
        return soup.title.string
    except Exception as e:
        return None

def fav_recipe():
    st.title("My Favorite Recipe")
    user_info = st.session_state.get('user_info')
    if user_info:
        user_email = user_info['email']
#        email = {'email': email}
#        response = requests.get(API_URL, json =email)
        response = requests.get(f"{API_URL}/{user_email}")
        if response.status_code == 200:
            favorite_recipes = response.json()
            unique = set()
            if favorite_recipes:
                for id, recipe in enumerate(favorite_recipes):
                    if recipe['LINK_VIDEO'] in unique:
                        continue
                    unique.add(recipe['LINK_VIDEO'])
                    url = recipe['LINK_VIDEO']
                    summary = recipe['GENERATED_RECIPE']
                    title = recipe['TITLE']
                    user_email =recipe['USER_EMAIL']
                    if st.button(title, key=f'recipe-row-{id}'):
                        st.markdown(f"[{title}]({url})")
                        st.write(f"**Summary:** {summary}")
            else:
                st.write("No favorite recipes found.")
        else:
            st.error("Failed to fetch favorite recipes. Please try again later.")
    else:
        st.warning("User information not found.")
