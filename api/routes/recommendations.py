"""Recommendation endpoints."""
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from api.database import get_db
from api.models import UserRating, SessionModel
from api.schemas import RecommendationResponse, RecommendationItem
from api.services.joke_catalog import JokeCatalog
from api.services.model_loader import ModelLoader, InferenceService
from config import settings
import numpy as np
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/recommendations", tags=["Recommendations"])


@router.get("/{user_id}", response_model=RecommendationResponse)
async def get_recommendations(
    user_id: int,
    model: str = Query(default="pmf", description="Model type: pmf or autoencoder"),
    top_k: int = Query(default=10, ge=1, le=100, description="Number of recommendations"),
    db: Session = Depends(get_db),
):
    """Get recommendations for a user.
    
    Args:
        user_id: User ID
        model: Model type to use ('pmf' or 'autoencoder')
        top_k: Number of top recommendations to return
        
    Returns:
        List of top-k jokes with predicted ratings
    """
    
    if model not in ["pmf", "autoencoder"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unknown model type: {model}. Use 'pmf' or 'autoencoder'.",
        )
    
    try:
        # Load model
        logger.info(f"Loading {model} model for recommendations...")
        model_data = ModelLoader.get_model(model)
        
        # Get user's existing ratings
        user_ratings_db = db.query(UserRating).filter(
            UserRating.user_id == user_id
        ).all()
        user_ratings = {r.joke_id: r.rating for r in user_ratings_db}
        
        # Determine number of items from model or splits
        if model == "pmf":
            n_items = model_data['U'].shape[0] if 'U' in model_data else 100
            # PMF uses V for items, so n_items = V.shape[0]
            n_items = model_data['V'].shape[0]
            
            recommendations = InferenceService.get_pmf_recommendations(
                model_data=model_data,
                user_id=user_id,
                user_ratings=user_ratings,
                n_items=n_items,
                top_k=top_k,
            )
        
        elif model == "autoencoder":
            # Load splits to get n_items and train_filled for autoencoder
            splits_path = settings.processed_data_dir / f"seed_{settings.default_seed}" / "splits.npz"
            if not splits_path.exists():
                raise FileNotFoundError(f"Splits file not found: {splits_path}")
            
            splits_data = np.load(splits_path, allow_pickle=True)
            train_filled = splits_data['train_filled'].astype(np.float32)
            n_items = train_filled.shape[1]
            
            recommendations = InferenceService.get_autoencoder_recommendations(
                model_data=model_data,
                user_id=user_id,
                user_ratings=user_ratings,
                train_filled=train_filled,
                top_k=top_k,
            )
        
        # Format response
        rec_items = []
        for rank, (joke_id, score) in enumerate(recommendations):
            joke_text = JokeCatalog.get_joke_text(joke_id)
            rec_items.append(
                RecommendationItem(
                    joke_id=joke_id,
                    joke_text=joke_text,
                    predicted_rating=float(score),
                    rank=rank + 1,
                )
            )
        
        return RecommendationResponse(
            user_id=user_id,
            model=model,
            top_k=len(rec_items),
            recommendations=rec_items,
            generated_at=datetime.utcnow(),
        )
    
    except FileNotFoundError as e:
        logger.error(f"Model or data file not found: {e}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Model or data file not found: {str(e)}",
        )
    
    except Exception as e:
        logger.error(f"Error generating recommendations: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating recommendations: {str(e)}",
        )
