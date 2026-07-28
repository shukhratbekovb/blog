from fastapi import Depends
from typing import Annotated

from backend.dependencies.database import SessionDep
from backend.repository.comment import CommentRepository
from backend.services.comment import CommentService


async def get_comment_repo(session: SessionDep) -> CommentRepository:
    return CommentRepository(session)


CommentRepoDep = Annotated[
    CommentRepository,
    Depends(get_comment_repo),
]


async def get_comment_service(
        session: SessionDep,
        comment_repo: CommentRepoDep
) -> CommentService:
    return CommentService(session, comment_repo)


CommentServiceDep = Annotated[
    CommentService,
    Depends(get_comment_service),
]
