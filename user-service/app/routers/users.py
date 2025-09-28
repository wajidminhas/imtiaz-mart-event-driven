import hashlib
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError
from app.models.user import User, UserCreate, UserResponse, UserLogin
from app.database.connection import get_session
import os
from jose import JWTError, jwt
from datetime import datetime, timedelta
from crud.user import get_current_user, verify_password, create_access_token
# Create router
router = APIRouter(prefix="/users", tags=["users"])


SECRET_KEY = os.getenv("SECRET_KEY", "your-super-secret-key-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
# Password hashing with Argon2 (more reliable than bcrypt)
ph = PasswordHasher()



def hash_password(password: str) -> str:
    """Hash a password with Argon2"""
    return ph.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password with Argon2"""
    try:
        ph.verify(hashed_password, plain_password)
        return True
    except VerifyMismatchError:
        return False

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register_user(
    user_data: UserCreate, 
    session: Session = Depends(get_session)
):
    """Register a new user"""
    
    # Check if username already exists
    existing_username = session.exec(
        select(User).where(User.username == user_data.username)
    ).first()
    
    if existing_username:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already taken"
        )
    
    # Check if email already exists
    existing_email = session.exec(
        select(User).where(User.email == user_data.email)
    ).first()
    
    if existing_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Hash the password
    hashed_password = hash_password(user_data.password)
    
    # Create new user
    new_user = User(
        username=user_data.username,
        email=user_data.email,
        password_hash=hashed_password,
        first_name=user_data.first_name,
        last_name=user_data.last_name
    )
    
    # Save to database
    session.add(new_user)
    session.commit()
    session.refresh(new_user)
    
    return new_user


# ***********************************************************************************************

@router.get("/{user_id}", response_model=UserResponse)
async def get_user(user_id: int, session: Session = Depends(get_session)):
    """Get user by ID"""
    
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return user

@router.get("/me", response_model=UserResponse)
async def get_current_user_profile(current_user: User = Depends(get_current_user)):
    """Get current user profile (protected route)"""
    return current_user  

#  user login endpoint

@router.post("/login")
async def login_user(
    login_data: UserLogin,
    session: Session = Depends(get_session)
):
    """Login user with username/email and password"""
    
    # Find user by username or email
    user = session.exec(
        select(User).where(
            (User.username == login_data.username_or_email) | 
            (User.email == login_data.username_or_email)
        )
    ).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )
    
    if not verify_password(login_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is deactivated"
        )
    
    # Replace the return statement in your login function with:
    return {
        "message": "Login successful",
        "access_token": create_access_token({"user_id": user.id, "username": user.username}),
        "token_type": "bearer",
        "user": UserResponse.model_validate(user)
    }