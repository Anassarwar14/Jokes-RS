"""Session management routes."""
import uuid
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from api.database import get_db
from api.models import SessionModel
from api.schemas import SessionCreateRequest, SessionResponse

router = APIRouter(prefix="/api/sessions", tags=["Sessions"])


@router.post("", response_model=SessionResponse, status_code=status.HTTP_201_CREATED)
async def create_session(
    request: SessionCreateRequest,
    db: Session = Depends(get_db),
):
    """Create a new ephemeral session for a user."""
    # Generate unique session ID
    session_id = str(uuid.uuid4())
    
    # Assign a user ID within the trained model range (0-24982 for PMF/AE models)
    # This ensures compatibility with pre-trained models
    # In production, map real user IDs to this range or implement cold-start strategies
    MAX_TRAINED_USERS = 24983  # PMF model has 24983 users
    user_id = abs(hash(session_id)) % MAX_TRAINED_USERS  # Map to valid user index
    
    # Create session record
    new_session = SessionModel(
        session_id=session_id,
        user_id=user_id,
        created_at=datetime.utcnow(),
        last_active_at=datetime.utcnow(),
        is_active=True,
    )
    
    db.add(new_session)
    db.commit()
    db.refresh(new_session)
    
    return SessionResponse(
        session_id=new_session.session_id,
        user_id=new_session.user_id,
        created_at=new_session.created_at,
        last_active_at=new_session.last_active_at,
        is_active=new_session.is_active,
    )


@router.options("", status_code=200)
async def options_sessions():
    """Handle OPTIONS requests for CORS or method discovery."""
    return


@router.get("/{session_id}", response_model=SessionResponse)
async def get_session(
    session_id: str,
    db: Session = Depends(get_db),
):
    """Retrieve session information."""
    session = db.query(SessionModel).filter(SessionModel.session_id == session_id).first()
    
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Session {session_id} not found",
        )
    
    if not session.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Session is no longer active",
        )
    
    return SessionResponse(
        session_id=session.session_id,
        user_id=session.user_id,
        created_at=session.created_at,
        last_active_at=session.last_active_at,
        is_active=session.is_active,
    )


@router.post("/{session_id}/validate", response_model=dict)
async def validate_session(
    session_id: str,
    db: Session = Depends(get_db),
):
    """Validate and check if a session is still active."""
    session = db.query(SessionModel).filter(SessionModel.session_id == session_id).first()
    
    if not session or not session.is_active:
        return {"valid": False, "message": "Session not found or inactive"}
    
    # Update last_active_at
    session.last_active_at = datetime.utcnow()
    db.commit()
    
    return {"valid": True, "user_id": session.user_id, "message": "Session is active"}
