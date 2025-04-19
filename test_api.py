import requests

# Try to connect to the backend
try:
    response = requests.get("http://127.0.0.1:8080/")
    print(f"Response status code: {response.status_code}")
    print(f"Response content: {response.text}")
except Exception as e:
    print(f"Error connecting to backend: {e}")
