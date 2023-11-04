import base64
import re
from datetime import datetime, timedelta
from typing import Match

from fastapi import Request, HTTPException
from jose import jwt, ExpiredSignatureError, JWTError
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from starlette import status

from auth import schemas
from auth.dependencies import ValidToken
from auth.exceptions import invalid_credentials_exception, token_exception, user_inactive_exception
from core.constants import ACTIVATE_ACCOUNT_SUBJECT
from core.dependencies import DBDependency
from core.models import User, UserDetail
from src.config import SECRET_KEY, ALGORITHM, TOKEN_EXP_MINUTES

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
    """Create authentication jwt token for a specific user

    Args:
        user_id (int): user id for which jwt token will be created

    Returns:
        jwt token for a specific user
    """
    token_creation_time = datetime.utcnow()
    user_id_base64 = base64.b64encode(str(user_id).encode('utf-8')).decode('utf-8')
    encode = {"sub": user_id_base64, "iat": token_creation_time}
    expire = token_creation_time + timedelta(minutes=float(TOKEN_EXP_MINUTES))
    encode.update({"exp": expire})
    return jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHM)


def get_current_user(token: str = ValidToken, db=DBDependency):
    """Get current user object if jwt is valid

    Args:
        token (str): jwt token
        db (Session): database session

    Returns:
        User object or invalid credentials exception
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=ALGORITHM)
        user_id_base64 = payload.get("sub")
        user_id = int(base64.b64decode(user_id_base64).decode('utf-8'))
        if user_id is None:
            raise invalid_credentials_exception()
        user: User = db.query(User).get(user_id)
        if user is None:
            raise invalid_credentials_exception()
        return user
    except ExpiredSignatureError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Token expired")
    except JWTError:
        token_exception()


def get_current_active_user(token: str):
    current_user = get_current_user(token)
    if not current_user.is_active:
        raise user_inactive_exception()


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


def check_account_existence_by_email(db: Session, email: str) -> bool:
    """Check if user exist based on provided email

    Args:
        db (Session): database session
        email (str): provided email
    Returns:
        bool: True if user object exist in the database or None
    """
    return db.query(User).filter(User.email == email).first()


async def create_user(request: Request, db: Session,
                      data: schemas.RegistrationSchemaUser) -> User.user_id | None:
    """ If user doesn't already exist, create user in database, send verification email and
    return created object id.
    Also create UserDetail.
    If user already exist, return None.

    Args:
        request (Request): request object to construct verification url
        db (Session): database Session
        data (schema): fields provided based on schema
            email (str): provided email for the registration
            first_name (str): user's first name
            last_name (str): user's last name
            password (str): plain password that will be stored as hash

    Returns:
        object id | None: User object id or None
    """
    account_exist: bool = check_account_existence_by_email(db, data.email)
    if account_exist:
        return None
    db_user = User()
    db_user.email = data.email
    db_user.first_name = data.first_name
    db_user.last_name = data.last_name
    hashed_password = get_password_hash(data.password)
    db_user.password = hashed_password
    db.add(db_user)
    db.commit()
    # create user details
    user_detail = UserDetail(user_id=db_user.user_id)
    db.add(user_detail)
    db.commit()
    db.refresh(db_user)
    token = create_auth_token(db_user.user_id)
    base_url = str(request.base_url)
    verification_url = f"{base_url}auth/verify_email?token={token}"
    expiration_time = datetime.utcnow() + timedelta(minutes=int(TOKEN_EXP_MINUTES))
    await db_user.email_user(subject=ACTIVATE_ACCOUNT_SUBJECT,
                             body={"first_name": db_user.first_name, "url": verification_url,
                                   "expire_at": expiration_time.strftime("%Y-%m-%d %H:%M:%S")},
                             template_name="activation_email.html")
    return db_user.user_id


def activate_user(user: User, db: Session) -> None:
    user.is_active = True
    db.commit()
    return
