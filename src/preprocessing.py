"""Load and preprocess Jester dataset."""
from pathlib import Path
import numpy as np
import pandas as pd
from scipy import sparse

# Paths
PROJECT_ROOT = Path(__file__).parent.parent
EDA_DATA_DIR = PROJECT_ROOT / "EDA" / "data"
DATA_PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"
DATA_PROCESSED_DIR.mkdir(parents=True, exist_ok=True)


def preprocess(seed=42, val_ratio=0.1, test_ratio=0.1):
    """Load ratings and create user-centric train/val/test splits."""
    print(f"Loading ratings from {EDA_DATA_DIR}...")
    ratings_df = pd.read_parquet(EDA_DATA_DIR / "ratings_clean.parquet")
    print(f"Loaded: {ratings_df.shape} (users × jokes)")
    
    np.random.seed(seed)
    n_users, n_jokes = ratings_df.shape
    
    # Get all observed ratings as (user, item, rating) tuples
    observed_ratings = []
    for user_idx in range(n_users):
        user_ratings = ratings_df.iloc[user_idx]
        for item_idx in range(n_jokes):
            rating = user_ratings.iloc[item_idx]
            if not np.isnan(rating):
                observed_ratings.append((user_idx, item_idx, rating))
    
    observed_ratings = np.array(observed_ratings)
    print(f"Total observed ratings: {len(observed_ratings)}")
    
    # Group by user for user-centric splitting
    user_groups = {}
    for user_idx, item_idx, rating in observed_ratings:
        if user_idx not in user_groups:
            user_groups[user_idx] = []
        user_groups[user_idx].append((item_idx, rating))
    
    # Split users into train/val/test (ensuring each user has ratings in each set)
    users = list(user_groups.keys())
    np.random.shuffle(users)
    
    n_val = int(len(users) * val_ratio)
    n_test = int(len(users) * test_ratio)
    n_train = len(users) - n_val - n_test
    
    train_users = users[:n_train]
    val_users = users[n_train:n_train + n_val]
    test_users = users[n_train + n_val:]
    
    print(f"User split: Train {len(train_users)}, Val {len(val_users)}, Test {len(test_users)}")
    
    # For each user, split their ratings
    train_data = []
    val_data = []
    test_data = []
    
    for user_idx in train_users:
        user_ratings = user_groups[user_idx]
        np.random.shuffle(user_ratings)
        # All ratings from train users go to train
        for item_idx, rating in user_ratings:
            train_data.append((user_idx, item_idx, rating))
    
    for user_idx in val_users:
        user_ratings = user_groups[user_idx]
        np.random.shuffle(user_ratings)
        n_val_ratings = max(1, int(len(user_ratings) * 0.5))  # At least 1 rating for val
        val_data.extend([(user_idx, item_idx, rating) for item_idx, rating in user_ratings[:n_val_ratings]])
        train_data.extend([(user_idx, item_idx, rating) for item_idx, rating in user_ratings[n_val_ratings:]])
    
    for user_idx in test_users:
        user_ratings = user_groups[user_idx]
        np.random.shuffle(user_ratings)
        n_test_ratings = max(1, int(len(user_ratings) * 0.5))  # At least 1 rating for test
        test_data.extend([(user_idx, item_idx, rating) for item_idx, rating in user_ratings[:n_test_ratings]])
        train_data.extend([(user_idx, item_idx, rating) for item_idx, rating in user_ratings[n_test_ratings:]])
    
    # Convert to arrays
    train_data = np.array(train_data)
    val_data = np.array(val_data)
    test_data = np.array(test_data)
    
    # Create sparse matrices
    train_matrix = sparse.csr_matrix(
        (train_data[:, 2], (train_data[:, 0].astype(int), train_data[:, 1].astype(int))),
        shape=(n_users, n_jokes)
    )
    
    # Compute user means from train data
    user_means = np.zeros(n_users)
    for u in range(n_users):
        user_ratings = train_matrix[u].data
        if len(user_ratings) > 0:
            user_means[u] = user_ratings.mean()
    
    # Center the training matrix
    train_centered = train_matrix.copy()
    train_centered.data -= user_means[train_centered.indices]
    
    # Save
    output_dir = DATA_PROCESSED_DIR / f"seed_{seed}"
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Convert sparse matrices to dense for compatibility with existing code
    # TODO: Update downstream code to handle sparse matrices
    train_centered_dense = train_centered.toarray()
    train_mask_dense = (train_matrix > 0).toarray().astype(bool)
    
    splits = {
        'train_filled': train_centered_dense,
        'train_mask': train_mask_dense,
        'val_user': val_data[:, 0].astype(int),
        'val_item': val_data[:, 1].astype(int),
        'val_rating': val_data[:, 2],
        'test_user': test_data[:, 0].astype(int),
        'test_item': test_data[:, 1].astype(int),
        'test_rating': test_data[:, 2],
        'user_means': user_means,
        'n_users': n_users,
        'n_items': n_jokes
    }
    
    np.savez_compressed(output_dir / "splits.npz", **splits)
    print(f"Splits saved to {output_dir / 'splits.npz'}")
    print(f"  Train ratings: {len(train_data)} | Val: {len(val_data)} | Test: {len(test_data)}")
    
    return output_dir / "splits.npz"
