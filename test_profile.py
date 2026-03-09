import requests

API_URL = "http://localhost:8000"

def test_profile():
    email = "test.create@adaniuni.ac.in"
    password = "Password123!"
    
    login_res = requests.post(f"{API_URL}/api/auth/login-json", json={"email": email, "password": password})
    print("Login:", login_res.status_code, login_res.text)
    
    if login_res.status_code == 200:
        token = login_res.json()["access_token"]
        
        prof_res = requests.get(f"{API_URL}/api/profile", headers={"Authorization": f"Bearer {token}"})
        print("Profile GET:", prof_res.status_code, prof_res.text)

test_profile()
