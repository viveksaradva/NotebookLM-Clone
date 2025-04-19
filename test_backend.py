import requests

# Try different endpoints
endpoints = [
    "http://127.0.0.1:9000/",
    "http://127.0.0.1:9000/health",
    "http://127.0.0.1:9000/api/v1/auth/register",
    "http://127.0.0.1:9000/docs"
]

for endpoint in endpoints:
    try:
        print(f"\nTesting endpoint: {endpoint}")
        response = requests.get(endpoint)
        print(f"Status code: {response.status_code}")
        print(f"Response: {response.text[:100]}...")  # Show first 100 chars
    except Exception as e:
        print(f"Error: {e}")
