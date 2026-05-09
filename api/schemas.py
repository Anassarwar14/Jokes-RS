"""Pydantic schemas for request/response validation."""
from datetime import datetime
from pydantic import BaseModel, Field


# Session Schemas
class SessionCreateRequest(BaseModel):
    """Request to create a new session."""
    pass  # No required fields for anonymous ephemeral sessions


class SessionResponse(BaseModel):
    """Response containing session info."""
    session_id: str
    user_id: int
    created_at: datetime
    last_active_at: datetime
    is_active: bool


# Rating Schemas
class RatingCreateRequest(BaseModel):
    """Request to submit a user rating."""
    session_id: str
    user_id: int = Field(..., ge=0, description="User ID")
    joke_id: int = Field(..., ge=0, description="Joke ID")
    rating: float = Field(..., ge=-10, le=10, description="Rating from -10 to 10 (Jester scale)")


class RatingResponse(BaseModel):
    """Response containing a stored rating."""
    user_id: int
    joke_id: int
    rating: float
    created_at: datetime
    updated_at: datetime


class UserRatingsResponse(BaseModel):
    """Response containing all ratings for a user."""
    user_id: int
    ratings: list[RatingResponse]


# Recommendation Schemas
class RecommendationItem(BaseModel):
    """Single recommendation result."""
    joke_id: int
    joke_text: str | None = Field(None, description="Optional joke text for the recommendation")
    predicted_rating: float = Field(..., description="Predicted rating score")
    rank: int = Field(..., description="Rank in top-k results")


class RecommendationResponse(BaseModel):
    """Response containing recommendations for a user."""
    user_id: int
    model: str = Field(..., description="Model used (pmf, autoencoder)")
    top_k: int
    recommendations: list[RecommendationItem]
    generated_at: datetime


# Model Info Schemas
class JokeItem(BaseModel):
    """Joke item containing text metadata."""
    joke_id: int
    joke_text: str


class JokeListResponse(BaseModel):
    """Response containing a list of jokes."""
    jokes: list[JokeItem]


class ModelInfo(BaseModel):
    """Information about a trained model."""
    model_type: str  # 'pmf' or 'autoencoder'
    model_name: str  # e.g., 'pmf_k10_sigmaU0.1_sigmaV0.1_bs1000'
    model_path: str
    created_at: datetime | None = None
    metrics: dict | None = None  # e.g., test_rmse, test_ndcg_10


class ModelsListResponse(BaseModel):
    """Response listing all available models."""
    models: list[ModelInfo]
    default_model: str


# Feedback Schemas
class FeedbackCreateRequest(BaseModel):
    """Request to submit implicit feedback."""
    session_id: str
    user_id: int
    joke_id: int
    feedback_type: str = Field(..., description="Type of feedback: 'like', 'dislike', 'view'")


# Error Schemas
class ErrorResponse(BaseModel):
    """Standardized error response."""
    error_code: str
    message: str
    details: dict | None = None
