from fastapi import APIRouter, Query
from typing import List, Optional, Dict, Any

from services.social_media_service import social_media_service
from models.social_media_schemas import PaginatedPosts, Post


router = APIRouter()


@router.get("/", response_model=PaginatedPosts)
async def read_posts(
    page: int = Query(1, ge=1),
    per_page: int = Query(10, ge=1, le=100),
    platform: Optional[str] = Query(None),
    user_handle: Optional[str] = Query(None),
    sentiment: Optional[str] = Query(None),
    category: Optional[str] = Query(None),
    date_from: Optional[str] = Query(None),
    date_to: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
):
    """Get social media posts with filtering."""

    return await social_media_service.get_posts(
        page=page,
        per_page=per_page,
        platform=platform,
        user_handle=user_handle,
        sentiment=sentiment,
        category=category,
        date_from=date_from,
        date_to=date_to,
        search=search,
    )


@router.get("/{post_id}", response_model=Post)
async def read_post(post_id: str):
    """Get a specific social media post."""

    return await social_media_service.get_post(
        post_id=post_id
    )


@router.get("/platforms/list", response_model=List[str])
async def read_platforms():
    """Get available social media platforms."""

    return await social_media_service.get_platforms()


@router.get(
    "/sentiments/list",
    response_model=List[Dict[str, Any]]
)
async def read_sentiments(
    date_from: Optional[str] = Query(None),
    date_to: Optional[str] = Query(None),
):
    """Get sentiment distribution."""

    return await social_media_service.get_sentiments(
        date_from=date_from,
        date_to=date_to,
    )


@router.get(
    "/users/top",
    response_model=List[Dict[str, Any]]
)
async def read_top_users(
    platform: Optional[str] = Query(None),
    limit: int = Query(10, ge=1, le=50),
    date_from: Optional[str] = Query(None),
    date_to: Optional[str] = Query(None),
):
    """Get top users by post count."""

    return await social_media_service.get_top_users(
        platform=platform,
        limit=limit,
        date_from=date_from,
        date_to=date_to,
    )


@router.get(
    "/categories/list",
    response_model=List[Dict[str, Any]]
)
async def read_categories(
    date_from: Optional[str] = Query(None),
    date_to: Optional[str] = Query(None),
):
    """Get categories with post counts."""

    return await social_media_service.get_categories(
        date_from=date_from,
        date_to=date_to,
    )


@router.get(
    "/users/sentiment",
    response_model=List[Dict[str, Any]]
)
async def read_user_sentiment(
    limit: int = Query(10, ge=1, le=50),
    platform: Optional[str] = Query(None),
    date_from: Optional[str] = Query(None),
    date_to: Optional[str] = Query(None),
):
    """Get users with sentiment breakdown."""

    return await social_media_service.get_user_sentiment(
        limit=limit,
        platform=platform,
        date_from=date_from,
        date_to=date_to,
    )


@router.get(
    "/categories/sentiment",
    response_model=List[Dict[str, Any]]
)
async def read_category_sentiment(
    date_from: Optional[str] = Query(None),
    date_to: Optional[str] = Query(None),
):
    """Get sentiment distribution by category."""

    return await social_media_service.get_category_sentiment(
        date_from=date_from,
        date_to=date_to,
    )


@router.get(
    "/topic/trends",
    response_model=List[Dict[str, Any]]
)
async def read_trending_topics(
    limit: int = Query(10, ge=1, le=50),
    date_from: Optional[str] = Query(None),
    date_to: Optional[str] = Query(None),
):
    """Get trending topics."""

    return await social_media_service.get_trending_topics(
        date_from=date_from,
        date_to=date_to,
        limit=limit,
    )


@router.get(
    "/trends/time",
    response_model=List[Dict[str, Any]]
)
async def read_sentiment_over_time(
    platform: Optional[str] = Query(None),
    date_from: Optional[str] = Query(None),
    date_to: Optional[str] = Query(None),
):
    """Get sentiment trends over time."""

    return await social_media_service.get_sentiment_over_time(
        date_from=date_from,
        date_to=date_to,
        platform=platform,
    )


@router.get(
    "/posts/influential",
    response_model=List[Dict[str, Any]]
)
async def read_influential_posts(
    sentiment: Optional[str] = Query(None),
    limit: int = Query(5, ge=1, le=20),
    date_from: Optional[str] = Query(None),
    date_to: Optional[str] = Query(None),
):
    """Get influential posts."""

    return await social_media_service.get_influential_posts(
        sentiment=sentiment,
        limit=limit,
        date_from=date_from,
        date_to=date_to,
    )


@router.get(
    "/engagement/stats",
    response_model=Dict[str, Any]
)
async def read_engagement_stats(
    date_from: Optional[str] = Query(None),
    date_to: Optional[str] = Query(None),
):
    """Get engagement statistics."""

    return await social_media_service.get_engagement_stats(
        date_from=date_from,
        date_to=date_to,
    )


@router.post("/session/setup")
async def setup_browser_session():
    """
    Browser-based social media login is disabled in the
    lightweight local version because Playwright/Browser Use
    is not required for the main news and podcast pipeline.
    """

    return {
        "status": "disabled",
        "message": (
            "Browser-based social media authentication "
            "is disabled in the lightweight local version."
        ),
    }