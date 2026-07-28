from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from backend.models import Comment
from backend.repository.comment import CommentRepository
from backend.schemas.comment import CommentCreate, CommentUpdate
from backend.utils.comment_tree import build_comment_tree


class CommentService:
    def __init__(
            self,
            session: AsyncSession,
            comment_repo: CommentRepository,
    ):
        self.session = session
        self.comment_repo = comment_repo

    def _validate_comment(self, post_id: int, comment: Comment) -> None:
        if comment.post_id != post_id:
            raise HTTPException(
                status_code=404,
                detail="Comment not found"
            )

    async def get_or_404(
            self,
            post_id: int,
            comment_id: int
    ) -> Comment:
        comment = await self.comment_repo.get_by_id(comment_id)
        if not comment:
            raise HTTPException(status_code=404, detail="Comment not found")
        self._validate_comment(post_id, comment)
        return comment

    async def create(
            self,
            post_id: int,  # 1
            author_id: int,
            body: CommentCreate,
    ) -> Comment:
        if body.parent_id:
            parent = await self.comment_repo.get_by_id(body.parent_id)  # 2
            if parent.post_id != post_id:
                raise HTTPException(
                    status_code=400,
                    detail="Родительский комментарий привязан к другому посту"
                )
        comment = Comment(
            parent_id=post_id,
            author_id=author_id,
            content=body.content,
            post_id=post_id
        )
        await self.comment_repo.add(comment)
        await self.session.commit()
        comment = await self.comment_repo.get_by_id(comment.id)
        return comment

    async def update(
            self,
            post_id: int,
            comment_id: int,
            current_user_id: int,
            body: CommentUpdate,
    ) -> None:
        comment = await self.comment_repo.get_by_id(comment_id)
        if not comment:
            raise HTTPException(status_code=404, detail="Comment not found")
        self._validate_comment(post_id, comment)
        if comment.author_id != current_user_id:
            raise HTTPException(
                status_code=403,
                detail="Ты можешь обновлять только свои комментарии"
            )
        comment.content = body.content
        await self.comment_repo.update(comment)
        await self.session.commit()

    async def delete(
            self,
            post_id: int,
            comment_id: int,
            current_user_id: int
    ) -> None:
        comment = await self.comment_repo.get_by_id(comment_id)
        if not comment:
            raise HTTPException(status_code=404, detail="Comment not found")
        self._validate_comment(post_id, comment)
        if comment.author_id != current_user_id:
            raise HTTPException(
                status_code=403,
                detail="Ты можешь удалять только свои комментарии"
            )
        await self.comment_repo.delete(comment)
        await self.session.commit()

    async def get_tree(
            self,
            post_id: int
    ) -> list[Comment]:
        comments = await self.comment_repo.get_by_post(post_id)
        return build_comment_tree(comments)
