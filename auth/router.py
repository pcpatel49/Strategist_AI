from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session
from uuid import UUID

from database.database import get_db
from database.models import User, Student
from auth.schemas import (
    UserCreate, UserResponse, Token, 
    EmailVerification, OTPVerification, PasswordResetRequest, PasswordReset
)
from auth.security import (
    get_password_hash, verify_password, create_access_token, 
    ACCESS_TOKEN_EXPIRE_MINUTES, create_verification_token,
    create_password_reset_token, blacklist_token, is_token_blacklisted
)
from utils.email import send_verification_email, send_password_reset_email
from utils.limiter import limiter
from auth.dependencies import security
import random
from datetime import datetime, timezone

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/register", response_model=dict, status_code=status.HTTP_201_CREATED)
def register(user: UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    hashed_password = get_password_hash(user.password)
    
    # Generate 6-digit OTP
    otp = "".join([str(random.randint(0, 9)) for _ in range(6)])
    otp_expires = datetime.now(timezone.utc) + timedelta(minutes=10)
    
    new_user = User(
        email=user.email, 
        password_hash=hashed_password,
        otp=otp,
        otp_expires_at=otp_expires
    )
    
    db.add(new_user)
    db.flush() # flush to get user id
    
    new_student = Student(
        student_id=new_user.id,
        first_name=user.first_name,
        last_name=user.last_name,
        current_grade=user.current_grade,
        graduation_year=user.graduation_year
    )
    db.add(new_student)
    db.commit()
    
    # Send OTP email
    send_verification_email(user.email, otp)
    
    return {"message": "User registered successfully. Please check your email for the 6-digit verification code."}

@router.post("/verify-otp", response_model=dict)
def verify_otp(payload: OTPVerification, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == payload.email).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
        
    if user.is_verified:
        return {"message": "Email already verified."}
        
    if not user.otp or user.otp != payload.otp:
        raise HTTPException(status_code=400, detail="Invalid verification code")
        
    # Check expiration
    if user.otp_expires_at:
        # Pydantic/SQLAlchemy might return naive or aware, let's normalize
        expires = user.otp_expires_at
        if expires.tzinfo is None:
            expires = expires.replace(tzinfo=timezone.utc)
        
        if expires < datetime.now(timezone.utc):
            raise HTTPException(status_code=400, detail="Verification code expired")
        
    user.is_verified = True
    user.otp = None # Clear OTP after verification
    user.otp_expires_at = None
    db.commit()
    return {"message": "Email successfully verified."}

@router.post("/verify-email", response_model=dict)
def verify_email(payload: EmailVerification, db: Session = Depends(get_db)):
    from jose import jwt, JWTError
    from auth.security import SECRET_KEY, ALGORITHM
    
    try:
        decoded = jwt.decode(payload.token, SECRET_KEY, algorithms=[ALGORITHM])
        email = decoded.get("sub")
        token_type = decoded.get("type")
        
        if token_type != "verification" or not email:
            raise HTTPException(status_code=400, detail="Invalid token")
            
        user = db.query(User).filter(User.email == email).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
            
        if user.is_verified:
            return {"message": "Email already verified."}
            
        user.is_verified = True
        db.commit()
        return {"message": "Email successfully verified."}
        
    except JWTError:
        raise HTTPException(status_code=400, detail="Invalid or expired token")

@router.post("/login", response_model=Token)
@limiter.limit("100/15minutes")
def login_form(request: Request, login_data: UserCreate, db: Session = Depends(get_db)):
    # Reusing UserCreate for email/password structure, or we can use OAuth2PasswordRequestForm
    # User specified accepting email and password, so checking UserCreate
    # Wait, UserCreate has more requirements. Let's create a dynamic check or use OAuth2PasswordRequestForm.
    # User said: "Accept email and password", let's use a simpler schema inline or just parse JSON.
    pass

# Redefining login to just take email and password instead of UserCreate which requires name etc.
from pydantic import BaseModel, EmailStr
class UserLogin(BaseModel):
    email: EmailStr
    password: str

@router.post("/login-json", response_model=Token)
@limiter.limit("100/15minutes")
def login_json(request: Request, login_data: UserLogin, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == login_data.email).first()
    if not user or not verify_password(login_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )
        
    if not user.is_verified:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email not verified. Please check your inbox."
        )
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    # Payload includes student_id, email, exp
    # user.id is the student_id due to 1:1 mapping in Student model primary key
    token_data = {
        "sub": user.email, 
        "student_id": str(user.id)
    }
    
    access_token = create_access_token(
        data=token_data, expires_delta=access_token_expires
    )
    
    return {
        "access_token": access_token, 
        "token_type": "bearer",
        "student_id": user.id
    }

@router.post("/logout", response_model=dict)
def logout(credentials: HTTPAuthorizationCredentials = Depends(security), db: Session = Depends(get_db)):
    token = credentials.credentials
    if is_token_blacklisted(db, token):
        return {"message": "Already logged out"}
        
    blacklist_token(db, token)
    return {"message": "Successfully logged out"}

@router.post("/forgot-password", response_model=dict)
def forgot_password(payload: PasswordResetRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == payload.email).first()
    if user:
        token = create_password_reset_token(user.email)
        send_password_reset_email(user.email, token)
        
    # Always return success to prevent email enumeration
    return {"message": "If that email is registered, a password reset link has been sent."}

@router.post("/reset-password", response_model=dict)
def reset_password(payload: PasswordReset, db: Session = Depends(get_db)):
    from jose import jwt, JWTError
    from auth.security import SECRET_KEY, ALGORITHM
    
    try:
        decoded = jwt.decode(payload.token, SECRET_KEY, algorithms=[ALGORITHM])
        email = decoded.get("sub")
        token_type = decoded.get("type")
        
        if token_type != "reset" or not email:
            raise HTTPException(status_code=400, detail="Invalid token")
            
        user = db.query(User).filter(User.email == email).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
            
        user.password_hash = get_password_hash(payload.new_password)
        db.commit()
        return {"message": "Password successfully reset."}
        
    except JWTError:
        raise HTTPException(status_code=400, detail="Invalid or expired token")
