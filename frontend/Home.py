# main.py
import streamlit as st
from auth import authenticate
from database import connect_to_snowflake, create_user_info_table
#from ui import render_user_info
from naviagation.my_info import show_info
from naviagation.favorite_recipe import fav_recipe
from naviagation.find_recipe import find_recipe
from naviagation.search_recipe import search_recipe

from naviagation.video_url_processor import process_url
from database import connect_to_snowflake, insert_user_info

st.title('FoodWizard')

def main():
    user_info = st.session_state.get('user_info')
    print(user_info)
    ctx = connect_to_snowflake()
    authenticate()
    create_user_info_table(ctx)
    
    # Check if the user is authenticated
    if 'connected' not in st.session_state or not st.session_state['connected']:
        #st.warning("You are not authenticated.")
        return
    
    else:
        render_user_info(ctx)
        pages = {
            "My info": show_info,
            "Home": process_url,
            "Favorite Recipe": fav_recipe,
            "Find Recipe" : find_recipe,
            "Search Recipe" : search_recipe
            
    
            # Add more pages here
        }

        st.sidebar.title("Navigation")
        selection = st.sidebar.radio("Go to", list(pages.keys()))

            # Handle invalid selection
        if selection not in pages:
            st.error("Invalid selection. Please choose a valid option.")
        else:
            pages[selection]()

        if st.button('Log out'):
            st.session_state['connected'] = False
            st.session_state['user_info'] = None
            ctx.close()
            st.experimental_rerun()
           
    # Render the dashboard page if authenticated


def render_user_info(ctx):
    
    user_info = st.session_state.get('user_info')
    
    email = user_info['email']
    name = user_info['name']

    insert_user_info(ctx, email, name)

if __name__ == "__main__":
    main()
