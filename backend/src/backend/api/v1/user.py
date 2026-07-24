from fastapi import APIRouter, Depends

from backend.dependencies.auth import CurrentUserDep
from backend.dependencies.user import UserServiceDep
from backend.schemas.post import PostBrief
from backend.schemas.user import UserRead, UserBrief, UserFilter, UserUpdate
from backend.schemas.pagination import Page, PaginationParams

router = APIRouter(
    prefix="/users",
    tags=["users"],
)


@router.get(
    "/",
    response_model=Page[UserBrief]
)
async def list_users(
        service: UserServiceDep,
        filters: UserFilter = Depends(),
        pagination: PaginationParams = Depends(),
):
    users = await service.list_users(filters, pagination)
    return users


@router.get(
    "/me/bookmarks",
    response_model=Page[PostBrief]
)
async def get_my_bookmarks(
        current_user: CurrentUserDep,
        service: UserServiceDep,
        pagination: PaginationParams = Depends(),
):
    posts = await service.get_bookmarked_posts(current_user, pagination)
    return posts


@router.get(
    "/me",
    response_model=UserRead
)
async def get_me(
        current_user: CurrentUserDep
):
    return current_user


@router.patch(
    "/me"
)
async def update_me(
        body: UserUpdate,
        current_user: CurrentUserDep,
        service: UserServiceDep
):
    await service.update_me(current_user, body)


@router.get(
    "/{user_id}",
    response_model=UserRead
)
async def get_user(
        user_id: int,
        service: UserServiceDep
):
    user = await service.get_user(user_id)
    return user


@router.get(
    "/{user_id}/posts",
    response_model=Page[PostBrief]
)
async def list_user_posts(
        user_id: int,
        service: UserServiceDep,
        pagination: PaginationParams = Depends(),
):
    posts = await service.get_user_posts(pagination=pagination, user_id=user_id)
    return posts
