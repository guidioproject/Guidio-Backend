import os
import re
from datetime import datetime, timedelta
from typing import Match

from fastapi import Depends, Response, status
from jose import jwt, JWTError
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from auth import schemas
from auth.dependencies import has_valid_token
from auth.exceptions import invalid_credentials_exception, token_exception
from core.dependencies import DBDependency
from core.settings import AUTH_TOKEN
from users import models
from users.models import User

# CONSTANTS
bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# Intermediate function helpers
def get_password_hash(password: str) -> str:
    """Return password hash from plain password

    Args:
        password (str): plain password

    Returns:
        string value as password hash
    """
    return bcrypt_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Return True if plain password matches hashed password from the database after verification

    Args:
        plain_password (str): plain password from user input
        hashed_password (str): current user's password in database

    Returns:
        boolean value as result of verification
    """
    return bcrypt_context.verify(plain_password, hashed_password)


def find_detail_in_error(substring: str, message: str) -> Match[str] | None:
    """Handle search for substring in error message. Used in exception handling.

    Args:
        substring (str): specific text to search for, e.g. "email"
        message (str): message provided to search a substring in

    Returns:
        Match[str]: Match if string is found
        None: if string isn't found
    """
    return re.search(str(substring), str(message))


def create_auth_token(user_id: int) -> str:
    """Create authentication jwt token for specific user

    Args:
        user_id (int): user id for which jwt token will be created

    Returns:
        jwt token for specific user
    """
    token_creation_time = datetime.utcnow()
    encode = {"sub": str(user_id), "iat": token_creation_time}
    token_expiration_time = float(os.getenv("TOKEN_EXP_MINUTES"))
    expire = datetime.utcnow() + timedelta(minutes=token_expiration_time)
    encode.update({"exp": expire})
    return jwt.encode(encode, os.getenv("SECRET_KEY"), algorithm=os.getenv("ALGORITHM"))


def get_current_user(token: str = Depends(has_valid_token), db=DBDependency):
    """Get current user object if jwt is valid

    Args:
        token (str): jwt token
        db (Session): database session

    Returns:
        User object or invalid credentials exception
    """
    try:
        payload = jwt.decode(token, os.getenv("SECRET_KEY"), algorithms=[os.getenv("ALGORITHM")])
        user_id: int = payload.get("sub")
        if user_id is None:
            raise invalid_credentials_exception()
        user = db.query(User).get(user_id)
        if user is None:
            return invalid_credentials_exception()
        return user
    except JWTError:
        token_exception()


# Database interactive functions
def authenticate_user(email: str, password: str, db: Session) -> User | bool:
    """Search for user in database and return user object. If user doesn't exist return False

    Args:
        email (str): user's provided email
        password (str): plain password
        db (Session): database Session

    Returns:
        object: User's object if user exist
        bool: False if user doesn't exist in database
    """
    user = db.query(User).filter(User.email == email).first()
    if not user:
        return False
    if not verify_password(password, user.password):
        return False
    return user


def get_user_by_email(db: Session, email: str) -> User | None:
    """Search for user in database based on provided email.

    Args:
        db (Session): database Session
        email (str): user's provided email

    Returns:
        object: User's object if user exist
        None: If user doesn't exist
    """
    return db.query(models.User).filter(models.User.email == email).first()


def create_user(db: Session, data: schemas.RegistrationSchema) -> User:
    """Create user in database and return created object

    Args:
        db (Session): database Session
        data (schema): fields provided based on schema
            email (str): provided email for the registration
            first_name (str): user's first name
            last_name (str): user's last name
            password (str): plain password that will be stored as hash

    Returns:
        object: User object after creation
    """
    db_user = User()
    db_user.email = data.email
    db_user.first_name = data.first_name
    db_user.last_name = data.last_name
    hashed_password = get_password_hash(data.password)
    db_user.password = hashed_password
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def perform_user_logout(response: Response):
    response.delete_cookie(key=AUTH_TOKEN)
    response.status_code = status.HTTP_200_OK
    return response
