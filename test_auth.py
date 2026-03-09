import requests
import uuid

# Simulate registering/login two identical users at the same time
API_URL = "http://localhost:8000"

def test_login_flow():
    # Attempt login for an existing user
    login_data = {"email": "patelchetan1822@gmail.com", "password": "Password123!"}
    
    # Get Token A
    res_a = requests.post(f"{API_URL}/api/auth/login-json", json=login_data)
    if res_a.status_code != 200:
        print("Login A failed. Make sure user exists.", res_a.text)
        return
    token_a = res_a.json()["access_token"]
    print(f"Token A: {token_a[:20]}...")

    # Get Token B immediately
    res_b = requests.post(f"{API_URL}/api/auth/login-json", json=login_data)
    token_b = res_b.json()["access_token"]
    print(f"Token B: {token_b[:20]}...")

    if token_a == token_b:
        print("ERROR: Tokens are identical. JTI fix didn't work.")
        return
    else:
        print("SUCCESS: Tokens are unique.")

    # Logout Token B
    headers_b = {"Authorization": f"Bearer {token_b}"}
    logout_res = requests.post(f"{API_URL}/api/auth/logout", headers=headers_b)
    print("Logout Token B:", logout_res.status_code)

    # Verify Token A still works (try fetching profile)
    headers_a = {"Authorization": f"Bearer {token_a}"}
    profile_res = requests.get(f"{API_URL}/api/profile", headers=headers_a)
    print("Fetch Profile with Token A:", profile_res.status_code)
    
    if profile_res.status_code == 200:
        print("SUCCESS: Token A is still valid after Token B logged out.")
    else:
        print("ERROR: Token A was blacklisted when Token B logged out.")

if __name__ == "__main__":
    test_login_flow()
