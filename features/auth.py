# utils/auth.py
import streamlit as st
from database.db_methods import create_user, verify_user

def register_user(name, email, password):
    user_id = create_user(name, email, password)
    return user_id is not None

def login_user(email, password):
    user = verify_user(email, password)
    if user:
        return True, user["name"], user["id"]
    return False, None, None

def require_login():
    if "logged_in" not in st.session_state or not st.session_state.logged_in:
        st.session_state.page = "login"
        st.stop()

def logout():
    """Clears the session state to log the user out."""
    for key in list(st.session_state.keys()):
        del st.session_state[key]