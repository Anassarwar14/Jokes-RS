"""Model information and listing endpoints."""
from fastapi import APIRouter, HTTPException, status
from api.config import settings
from api.schemas import ModelInfo, ModelsListResponse
from api.services.model_loader import ModelLoader
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/models", tags=["Models"])


@router.get("", response_model=ModelsListResponse)
async def list_models():
    """List all available trained models."""
    try:
        available = ModelLoader.list_available_models()
        
        # Convert to ModelInfo objects
        models_list = []
        
        for pmf_model in available["pmf"]:
            models_list.append(ModelInfo(
                model_type="pmf",
                model_name=pmf_model["model_name"],
                model_path=pmf_model["model_path"],
                metrics=pmf_model.get("metrics"),
            ))
        
        for ae_model in available["autoencoder"]:
            models_list.append(ModelInfo(
                model_type="autoencoder",
                model_name=ae_model["model_name"],
                model_path=ae_model["model_path"],
                metrics=ae_model.get("metrics"),
            ))
        
        return ModelsListResponse(
            models=models_list,
            default_model=settings.default_model,
        )
    
    except Exception as e:
        logger.error(f"Error listing models: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error listing models: {str(e)}",
        )


@router.get("/{model_type}", response_model=list)
async def list_models_by_type(model_type: str):
    """List all models of a specific type.
    
    Args:
        model_type: 'pmf' or 'autoencoder'
        
    Returns:
        List of model information
    """
    if model_type not in ["pmf", "autoencoder"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unknown model type: {model_type}. Use 'pmf' or 'autoencoder'.",
        )
    
    try:
        available = ModelLoader.list_available_models()
        
        models = available.get(model_type, [])
        
        return [
            ModelInfo(
                model_type=model_type,
                model_name=m["model_name"],
                model_path=m["model_path"],
                metrics=m.get("metrics"),
            )
            for m in models
        ]
    
    except Exception as e:
        logger.error(f"Error listing {model_type} models: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error listing models: {str(e)}",
        )


@router.get("/{model_type}/{model_name}", response_model=ModelInfo)
async def get_model_info(model_type: str, model_name: str):
    """Get information about a specific model.
    
    Args:
        model_type: 'pmf' or 'autoencoder'
        model_name: Name of the model
        
    Returns:
        Model information including metrics
    """
    if model_type not in ["pmf", "autoencoder"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unknown model type: {model_type}. Use 'pmf' or 'autoencoder'.",
        )
    
    try:
        available = ModelLoader.list_available_models()
        
        models = available.get(model_type, [])
        
        for model in models:
            if model["model_name"] == model_name or model_name in model["model_name"]:
                return ModelInfo(
                    model_type=model_type,
                    model_name=model["model_name"],
                    model_path=model["model_path"],
                    metrics=model.get("metrics"),
                )
        
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Model '{model_name}' of type '{model_type}' not found",
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving model info: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving model info: {str(e)}",
        )
