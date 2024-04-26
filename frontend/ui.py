# ui.py
import streamlit as st
from database import connect_to_snowflake, insert_user_info

def render_user_info(ctx):
    user_info = st.session_state.get('user_info')
    st.image(user_info.get('picture'))
    st.write('Hello, '+ user_info.get('name'))
    st.write('Your email is '+ user_info.get('email'))
    st.write('Your name is '+ user_info.get('name'))
    email = user_info.get('email')
    name = user_info.get('name')

    insert_user_info(ctx, email, name)



