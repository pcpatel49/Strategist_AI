import requests

API_URL = "http://localhost:8000"

# Assuming user might have recreated patelchetan1822@gmail.com or PRITPATEL.ict22@adaniuni.ac.in
# Let's try to login with a known account or create one to test the flow
def test_flow():
    # Attempt login to see error
    login_data = {"email": "PRITPATEL.ict22@adaniuni.ac.in", "password": "Password123!"}
    res = requests.post(f"{API_URL}/api/auth/login-json", json=login_data)
    print("Login Response Status:", res.status_code)
    print("Login Response Body:", res.text)

test_flow()
