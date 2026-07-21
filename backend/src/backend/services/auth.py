from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from backend.core.security import hash_password, verify_password, create_access_token, create_refresh_token, \
    decode_token
from backend.models import User
from backend.repository.user import UserRepository
from backend.schemas.auth import UserLogin, Token, RefreshToken, ChangePassword
from backend.schemas.user import UserCreate, UserUpdate


class AuthService:
    def __init__(self, session: AsyncSession, user_repo: UserRepository):
        self.session = session
        self.user_repo = user_repo

    async def register(
            self,
            body: UserCreate,
    ) -> User:
        # Есть ли такой username в БД
        exists_username = await self.user_repo.get_by_username(body.username)
        if exists_username:
            raise HTTPException(
                status_code=409,
                detail="User with that username already exists"
            )
        # Есть ли такой email в БД
        exists_email = await self.user_repo.get_by_email(body.email)
        if exists_email:
            raise HTTPException(
                status_code=409,
                detail="User with that email already exists"
            )
        # Создаем пользователя
        user = User(
            username=body.username,
            email=body.email,
            hashed_password=hash_password(body.password),
        )
        await self.user_repo.add(user)
        await self.session.commit()
        await self.session.refresh(user)

        return user

    async def login(
            self,
            body: UserLogin,
    ) -> Token:
        # Есть ли такой username в БД
        user = await self.user_repo.get_by_username(body.username)
        if not user:
            raise HTTPException(
                status_code=401,
                detail="Incorrect username or password"
            )
        # Проверяем Пароль
        if not verify_password(body.password, user.hashed_password):
            raise HTTPException(
                status_code=401,
                detail="Incorrect username or password"
            )
        if not user.is_active:
            raise HTTPException(
                status_code=403,
                detail="Inactive user"
            )
        # Создаем токен
        access_token = create_access_token(user.id)
        refresh_token = create_refresh_token(user.id)

        return Token(access_token=access_token, refresh_token=refresh_token)

    async def refresh(
            self,
            body: RefreshToken,
    ) -> Token:
        user_id = decode_token(body.refresh_token, "refresh")

        user = await self.user_repo.get_by_id(user_id)

        if not user:
            raise HTTPException(
                status_code=401,
                detail="Invalid Credentials"
            )

        if not user.is_active:
            raise HTTPException(
                status_code=403,
                detail="Inactive user"
            )

        access_token = create_access_token(user.id)
        refresh_token = create_refresh_token(user.id)
        return Token(access_token=access_token, refresh_token=refresh_token)

    async def change_password(
            self,
            user: User,
            body: ChangePassword
    ) -> None:
        if not verify_password(body.old_password, user.hashed_password):
            raise HTTPException(
                status_code=401,
                detail="Incorrect username or password"
            )

        hashed_password = hash_password(body.new_password)
        user.hashed_password = hashed_password

        await self.user_repo.update(user)
        await self.session.commit()

    async def update_me(
            self,
            user: User,
            body: UserUpdate
    ) -> None:
        # vladislav
        # vladislav@example.com

        # vladislav
        # vladislav@example.com

        exists_username = await self.user_repo.get_by_username(body.username)
        if exists_username and exists_username.username != user.username:
            raise HTTPException(
                status_code=409,
                detail="User with that username already exists"
            )
        # Есть ли такой email в БД
        exists_email = await self.user_repo.get_by_email(body.email)
        if exists_email and exists_email.email != user.email:
            raise HTTPException(
                status_code=409,
                detail="User with that email already exists"
            )

        user.username = body.username
        user.email = body.email
        user.bio = body.bio

        await self.user_repo.update(user)
        await self.session.commit()
