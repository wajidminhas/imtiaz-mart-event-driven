import hashlib
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlmodel import Session, select
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError
from app.models.user import User, UserCreate, UserResponse, UserLogin, UserUpdate, PasswordChange, DeleteAccount
from app.database.connection import get_session

from dotenv import load_dotenv
import os
from jose import JWTError, jwt
from datetime import datetime, timedelta
from app.crud.user import (
    create_user, 
    get_user_by_username_or_email, 
    hash_password,
    verify_password,
    get_user_by_id, 
    get_user_by_email,
    get_user_by_username
)
# Create router
router = APIRouter(prefix="/users", tags=["users"])

load_dotenv
security = HTTPBearer()


SECRET_KEY = os.getenv("SECRET_KEY", "your-super-secret-key-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
# Password hashing with Argon2 (more reliable than bcrypt)
# ph = PasswordHasher()


# ************ CREATE OPERATIONS ************

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register_user(
    user_data: UserCreate, 
    session: Session = Depends(get_session)
):
    """Register a new user"""
    
    # Check for active users only
    existing_username = session.exec(
        select(User).where(
            User.username == user_data.username,
            User.is_active == True
        )
    ).first()
    
    if existing_username:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already taken"
        )
    
    # Check for recently deleted accounts
    deleted_username = session.exec(
        select(User).where(
            User.username == user_data.username,
            User.is_active == False,
            User.deleted_at.isnot(None)
        )
    ).first()
    
    if deleted_username and deleted_username.deleted_at:
        days_since_deletion = (datetime.now() - deleted_username.deleted_at).days
        if days_since_deletion < 30:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Username reserved for account recovery. Available in {30 - days_since_deletion} days."
            )
    
    # Check email similarly
    existing_email = get_user_by_email(session, user_data.email)
    if existing_email and existing_email.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Create user using CRUD function
    new_user = create_user(session, user_data)
    
    return new_user
    # Rest of registration logic...

# ************ AUTHENTICATION & AUTHORIZATION ************

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security), session : Session = Depends(get_session)):
    
    print(f"Received token: {credentials.credentials[:20]}...")  # First 20 chars
    print(f"SECRET_KEY being used: {SECRET_KEY[:10]}...")  # First 10 chars
    print(f"Algorithm: {ALGORITHM}")
    
    try:
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        print(f"Decoded payload: {payload}")
        user_id : int = payload.get("user_id")
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials"
            )
    except JWTError as e:
        print(f"JWT Error: {str(e)}")  # See the actual error
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



@router.get("/me", response_model=UserResponse)
async def get_current_user_profile(current_user: User = Depends(get_current_user)):
    """Get current user profile (protected route)"""
    return current_user  
  # We'll create this model

# ************ UPDATE OPERATIONS / UPDATE USER  ************

@router.put("/me", response_model=UserResponse)
async def update_profile(
    update_data: UserUpdate,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """Update current user profile"""
    
    # Check if username is being changed and already exists
    if update_data.username and update_data.username != current_user.username:
        existing = get_user_by_username(session, update_data.username)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already taken"
            )
        current_user.username = update_data.username
    
    # Check if email is being changed and already exists
    if update_data.email and update_data.email != current_user.email:
        existing = get_user_by_email(session, update_data.email)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        current_user.email = update_data.email
    
    # Update other fields
    if update_data.first_name:
        current_user.first_name = update_data.first_name
    if update_data.last_name:
        current_user.last_name = update_data.last_name
    
    current_user.updated_at = datetime.now()
    
    session.add(current_user)
    session.commit()
    session.refresh(current_user)
    
    return current_user


# ************ UPDATE OPERATIONS / CHANGE PASSWORD  ************

@router.post("/change-password")
async def change_password(
    password_data: PasswordChange,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """Change user password"""
    
    # Verify old password
    if not verify_password(password_data.old_password, current_user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect current password"
        )
    
    # Hash new password
    new_hashed_password = hash_password(password_data.new_password)
    
    # Update password
    current_user.password_hash = new_hashed_password
    current_user.updated_at = datetime.now()
    
    session.add(current_user)
    session.commit()
    
    return {"message": "Password changed successfully"}
# ************ READ OPERATIONS ************

@router.get("me/{user_id}", response_model=UserResponse)
async def get_user(user_id: int, session: Session = Depends(get_session)):
    """Get user by ID"""
    
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return user

def create_access_token(data: dict):
    """Create JWT access token"""
    to_encode = data.copy()
    expire = datetime.now() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

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
# ************ DELETE OPERATIONS / THIS WILL DELETE USER BUT NOT PERMANENTLY************

  # We'll create this

@router.delete("/me")
async def delete_account(
    delete_data: DeleteAccount,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """Delete current user account (requires password confirmation)"""
    
    # Verify password before deletion
    if not verify_password(delete_data.password, current_user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect password"
        )
    
    # Soft delete
    current_user.is_active = False
    current_user.updated_at = datetime.now()
    
    session.add(current_user)
    session.commit()
    
    return {"message": "Account deactivated successfully"}

# ************ DELETE OPERATIONS / DEACTIVATE ACCOUNT WITH RECOVERY PERIOD ************

@router.delete("/me")
async def delete_account(
    delete_data: DeleteAccount,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """Deactivate account with 30-day recovery period"""
    
    if not delete_data.confirm:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Account deletion must be confirmed"
        )
    
    if not verify_password(delete_data.password, current_user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect password"
        )
    
    current_user.is_active = False
    current_user.deleted_at = datetime.now()
    current_user.updated_at = datetime.now()
    
    session.add(current_user)
    session.commit()
    
    return {
        "message": "Account scheduled for deletion",
        "recovery_deadline": (datetime.now() + timedelta(days=30)).isoformat(),
        "note": "You have 30 days to reactivate your account"
    }