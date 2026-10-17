from sqlalchemy.orm import Session
from uuid import UUID, uuid4
from fastapi import HTTPException, status
from ..models.user import User
from ..models.workspace import Workspace
from ..utils.auth_utils import get_password_hash, verify_password, create_access_token
from ..schemas.auth import UserRegister, UserLogin, Token, UserResponse

def register_user(db: Session, data: UserRegister) -> tuple[User, Workspace]:
    """Register new user and create default workspace."""
    
    # Check if email exists
    existing = db.query(User).filter(User.email == data.email).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Create user
    user = User(
        id=uuid4(),
        email=data.email,
        password_hash=get_password_hash(data.password),
        full_name=data.full_name,
    )
    db.add(user)
    db.flush()
    
    # Create default workspace
    workspace = Workspace(
        id=uuid4(),
        owner_id=user.id,
        name=f"{data.email}'s Workspace",
        mode="personal",
        currency="IDR",
        timezone="Asia/Jakarta",
    )
    db.add(workspace)
    db.commit()
    db.refresh(user)
    db.refresh(workspace)
    
    return user, workspace

def authenticate_user(db: Session, data: UserLogin) -> User:
    """Authenticate user by email and password."""
    
    user = db.query(User).filter(User.email == data.email).first()
    
    if not user or not verify_password(data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return user

def create_user_token(user: User) -> Token:
    """Create JWT token for user."""
    
    access_token = create_access_token(
        data={"sub": str(user.id), "email": user.email}
    )
    
    return Token(access_token=access_token, token_type="bearer")
