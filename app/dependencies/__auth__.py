from datetime import datetime, timedelta, timezone
from typing import Annotated, Optional

from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer

import jwt
from jwt.exceptions import InvalidTokenError
from passlib.context import CryptContext

from app.dependencies.__config__ import settings
from app.dependencies.__database__ import AsyncSession, get_db, select
from app.dependencies.__exceptions__ import bad_request, unauthorized
from app.dependencies.__redis__ import redis_manager

from app.models.database.account import Users

from app.models.pydantic.user import UserPublic
from app.models.pydantic.token import TokenData

ALGORITHM = settings.algorithm
SECRET_KEY = settings.secret_key

bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl='/auth/token')

def verify_password(plain_password, hashed_password):
    return bcrypt_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return bcrypt_context.hash(password)

async def get_user(db: AsyncSession, username: str):
    query = await db.scalars(select(Users).where(Users.username == username))
    return query.first()
    
async def authenticate_user(db: AsyncSession, username: str, password: str):
    user = await get_user(db, username)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user

async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)], db: AsyncSession = Depends(get_db)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if not username:
            raise unauthorized("Could not validate credentials.")
        token_data = TokenData(username=username)
    except jwt.ExpiredSignatureError:
        raise unauthorized("Expired Token. Please sign in again.")
    except InvalidTokenError:
        raise bad_request("Invalid Token. Please sign in again.")
    user = await get_user(db, username=token_data.username)
    if user is None:
        raise unauthorized("User not found. Please make sure your username is correct.")
    return user

async def is_active_user(current_user: Annotated[UserPublic, Depends(get_current_user)]):
    if not current_user.is_active:
        raise unauthorized("Not Allowed. Please contact admin to activate user.")
    return current_user

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(hours=settings.JWT_EXPIRE)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

async def blacklist_token(token: str):
    await redis_manager.set(token, "blacklisted")

async def is_token_blacklisted(token: str) -> bool:
    return await redis_manager.exists(token)