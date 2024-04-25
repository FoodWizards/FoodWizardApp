# auth.py
import streamlit as st
from streamlit_google_auth import Authenticate

def authenticate():
    authenticator = Authenticate(
        secret_credentials_path='client_secret.json',
        cookie_name='fW_cookie',
        cookie_key='fw_secret',
        redirect_uri='http://localhost:8501',
    )
    authenticator.check_authentification()
    authenticator.login()
