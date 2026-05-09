"""SQLAlchemy ORM models for database tables."""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from api.database import Base


class SessionModel(Base):
    """User session for tracking interactions."""
    __tablename__ = "sessions"
    
    session_id = Column(String(36), primary_key=True, index=True)
    user_id = Column(Integer, nullable=False, index=True)  # Assigned on session creation
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    last_active_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = Column(Boolean, default=True)
    
    # Relationships
    ratings = relationship("UserRating", back_populates="session", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<SessionModel(session_id={self.session_id}, user_id={self.user_id})>"


class UserRating(Base):
    """User rating for a joke item."""
    __tablename__ = "user_ratings"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(String(36), ForeignKey("sessions.session_id"), nullable=False, index=True)
    user_id = Column(Integer, nullable=False, index=True)
    joke_id = Column(Integer, nullable=False, index=True)
    rating = Column(Float, nullable=False)  # -10 to 10 for Jester dataset
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    session = relationship("SessionModel", back_populates="ratings")
    
    def __repr__(self):
        return f"<UserRating(user_id={self.user_id}, joke_id={self.joke_id}, rating={self.rating})>"


class UserFeedback(Base):
    """Optional implicit feedback (likes, dislikes, views)."""
    __tablename__ = "user_feedback"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(String(36), ForeignKey("sessions.session_id"), nullable=False, index=True)
    user_id = Column(Integer, nullable=False, index=True)
    joke_id = Column(Integer, nullable=False, index=True)
    feedback_type = Column(String(50), nullable=False)  # 'like', 'dislike', 'view'
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    def __repr__(self):
        return f"<UserFeedback(user_id={self.user_id}, joke_id={self.joke_id}, type={self.feedback_type})>"
