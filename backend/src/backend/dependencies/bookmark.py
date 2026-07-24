from typing import Annotated

from fastapi import Depends

from backend.dependencies.database import SessionDep
from backend.repository.bookmark import BookmarkRepository


async def get_bookmark_repo(session: SessionDep) -> BookmarkRepository:
    return BookmarkRepository(session)

BookmarkRepoDep = Annotated[
    BookmarkRepository,
    Depends(get_bookmark_repo)
]