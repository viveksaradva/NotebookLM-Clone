import requests
import json

# API URL
API_URL = "http://127.0.0.1:9000/api/v1"

def register_user(username, email, password):
    """Register a new user."""
    url = f"{API_URL}/auth/register"
    data = {
        "username": username,
        "email": email,
        "password": password
    }
    
    response = requests.post(url, json=data)
    print(f"Register Status Code: {response.status_code}")
    print(f"Register Response: {response.text}")
    
    return response.json() if response.status_code < 400 else None

def login_user(username, password):
    """Login a user."""
    url = f"{API_URL}/auth/login"
    data = {
        "username": username,
        "password": password
    }
    
    response = requests.post(url, json=data)
    print(f"Login Status Code: {response.status_code}")
    print(f"Login Response: {response.text}")
    
    return response.json() if response.status_code < 400 else None

def get_current_user(token):
    """Get current user information."""
    url = f"{API_URL}/auth/me"
    headers = {
        "Authorization": f"Bearer {token}"
    }
    
    response = requests.get(url, headers=headers)
    print(f"Get User Status Code: {response.status_code}")
    print(f"Get User Response: {response.text}")
    
    return response.json() if response.status_code < 400 else None

# Test the API
if __name__ == "__main__":
    # Register a new user
    print("Registering a new user...")
    user = register_user("testuser", "test@example.com", "password123")
    
    if user:
        print(f"User registered: {user}")
        
        # Login the user
        print("\nLogging in...")
        token_data = login_user("testuser", "password123")
        
        if token_data:
            token = token_data["access_token"]
            print(f"Login successful. Token: {token}")
            
            # Get current user info
            print("\nGetting user info...")
            current_user = get_current_user(token)
            
            if current_user:
                print(f"Current user: {current_user}")
            else:
                print("Failed to get user info.")
        else:
            print("Login failed.")
    else:
        print("Registration failed.")
