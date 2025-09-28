from typing import Optional
from sqlmodel import Session, select
from app.models.user import User, UserCreate
from argon2 import PasswordHasher
import os
from jose import JWTError, jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HHTPBearer
from database.connection import get_session
from datetime import datetime, timedelta

ph = PasswordHasher()

security = HHTPBearer()


SECRET_KEY = os.getenv("SECRET_KEY", "your-super-secret-key-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

def create_user(session: Session, user_data: UserCreate) -> User:
    """Create a new user"""
    # Hash the password
    hashed_password = ph.hash(user_data.password)
    
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

def get_user_by_id(session: Session, user_id: int) -> Optional[User]:
    """Get user by ID"""
    return session.get(User, user_id)

def get_user_by_username(session: Session, username: str) -> Optional[User]:
    """Get user by username"""
    return session.exec(select(User).where(User.username == username)).first()

def get_user_by_email(session: Session, email: str) -> Optional[User]:
    """Get user by email"""
    return session.exec(select(User).where(User.email == email)).first()

def get_user_by_username_or_email(session: Session, username_or_email: str) -> Optional[User]:
    """Get user by username or email"""
    return session.exec(
        select(User).where(
            (User.username == username_or_email) | 
            (User.email == username_or_email)
        )
    ).first()

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify password with Argon2"""
    try:
        ph.verify(hashed_password, plain_password)
        return True
    except:
        return False
    
def get_current_user_from_token(session: Session, user_id: int) -> Optional[User]:
    """Get current user by ID from JWT token"""
    user = session.get(User, user_id)
    if user and user.is_active:
        return user
    return None


def get_active_user_by_id(session: Session, user_id: int) -> Optional[User]:
    """Get active user by ID (for JWT token validation)"""
    user = session.get(User, user_id)
    if user and user.is_active:
        return user
    return None

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security), session : Session = Depends(get_session)):

    try:
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        user_id : int = payload.get("user_id")
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials"
            )
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials"
        )
    user = session.get(User, user_id)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials"
        )
    return user


def create_access_token(data: dict):
    """Create JWT access token"""
    to_encode = data.copy()
    expire = datetime.now() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt