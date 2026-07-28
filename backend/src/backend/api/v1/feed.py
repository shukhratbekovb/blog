from enum import StrEnum

from fastapi import APIRouter

router = APIRouter(
    prefix="/feed",
)


class FeedType(StrEnum):
    new = "new"
    top = "top"
    hot = "hot"


@router.get("/{feed_type}")
async def get_feed(
        feed_type: FeedType
):
    return {"type": feed_type, "posts": []}
