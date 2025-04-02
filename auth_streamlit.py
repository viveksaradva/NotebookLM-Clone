import streamlit as st
import requests

API_URL = "http://127.0.0.1:8000/auth"

st.set_page_config(page_title="Auth System", page_icon="🔐", layout="centered")

# Initialize session state
if "page" not in st.session_state:
    st.session_state["page"] = "Login"
if "token" not in st.session_state:
    st.session_state["token"] = None

st.title("🔐 Authentication System")

# Sidebar Navigation
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/942/942799.png", width=80)  # Auth icon
    if st.session_state["token"]:
        option = st.radio("Navigation", ["🏠 Protected Route", "🚪 Logout"])
    else:
        option = st.radio("Choose an action", ["📝 Register", "🔑 Login"])

# Registration Page
if option == "📝 Register":
    st.subheader("Create a New Account")
    with st.form("register_form"):
        username = st.text_input("👤 Username")
        email = st.text_input("📧 Email")
        password = st.text_input("🔑 Password", type="password")
        submit_btn = st.form_submit_button("Register")

    if submit_btn:
        response = requests.post(f"{API_URL}/register", json={"username": username, "email": email, "password": password})
        if response.status_code == 200:
            st.success("🎉 Registration successful! Redirecting to login...")
            st.session_state["page"] = "🔑 Login"
            st.rerun()
        else:
            st.error(response.json().get("detail", "Registration failed"))

# Login Page
elif option == "🔑 Login":
    st.subheader("Login to Your Account")
    with st.form("login_form"):
        username = st.text_input("👤 Username")
        password = st.text_input("🔑 Password", type="password")
        submit_btn = st.form_submit_button("Login")

    if submit_btn:
        response = requests.post(f"{API_URL}/login", json={"username": username, "password": password})
        if response.status_code == 200:
            token = response.json().get("access_token")
            st.session_state["token"] = token
            st.success("✅ Login successful! Redirecting...")
            st.rerun()
        else:
            st.error("❌ Invalid credentials. Please try again.")

# Protected Route (only for logged-in users)
elif option == "🏠 Protected Route" and st.session_state["token"]:
    st.subheader("🔒 Secure Dashboard")
    headers = {"Authorization": f"Bearer {st.session_state['token']}"}
    response = requests.get(f"{API_URL}/protected", headers=headers)

    if response.status_code == 200:
        user_info = response.json()
        st.success(f"🔹 Welcome, {user_info['message']}!")
    else:
        st.error("⛔ Access Denied: Invalid Token")

# Logout Page
elif option == "🚪 Logout" and st.session_state["token"]:
    st.subheader("👋 Logout")
    st.write("Are you sure you want to log out?")
    if st.button("Confirm Logout", type="primary"):
        del st.session_state["token"]
        st.success("👋 Logged out successfully!")
        st.rerun()
