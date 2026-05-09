"""User rating management routes."""
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from api.database import get_db
from api.models import UserRating, SessionModel
from api.schemas import RatingCreateRequest, RatingResponse, UserRatingsResponse

router = APIRouter(prefix="/api/ratings", tags=["Ratings"])


@router.post("", response_model=RatingResponse, status_code=status.HTTP_201_CREATED)
async def submit_rating(
    request: RatingCreateRequest,
    db: Session = Depends(get_db),
):
    """Submit a user rating for a joke."""
    # Validate session exists
    session = db.query(SessionModel).filter(
        SessionModel.session_id == request.session_id
    ).first()
    
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Session {request.session_id} not found",
        )
    
    if not session.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Session is no longer active",
        )
    
    # Verify user_id matches session
    if session.user_id != request.user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User ID does not match session",
        )
    
    # Check if rating already exists
    existing_rating = db.query(UserRating).filter(
        UserRating.user_id == request.user_id,
        UserRating.joke_id == request.joke_id,
    ).first()
    
    if existing_rating:
        # Update existing rating
        existing_rating.rating = request.rating
        existing_rating.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(existing_rating)
        return RatingResponse(
            user_id=existing_rating.user_id,
            joke_id=existing_rating.joke_id,
            rating=existing_rating.rating,
            created_at=existing_rating.created_at,
            updated_at=existing_rating.updated_at,
        )
    
    # Create new rating
    new_rating = UserRating(
        session_id=request.session_id,
        user_id=request.user_id,
        joke_id=request.joke_id,
        rating=request.rating,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )
    
    db.add(new_rating)
    db.commit()
    db.refresh(new_rating)
    
    return RatingResponse(
        user_id=new_rating.user_id,
        joke_id=new_rating.joke_id,
        rating=new_rating.rating,
        created_at=new_rating.created_at,
        updated_at=new_rating.updated_at,
    )


@router.get("/{user_id}/{joke_id}", response_model=RatingResponse)
async def get_rating(
    user_id: int,
    joke_id: int,
    db: Session = Depends(get_db),
):
    """Get a user's rating for a specific joke."""
    rating = db.query(UserRating).filter(
        UserRating.user_id == user_id,
        UserRating.joke_id == joke_id,
    ).first()
    
    if not rating:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Rating for user {user_id}, joke {joke_id} not found",
        )
    
    return RatingResponse(
        user_id=rating.user_id,
        joke_id=rating.joke_id,
        rating=rating.rating,
        created_at=rating.created_at,
        updated_at=rating.updated_at,
    )


@router.get("/{user_id}", response_model=UserRatingsResponse)
async def get_user_ratings(
    user_id: int,
    db: Session = Depends(get_db),
):
    """Get all ratings submitted by a user."""
    ratings = db.query(UserRating).filter(
        UserRating.user_id == user_id,
    ).all()
    
    rating_responses = [
        RatingResponse(
            user_id=r.user_id,
            joke_id=r.joke_id,
            rating=r.rating,
            created_at=r.created_at,
            updated_at=r.updated_at,
        )
        for r in ratings
    ]
    
    return UserRatingsResponse(user_id=user_id, ratings=rating_responses)
