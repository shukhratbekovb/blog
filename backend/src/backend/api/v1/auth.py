from fastapi import APIRouter
from starlette import status

from backend.dependencies.auth import AuthServiceDep, CurrentUserDep
from backend.schemas.auth import UserLogin, ChangePassword, RefreshToken, Token
from backend.schemas.user import UserCreate, UserRead

router = APIRouter(
    prefix="/auth",
    tags=["auth"]
)


@router.post(
    "/register",
    response_model=UserRead
)
async def register_user(
        body: UserCreate,
        service: AuthServiceDep
):
    user = await service.register(body)
    return user


@router.post(
    "/login",
    response_model=Token
)
async def login_user(
        body: UserLogin,
        service: AuthServiceDep
):
    token = await service.login(body)
    return token


@router.post(
    "/refresh",
    response_model=Token
)
async def refresh_token(
        body: RefreshToken,
        service: AuthServiceDep
):
    token = await service.refresh(body)
    return token


@router.post(
    "/change-password",
    status_code=status.HTTP_200_OK,
)
async def change_password(
        body: ChangePassword,
        current_user: CurrentUserDep,
        service: AuthServiceDep
):
    await service.change_password(current_user, body)
