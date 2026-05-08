"""Model loading and inference service."""
import numpy as np
import json
import pickle
from pathlib import Path
from typing import Optional, Tuple
import logging
from config import settings

logger = logging.getLogger(__name__)

# In-process model cache
_model_cache = {}


class ModelLoader:
    """Load and cache trained recommendation models."""
    
    @staticmethod
    def load_pmf_model(model_path: str) -> dict:
        """Load a PMF model from .npz or .pkl file.
        
        Args:
            model_path: Path to the .npz or .pkl model file
            
        Returns:
            Dictionary with model parameters: U, V, global_bias, user_bias, item_bias, hyperparameters
        """
        model_path = Path(model_path)
        
        if not model_path.exists():
            raise FileNotFoundError(f"Model file not found: {model_path}")
        
        logger.info(f"Loading PMF model from {model_path}...")
        
        if model_path.suffix == '.pkl':
            # Load from pickle
            with open(model_path, 'rb') as f:
                model_data = pickle.load(f)
        else:
            # Load from npz
            data = np.load(model_path, allow_pickle=False)
            
            # Convert npz to dictionary and convert scalar arrays back to scalars
            model_data = {}
            for key in data.files:
                value = data[key]
                # Convert scalar arrays to scalars
                model_data[key] = value.item() if value.size == 1 else value
        
        logger.info(f"✓ Loaded PMF model: k={model_data.get('k')}")
        return model_data
    
    @staticmethod
    def load_autoencoder_model(model_path: str) -> dict:
        """Load an autoencoder model from .pt or .pkl file.
        
        Args:
            model_path: Path to the .pt or .pkl model file
            
        Returns:
            Dictionary with state_dict and metadata
        """
        model_path = Path(model_path)
        
        if not model_path.exists():
            raise FileNotFoundError(f"Model file not found: {model_path}")
        
        logger.info(f"Loading autoencoder model from {model_path}...")
        
        if model_path.suffix == '.pkl':
            # Load from pickle
            with open(model_path, 'rb') as f:
                model_data = pickle.load(f)
        else:
            # Load from pytorch
            import torch
            model_data = torch.load(model_path, map_location='cpu')
        
        logger.info(f"✓ Loaded autoencoder model")
        return model_data
    
    @staticmethod
    def list_available_models(models_dir: Optional[Path] = None) -> dict:
        """List all available trained models.
        
        Args:
            models_dir: Directory to scan for models (defaults to config setting)
            
        Returns:
            Dictionary with PMF and autoencoder models
        """
        if models_dir is None:
            models_dir = settings.models_dir
        
        models_dir = Path(models_dir)
        available_models = {
            "pmf": [],
            "autoencoder": [],
        }
        
        if not models_dir.exists():
            logger.warning(f"Models directory not found: {models_dir}")
            return available_models
        
        # Scan for PMF models
        pmf_dir = models_dir / "pmf"
        if pmf_dir.exists():
            for model_file in list(pmf_dir.glob("*.npz")) + list(pmf_dir.glob("*.pkl")):
                metrics_file = pmf_dir / (model_file.stem + "_metrics.json")
                metrics = {}
                if metrics_file.exists():
                    with open(metrics_file) as f:
                        metrics = json.load(f)
                
                available_models["pmf"].append({
                    "model_name": model_file.stem,
                    "model_path": str(model_file),
                    "metrics": metrics,
                })
        
        # Scan for autoencoder models
        ae_dir = models_dir / "autoencoder"
        if ae_dir.exists():
            for model_file in list(ae_dir.glob("*.pt")) + list(ae_dir.glob("*.pkl")):
                metrics_file = ae_dir / (model_file.stem + "_metrics.json")
                metrics = {}
                if metrics_file.exists():
                    with open(metrics_file) as f:
                        metrics = json.load(f)
                
                available_models["autoencoder"].append({
                    "model_name": model_file.stem,
                    "model_path": str(model_file),
                    "metrics": metrics,
                })
        
        logger.info(f"Found {len(available_models['pmf'])} PMF models and {len(available_models['autoencoder'])} autoencoder models")
        return available_models
    
    @staticmethod
    def get_model(model_type: str, model_name: Optional[str] = None) -> dict:
        """Get a model from cache or load it.
        
        Args:
            model_type: 'pmf' or 'autoencoder'
            model_name: Specific model name (if None, auto-discovers first available model)
            
        Returns:
            Model data dictionary
        """
        if model_type not in ["pmf", "autoencoder"]:
            raise ValueError(f"Unknown model type: {model_type}")
        
        models_dir = settings.models_dir / model_type
        
        # If no model name specified, find the first available model of this type
        if model_name is None:
            # Look for any .pkl or .npz/.pt file
            available_files = list(models_dir.glob("*.pkl")) + list(models_dir.glob("*.npz" if model_type == "pmf" else "*.pt"))
            if available_files:
                model_name = available_files[0].stem
                logger.info(f"Using default {model_type} model: {model_name}")
            else:
                raise FileNotFoundError(f"No {model_type} models found in {models_dir}")
        
        # Check cache
        cache_key = f"{model_type}:{model_name}"
        if cache_key in _model_cache:
            logger.debug(f"Using cached model: {cache_key}")
            return _model_cache[cache_key]
        
        # Find model file
        model_path = None
        
        if model_type == "pmf":
            # Look for .npz or .pkl files
            for file in list(models_dir.glob("*.npz")) + list(models_dir.glob("*.pkl")):
                if file.stem == model_name or model_name in file.stem:
                    model_path = file
                    break
            if model_path is None:
                raise FileNotFoundError(f"PMF model '{model_name}' not found in {models_dir}")
            model_data = ModelLoader.load_pmf_model(str(model_path))
        
        elif model_type == "autoencoder":
            # Look for .pt or .pkl files
            for file in list(models_dir.glob("*.pt")) + list(models_dir.glob("*.pkl")):
                if file.stem == model_name or model_name in file.stem:
                    model_path = file
                    break
            if model_path is None:
                raise FileNotFoundError(f"Autoencoder model '{model_name}' not found in {models_dir}")
            model_data = ModelLoader.load_autoencoder_model(str(model_path))
        
        # Cache the model
        _model_cache[cache_key] = model_data
        logger.info(f"Cached model: {cache_key}")
        
        return model_data


