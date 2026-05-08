"""Joke metadata endpoints."""
from fastapi import APIRouter, HTTPException, status
from api.schemas import JokeItem, JokeListResponse
from api.services.joke_catalog import JokeCatalog
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/jokes", tags=["Jokes"])


@router.get("", response_model=JokeListResponse)
async def list_jokes(limit: int | None = None):
    """List jokes with text content."""
    try:
        jokes = JokeCatalog.list_jokes(limit=limit)
        return JokeListResponse(jokes=[JokeItem(**joke) for joke in jokes])
    except FileNotFoundError as e:
        logger.error(f"Joke catalog not found: {e}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )
    except Exception as e:
        logger.error(f"Error listing jokes: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error listing jokes: {e}",
        )


@router.get("/{joke_id}", response_model=JokeItem)
async def get_joke(joke_id: int):
    """Retrieve joke text by joke ID."""
    joke_text = JokeCatalog.get_joke_text(joke_id)
    if joke_text is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Joke {joke_id} not found",
        )
    return JokeItem(joke_id=joke_id, joke_text=joke_text)
