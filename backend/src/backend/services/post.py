from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from backend.models import Post
from backend.repository.post import PostRepository
from backend.repository.tag import TagRepository
from backend.schemas.pagination import PaginationParams
from backend.schemas.post import PostCreate, PostUpdate, PostFilters
from backend.utils.slug import slug_generator


class PostService:
    def __init__(
            self,
            session: AsyncSession,
            post_repo: PostRepository,
            tag_repo: TagRepository
    ):
        self.session = session
        self.post_repo = post_repo
        self.tag_repo = tag_repo

    async def _make_unique_slug(self, base_slug: str) -> str:
        slug = base_slug
        counter = 1
        while await self.post_repo.get_by_slug(slug):
            slug = f'{base_slug}-{counter}'
            counter += 1
        return slug

    async def create(
            self,
            body: PostCreate,
            author_id: int
    ) -> Post:
        base_slug = slug_generator.generate(body.title)
        slug = await self._make_unique_slug(base_slug)

        tags = await self.post_repo.get_tags_by_ids(body.tag_ids)

        post = Post(
            title=body.title,
            slug=slug,
            content=body.content,
            author_id=author_id,
            category_id=body.category_id,
            is_published=body.is_published,
            tags=tags
        )
        post = await self.post_repo.add(post)
        for tag in tags:
            await self.tag_repo.sync_posts_count(tag.id)

        await self.session.commit()

        return post

    async def update(
            self,
            post_id: int,
            body: PostUpdate,
            current_user_id: int
    ) -> None:
        post = await self.get_or_404(post_id)

        if post.author_id != current_user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail='You can only edit your own posts'
            )

        update_data = body.model_dump(exclude_unset=True)

        if "title" in update_data:
            base_slug = slug_generator.generate(update_data["title"])
            update_data["slug"] = await self._make_unique_slug(base_slug)

        if "tag_ids" in update_data:
            tag_ids = update_data.pop("tag_ids")
            post.tags = await self.post_repo.get_tags_by_ids(tag_ids or [])

        for field, value in update_data.items():
            setattr(post, field, value)

        await self.post_repo.update(post)
        await self.session.commit()

    async def get_or_404(self, post_id: int) -> Post:
        post = await self.post_repo.get_by_id(post_id)

        if not post:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail='Post not found'
            )

        return post

    async def delete(
            self,
            post_id: int,
            current_user_id: int
    ) -> None:
        post = await self.get_or_404(post_id)
        if post.author_id != current_user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail='You can only delete your own posts'
            )
        await self.post_repo.delete(post)
        await self.session.commit()

    async def view_or_404(self, slug: str) -> Post:
        post = await self.post_repo.get_by_slug(slug)
        if not post or not post.is_published:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail='Post not found'
            )
        await self.post_repo.increment_views(post)
        await self.session.commit()
        return post

    async def get_all(
            self,
            filters: PostFilters,
            pagination: PaginationParams
    ):
        posts = await self.post_repo.get_all(
            filters=filters,
            pagination=pagination
        )
        return posts

    async def publish(self, current_user_id: int, post: Post):
        if post.author_id != current_user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail='You can only publish your own posts'
            )
        post.is_published = True
        await self.post_repo.update(post)
        await self.session.commit()
