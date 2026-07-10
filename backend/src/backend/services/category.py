from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from backend.models import Category
from backend.repository.category import CategoryRepository
from backend.schemas.category import CategoryCreate, CategoryUpdate
from backend.utils.slug import slug_generator


class CategoryService:
    def __init__(
            self,
            session: AsyncSession,
            category_repo: CategoryRepository
    ):
        self.session = session
        self.category_repo = category_repo

    async def get_all(self) -> list[Category]:
        categories = await self.category_repo.get_all()
        return categories

    async def create(
            self,
            body: CategoryCreate
    ) -> Category:
        # Мы из название категории генерируем слаг
        slug = slug_generator.generate(body.name)
        # Проверить сгенерированый слаг на наличие в БД
        existing = await self.category_repo.get_by_slug(
            slug
        )
        # Если есть ошибка
        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Category with slug {slug} already exists"
            )
        # Если нет то создаем категорию
        category = await self.category_repo.add(
            name=body.name,
            slug=slug,
            description=body.description
        )
        await self.session.commit()
        return category

    async def get_or_404(
            self,
            category_slug: str,
    ) -> Category:
        category = await self.category_repo.get_by_slug(category_slug)
        if not category:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Category with slug {category_slug} not found"
            )
        return category

    async def update(
            self,
            category_id: int,
            body: CategoryUpdate
    ) -> None:
        category = await self.category_repo.get_by_id(category_id)
        if not category:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Category with id {category_id} not found"
            )
        await self.category_repo.update(
            category_id,
            name=body.name,
            description=body.description
        )
        await self.session.commit()

    async def delete(
            self,
            category_id: int
    ) -> None:
        category = await self.category_repo.get_by_id(category_id)
        if not category:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Category with id {category_id} not found"
            )
        await self.category_repo.delete(category_id)
        await self.session.commit()
