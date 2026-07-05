from datetime import datetime

from pydantic import BaseModel, Field, EmailStr, field_validator, model_validator, ConfigDict


def validate_password(password: str) -> str:
    errors = []
    if not (any(c.islower() for c in password)):
        errors.append("Хотя бы одна маленькая буква")
    if not (any(c.isupper() for c in password)):
        errors.append("Хотя бы одна заглавная буква")
    if not (any(c.isdigit() for c in password)):
        errors.append("Хотя бы одна цифра")
    if errors:
        raise ValueError(f"Пароль должен содержать: {', '.join(errors)}")
    return password


class UserBase(BaseModel):
    username: str = Field(
        min_length=3,
        max_length=100,
        pattern=r"^[a-zA-Z0-9-]+$"
    )


class UserCreate(UserBase):
    email: EmailStr
    password: str = Field(
        min_length=8
    )

    @field_validator("password", mode="after")
    @classmethod
    def password_validator(cls, v: str):
        return validate_password(v)


class UserUpdate(UserBase):
    email: EmailStr
    bio: str | None = Field(default=None, max_length=512)


class UserBrief(UserBase):
    model_config = ConfigDict(
        from_attributes=True
    )

    id: int
    karma: int
    avatar_url: str | None = None


class UserRead(UserBrief):
    email: EmailStr
    bio: str | None = None
    created_at: datetime