class InferenceService:
    """Generate recommendations using loaded models."""
    
    @staticmethod
    def get_pmf_recommendations(
        model_data: dict,
        user_id: int,
        user_ratings: dict,
        n_items: int,
        top_k: int = 10,
    ) -> list:
        """Generate PMF recommendations for a user.
        
        Args:
            model_data: PMF model parameters (U, V, biases)
            user_id: User ID
            user_ratings: Dictionary of {joke_id: rating} for user
            n_items: Total number of items
            top_k: Number of recommendations
            
        Returns:
            List of (joke_id, predicted_rating) tuples, sorted by rating descending
        """
        U = model_data['U']
        V = model_data['V']
        global_bias = model_data['global_bias']
        user_bias = model_data['user_bias']
        item_bias = model_data['item_bias']
        user_means = model_data.get('user_means', np.zeros(len(user_bias)))
        
        # Generate centered predictions
        user_factors = U[user_id]
        item_factors = V
        
        # Compute dot product for all items
        pred_centered = global_bias + user_bias[user_id] + item_bias + (item_factors @ user_factors)
        
        # Add back user mean
        user_mean = user_means[user_id] if user_id < len(user_means) else 0
        predictions = pred_centered + user_mean
        
        # Rank items (excluding already-rated items)
        rated_jokes = set(user_ratings.keys()) if user_ratings else set()
        scores = []
        
        for joke_id in range(n_items):
            if joke_id not in rated_jokes:
                scores.append((joke_id, predictions[joke_id]))
        
        # Sort by predicted rating descending
        scores.sort(key=lambda x: x[1], reverse=True)
        
        return scores[:top_k]
    
    @staticmethod
    def get_autoencoder_recommendations(
        model_data: dict,
        user_id: int,
        user_ratings: dict,
        train_filled: np.ndarray,
        top_k: int = 10,
    ) -> list:
        """Generate autoencoder recommendations for a user.
        
        Args:
            model_data: Autoencoder model (state_dict)
            user_id: User ID
            user_ratings: Dictionary of {joke_id: rating} for user
            train_filled: Centered training matrix (n_users, n_items)
            top_k: Number of recommendations
            
        Returns:
            List of (joke_id, predicted_rating) tuples
        """
        import torch
        from src.autoencoder import Autoencoder
        
        n_items = train_filled.shape[1]
        latent_dim = model_data.get('latent_dim', 32)
        
        # Reconstruct model
        model = Autoencoder(n_items, latent_dim=latent_dim)
        model.load_state_dict(model_data['state_dict'])
        model.eval()
        
        # Generate predictions for all users
        train_tensor = torch.from_numpy(train_filled.astype(np.float32)).float()
        with torch.no_grad():
            pred_centered = model(train_tensor).cpu().numpy()
        
        # Add back user means
        user_means = model_data.get('user_means', np.zeros(train_filled.shape[0]))
        predictions = pred_centered[user_id] + user_means[user_id]
        
        # Rank items (excluding already-rated items)
        rated_jokes = set(user_ratings.keys()) if user_ratings else set()
        scores = []
        
        for joke_id in range(n_items):
            if joke_id not in rated_jokes:
                scores.append((joke_id, predictions[joke_id]))
        
        # Sort by predicted rating descending
        scores.sort(key=lambda x: x[1], reverse=True)
        
        return scores[:top_k]
