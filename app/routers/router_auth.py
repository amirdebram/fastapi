from datetime import timedelta
from typing import Annotated

from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm

from app.dependencies.__auth__ import authenticate_user, create_access_token
from app.dependencies.__config__ import settings
from app.dependencies.__database__ import AsyncSession, get_db
from app.dependencies.__exceptions__ import unauthorized
from app.models.pydantic.token import Token

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"],
    responses={401: {"description": "Not authorized"}, 404: {"description": "Resource not found"}}
)

@router.post("/token", response_model=Token)
async def login_for_access_token(form_data: Annotated[OAuth2PasswordRequestForm, Depends()], db: AsyncSession = Depends(get_db)) -> Token:
    user = await authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise unauthorized("Could not validate credentials")
    access_token_expires = timedelta(hours=settings.JWT_EXPIRE)
    access_token = create_access_token(data={"sub": user.username, "userid": int(user.id)}, expires_delta=access_token_expires)
    return Token(access_token=access_token, token_type="bearer")