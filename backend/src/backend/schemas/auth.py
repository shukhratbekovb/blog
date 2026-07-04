from pydantic import BaseModel, Field, EmailStr, field_validator, model_validator


class UserCreate(BaseModel):
    username: str = Field(
        min_length=3,
        max_length=100,
        pattern=r"^[a-zA-Z0-9-]+$"
    )
    email: EmailStr
    password: str = Field(
        min_length=8
    )

    @field_validator("password", mode="after")
    @classmethod
    def password_validator(cls, v: str):
        errors = []
        if not (any(c.islower() for c in v)):
            errors.append("Хотя бы одна маленькая буква")
        if not (any(c.isupper() for c in v)):
            errors.append("Хотя бы одна заглавная буква")
        if not (any(c.isdigit() for c in v)):
            errors.append("Хотя бы одна цифра")
        if errors:
            raise ValueError(f"Пароль должен содержать: {', '.join(errors)}")
        return v


class ChangePassword(BaseModel):
    old_password: str
    new_password: str

    @field_validator("old_password", "new_password", mode="after")
    @classmethod
    def password_validator(cls, v: str):
        errors = []
        if not (any(c.islower() for c in v)):
            errors.append("Хотя бы одна маленькая буква")
        if not (any(c.isupper() for c in v)):
            errors.append("Хотя бы одна заглавная буква")
        if not (any(c.isdigit() for c in v)):
            errors.append("Хотя бы одна цифра")
        if errors:
            raise ValueError(f"Пароль должен содержать: {', '.join(errors)}")
        return v

    @model_validator(mode="after")
    def password_match(self):
        if self.old_password == self.new_password:
            raise ValueError("Старый пароль не должен совпадать с новым")
        return self

class UserBrief(BaseModel):
    username: str
    email: EmailStr