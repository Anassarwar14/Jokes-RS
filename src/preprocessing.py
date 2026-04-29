"""Load and preprocess Jester dataset."""
from pathlib import Path
import numpy as np
import pandas as pd

# Paths
PROJECT_ROOT = Path(__file__).parent.parent
EDA_DATA_DIR = PROJECT_ROOT / "EDA" / "data"
DATA_PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"
DATA_PROCESSED_DIR.mkdir(parents=True, exist_ok=True)


def preprocess(seed=42):
    """Load ratings and create train/val/test splits."""
    print(f"Loading ratings from {EDA_DATA_DIR}...")
    ratings_df = pd.read_parquet(EDA_DATA_DIR / "ratings_clean.parquet")
    print(f"Loaded: {ratings_df.shape} (users × jokes)")
    
    np.random.seed(seed)
    rating_matrix = ratings_df.values.astype(np.float32)
    n_users, n_jokes = rating_matrix.shape
    
    # Get observed entries
    mask = ~np.isnan(rating_matrix)
    observed_users, observed_jokes = np.where(mask)
    observed_ratings = rating_matrix[mask]
    
    # Shuffle and split (80/10/10)
    perm = np.random.permutation(len(observed_users))
    observed_users = observed_users[perm]
    observed_jokes = observed_jokes[perm]
    observed_ratings = observed_ratings[perm]
    
    n_obs = len(observed_users)
    train_end = int(n_obs * 0.8)
    val_end = train_end + int(n_obs * 0.1)
    
    train_user = observed_users[:train_end]
    train_joke = observed_jokes[:train_end]
    train_rating = observed_ratings[:train_end]
    
    # Compute user means from train set
    user_means = np.zeros(n_users, dtype=np.float32)
    for u in range(n_users):
        user_train_ratings = train_rating[train_user == u]
        if len(user_train_ratings) > 0:
            user_means[u] = user_train_ratings.mean()
    
    # Create centered training matrix
    train_filled = np.zeros((n_users, n_jokes), dtype=np.float32)
    train_filled[train_user, train_joke] = train_rating - user_means[train_user]
    
    train_mask = np.zeros((n_users, n_jokes), dtype=bool)
    train_mask[train_user, train_joke] = True
    
    # Val and test
    val_user = observed_users[train_end:val_end]
    val_item = observed_jokes[train_end:val_end]
    val_rating = observed_ratings[train_end:val_end]
    
    test_user = observed_users[val_end:]
    test_item = observed_jokes[val_end:]
    test_rating = observed_ratings[val_end:]
    
    # Save
    output_dir = DATA_PROCESSED_DIR / f"seed_{seed}"
    output_dir.mkdir(parents=True, exist_ok=True)
    
    splits = {
        'train_filled': train_filled,
        'train_mask': train_mask,
        'val_user': val_user,
        'val_item': val_item,
        'val_rating': val_rating,
        'test_user': test_user,
        'test_item': test_item,
        'test_rating': test_rating,
        'user_means': user_means
    }
    
    np.savez_compressed(output_dir / "splits.npz", **splits)
    print(f"Splits saved to {output_dir / 'splits.npz'}")
    print(f"  Train: {train_filled.shape[0]} samples | Val: {len(val_user)} | Test: {len(test_user)}")
    
    return output_dir / "splits.npz"
