from fastapi import APIRouter, Depends

from typing import Annotated

from app.dependencies.__auth__ import is_active_user, get_password_hash
from app.dependencies.__database__ import AsyncSession, get_db, select, IntegrityError
from app.dependencies.__exceptions__ import bad_request, no_content, conflict, unauthorized, forbidden

from app.models.database.account import Users
from app.models.pydantic.user import UserCreate, UserUpdate, UserPublic

router = APIRouter(
    prefix="/users",
    tags=["Users"],
    responses={404: {"description": "Not found"}},
)

@router.get("/", response_model=list[UserPublic])
async def read_all_users(token: Annotated[str, Depends(is_active_user)], db: AsyncSession = Depends(get_db)) -> list[UserPublic]:
    if token.is_admin:
        result = await db.scalars(select(Users))
        response = [UserPublic(**user.__dict__) for user in result.all()]
        return response
    else:
        raise forbidden("Not Allowed. Reading all user information is restricted to Administrators only.")
    
@router.post("/", response_model=UserPublic)
async def create_user(user_data: UserCreate, db: AsyncSession = Depends(get_db)) -> UserPublic:
    user = Users(
        username=user_data.username,
        first_name=user_data.first_name,
        last_name=user_data.last_name,
        email=user_data.email,
        hashed_password=get_password_hash(user_data.password)
    )
    try:
        db.add(user)
        await db.commit()
        await db.refresh(user)
        return UserPublic(**user.__dict__)
    except IntegrityError:
        raise conflict("Email or Username already exists")

@router.get("/{user_id}", response_model=UserPublic)
async def read_user(user_id: int, token: Annotated[str, Depends(is_active_user)], db: AsyncSession = Depends(get_db)) -> UserPublic:
    if token.id == user_id or token.is_admin:
        result = await db.scalars(select(Users).where(Users.id == user_id))
        user = result.first()
        if not user:
            raise bad_request("User not found")
        return UserPublic(**user.__dict__)
    else:
        raise forbidden("Not Allowed. Reading another user's information is restricted to Administrators only.")

@router.put("/{user_id}", response_model=UserPublic)
async def update_user(user_id: int, user_data: UserUpdate, token: Annotated[str, Depends(is_active_user)], db: AsyncSession = Depends(get_db)) -> UserPublic:
    if token.id == user_id or token.is_admin:
        if user_data.is_active == True and token.is_admin == False:
            raise unauthorized("Not Allowed. Please contact admin to activate user.")
        result = await db.scalars(select(Users).where(Users.id == user_id))
        user_db = result.first()
        if not user_db:
            raise bad_request("User not found")
        
        update_data = user_data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            if value is not None:
                setattr(user_db, key, value)
        
        await db.commit()
        await db.refresh(user_db)
        return UserPublic(**user_db.__dict__)
    else:
        raise forbidden("Not Allowed. Changes to another user is restricted to Administrators only.")

@router.delete("/{user_id}")
async def delete_user(user_id: int, token: Annotated[str, Depends(is_active_user)], db: AsyncSession = Depends(get_db)):
    if token.id == user_id or token.is_admin:
        result = await db.scalars(select(Users).where(Users.id == user_id))
        user_db = result.first()
        if not user_db:
            raise bad_request("User not found")
        await db.delete(user_db)
        await db.commit()
        raise no_content("User deleted")
    else:
        raise forbidden("Not Allowed. Deleting another user is restricted to the User & Administrators only.")
        
