# ui.py
import streamlit as st

def show_info():

    user_info = st.session_state.get('user_info')

    st.image(user_info['picture'])
    st.write('Hello, '+ user_info['name'])
    st.write('Your email is '+ user_info['email'])
    st.write('Your name is '+ user_info['name'])