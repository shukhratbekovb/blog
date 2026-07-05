from pydantic import BaseModel, field_validator, model_validator

from backend.schemas.user import validate_password


class RefreshToken(BaseModel):
    refresh_token: str


class Token(RefreshToken):
    access_token: str


class UserLogin(BaseModel):
    username: str
    password: str


class ChangePassword(BaseModel):
    old_password: str
    new_password: str

    @field_validator("old_password", "new_password", mode="after")
    @classmethod
    def password_validator(cls, v: str):
        return validate_password(v)

    @model_validator(mode="after")
    def password_match(self):
        if self.old_password == self.new_password:
            raise ValueError("Старый пароль не должен совпадать с новым")
        return self
