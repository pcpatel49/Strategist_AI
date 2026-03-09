import requests
import json
import logging
from pprint import pprint

API_URL = "http://localhost:8000"

def test_full_flow():
    email = "test.rate.limit@adaniuni.ac.in"
    out = []
    out.append("Testing Registration...")
    reg_data = {
        "email": email,
        "password": "Password123!",
        "first_name": "Test",
        "last_name": "User",
        "current_grade": 10,
        "graduation_year": 2026
    }
    res = requests.post(f"{API_URL}/api/auth/register", json=reg_data)
    out.append(f"Register Status: {res.status_code}")
    out.append(f"Register Body: {res.text}")
    
    if res.status_code == 201:
        out.append("Now going into DB to fetch OTP...")
        import os
        from sqlalchemy import create_engine, text
        from dotenv import load_dotenv
        load_dotenv()
        engine = create_engine(os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost/strategist_ai"))
        with engine.connect() as conn:
            otp_val = conn.execute(text(f"SELECT otp FROM users WHERE email='{email}'")).fetchone()[0]
            out.append(f"Fetched OTP: {otp_val}")
            
        out.append("Testing OTP Verification...")
        verify_res = requests.post(f"{API_URL}/api/auth/verify-otp", json={"email": email, "otp": otp_val})
        out.append(f"Verify Status: {verify_res.status_code}")
        out.append(f"Verify Body: {verify_res.text}")
        
        out.append("Testing Login...")
        login_res = requests.post(f"{API_URL}/api/auth/login-json", json={"email": email, "password": "Password123!"})
        out.append(f"Login Status: {login_res.status_code}")
        out.append(f"Login Body: {login_res.text}")
        
    with open("test_flow_output.txt", "w") as f:
        f.write("\n".join(out))

test_full_flow()
