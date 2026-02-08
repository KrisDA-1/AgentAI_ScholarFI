import streamlit as st
from utils.auth import login_user
from utils.styles import login_css

def run():
    # --- Load CSS ---
    login_css()
    
    st.markdown('<h1 style="font-size: 2.5em; font-weight: bold; color: #4a73ff">Welcome to ScholarFi </h1>', unsafe_allow_html=True)
    st.markdown('<p style="font-size: 1.1em; color: #000000">Please login or register to continue.</p>', unsafe_allow_html=True)

    email = st.text_input("Email", key="login_email")
    password = st.text_input("Password", type="password", key="login_password")


    if st.button("Login"):
        if not email or not password:
            st.warning("Please enter both email and password.")
        else:
            success, name, user_id = login_user(email, password)
            if success:
                st.session_state.logged_in = True
                st.session_state.user_name = name
                st.session_state.user_id = user_id
                st.success(f"Welcome back, {name}!")
                st.session_state.page = "dashboard"
            else:
                st.error("Invalid email or password!")

    if st.button("Go to Register"):
        st.session_state.page = "register"