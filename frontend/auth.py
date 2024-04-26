# auth.py
import streamlit as st
from streamlit_google_auth import Authenticate
import os
from dotenv import load_dotenv

load_dotenv()

def authenticate():
    authenticator = Authenticate(
        secret_credentials_path='client_secret.json',
        cookie_name='fW_cookie',
        cookie_key='fw_secret',
        redirect_uri=os.getenv('AUTH_REDIRECT_URI'),
    )
    authenticator.check_authentification()
    authenticator.login()

