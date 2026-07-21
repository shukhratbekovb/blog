from dataclasses import dataclass
from datetime import datetime, date

from fastapi import Query
from pydantic import BaseModel, Field, field_validator, ConfigDict
from sqlalchemy import Select, or_

from backend.models import Post
from backend.schemas.filters import BaseFilter
from backend.schemas.tag import TagRead
from backend.schemas.user import UserBrief


@dataclass(frozen=True)
class PostFilters(BaseFilter):
    q: str | None = Query(
        default=None,
    )
    category_id: int | None = Query(
        default=None,
        ge=1
    )
    author_id: int | None = Query(
        default=None,
        ge=1
    )
    date_from: date | None = Query(
        default=None,
    )
    date_to: date | None = Query(
        default=None,
    )

    def filter(self, stmt: Select) -> Select:
        if self.q:
            pattern = f"%{self.q}%"
            stmt = stmt.where(
                or_(
                    Post.title.ilike(pattern),
                    Post.content.ilike(pattern)
                )
            )

        if self.category_id is not None:
            stmt = stmt.where(
                Post.category_id == self.category_id
            )

        if self.author_id is not None:
            stmt = stmt.where(
                Post.author_id == self.author_id
            )

        if self.date_from:
            stmt = stmt.where(
                Post.created_at >= datetime.combine(self.date_from, datetime.min.time())
            )
        if self.date_to:
            stmt = stmt.where(
                Post.created_at <= datetime.combine(self.date_to, datetime.max.time())
            )
        return stmt


class PostBase(BaseModel):
    title: str = Field(
        min_length=5,
        max_length=200,
        description="Заголовок Поста",
        examples=[
            "Как работа Pydantic?"
        ]
    )

    # slug: str = Field(
    #     min_length=3,
    #     max_length=220,
    #     pattern=r"^[a-z0-9-]+$",
    #     description="URL-friendly идентификатор"
    # )

    # @field_validator("slug", mode="after")
    # @classmethod
    # def slug_validator(cls, v: str):
    #     if not v.islower():
    #         raise ValueError("Слаг должен быть с маленькими буквами")
    #     return v

    @field_validator("title", mode="after")
    @classmethod
    def no_leading_trailing_spaces(cls, v: str):
        return v.strip()

    # @field_validator("slug", mode="after")
    # @classmethod
    # def auto_generate_slug(cls, v: str):
    #     if isinstance(v, str):
    #         return v.lower().replace(" ", "-")
    #     return v


class PostCreate(PostBase):
    content: str = Field(
        min_length=100,
        description="Содержимое поста в формате Markdown"
    )
    tag_ids: list[int] = Field(
        default_factory=list,
        max_length=5,
        description="ID Тегов"
    )
    is_published: bool = Field(
        default=False
    )
    category_id: int = Field(
        ge=1
    )


class PostUpdate(PostBase):
    content: str = Field(
        min_length=100,
        description="Содержимое поста в формате Markdown"
    )
    tag_ids: list[int] = Field(
        default_factory=list,
        max_length=5,
        description="ID Тегов"
    )
    is_published: bool = Field(
        default=False
    )


class PostBrief(PostBase):
    model_config = ConfigDict(
        from_attributes=True,
        # str_strip_whitespace=True,
        # str_to_lower=True,
        # extra="ignore"
    )
    id: int
    is_published: bool
    views_count: int = 0
    votes_count: int = 0
    created_at: datetime


class PostRead(PostBrief):
    content: str
    author: UserBrief
    tags: list[TagRead]
