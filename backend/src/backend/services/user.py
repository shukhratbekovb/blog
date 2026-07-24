from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from backend.models import User
from backend.repository.post import PostRepository
from backend.repository.user import UserRepository
from backend.schemas.pagination import PaginationParams
from backend.schemas.post import PostFilters
from backend.schemas.user import UserFilter, UserUpdate


class UserService:
    def __init__(
            self,
            session: AsyncSession,
            user_repo: UserRepository,
            post_repo: PostRepository
    ) -> None:
        self.session = session
        self.user_repo = user_repo
        self.post_repo = post_repo

    async def list_users(
            self,
            filters: UserFilter,
            pagination: PaginationParams
    ):
        users = await self.user_repo.get_all(filters=filters, pagination=pagination)
        return users

    async def get_user(self, user_id: int) -> User:
        user = await self.user_repo.get_by_id(user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        return user

    async def get_user_posts(
            self,
            user_id: int,
            pagination: PaginationParams
    ):
        user = await self.user_repo.get_by_id(user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        posts = await self.post_repo.get_all(filters=PostFilters(author_id=user_id), pagination=pagination)
        return posts

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

    async def get_bookmarked_posts(
            self,
            user: User,
            pagination: PaginationParams
    ):
        posts = await self.post_repo.get_bookmarked_user_posts(user.id, pagination)
        return posts
