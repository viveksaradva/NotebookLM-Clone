import streamlit as st
import requests

# API URL
API_URL = "http://127.0.0.1:9000/api/v1"

# Initialize session state
if "token" not in st.session_state:
    st.session_state.token = None
if "user" not in st.session_state:
    st.session_state.user = None

def login(username, password):
    """Login a user."""
    url = f"{API_URL}/auth/login"
    data = {"username": username, "password": password}
    
    try:
        response = requests.post(url, json=data)
        
        if response.status_code == 200:
            token_data = response.json()
            st.session_state.token = token_data["access_token"]
            return True
        else:
            st.error(f"Error: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        st.error(f"API Error: {str(e)}")
        return False

def register(username, email, password):
    """Register a new user."""
    url = f"{API_URL}/auth/register"
    data = {"username": username, "email": email, "password": password}
    
    try:
        response = requests.post(url, json=data)
        
        if response.status_code == 201:
            return True
        else:
            st.error(f"Error: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        st.error(f"API Error: {str(e)}")
        return False

def get_current_user():
    """Get current user information."""
    url = f"{API_URL}/auth/me"
    headers = {"Authorization": f"Bearer {st.session_state.token}"}
    
    try:
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            st.session_state.user = response.json()
            return True
        else:
            st.error(f"Error: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        st.error(f"API Error: {str(e)}")
        return False

def logout():
    """Logout the current user."""
    st.session_state.token = None
    st.session_state.user = None

# Main app
st.title("📚 DocuMind - Simple Login")

if st.session_state.token:
    # User is logged in
    if st.session_state.user:
        st.write(f"Welcome, {st.session_state.user['username']}!")
    else:
        if get_current_user():
            st.write(f"Welcome, {st.session_state.user['username']}!")
        else:
            st.error("Failed to get user information.")
    
    if st.button("Logout"):
        logout()
        st.rerun()
else:
    # User is not logged in
    tab1, tab2 = st.tabs(["Login", "Register"])
    
    with tab1:
        st.subheader("Login")
        username = st.text_input("Username", key="login_username")
        password = st.text_input("Password", type="password", key="login_password")
        
        if st.button("Login"):
            if login(username, password):
                st.success("Login successful!")
                st.rerun()
            else:
                st.error("Login failed. Please check your credentials.")
    
    with tab2:
        st.subheader("Register")
        username = st.text_input("Username", key="register_username")
        email = st.text_input("Email", key="register_email")
        password = st.text_input("Password", type="password", key="register_password")
        
        if st.button("Register"):
            if register(username, email, password):
                st.success("Registration successful! Please login.")
            else:
                st.error("Registration failed. Please try again.")
