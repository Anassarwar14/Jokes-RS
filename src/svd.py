"""Probabilistic Matrix Factorization for recommendation."""
from pathlib import Path
import numpy as np
import pickle
import json
from metrics import rmse, mae, ndcg_at_k, recall_at_k


def pmf_factorization(train_matrix, k=10, sigma_u=0.1, sigma_v=0.1, sigma_r=1.0, 
                     learning_rate=0.01, n_epochs=50, batch_size=1000, seed=42):
    """Probabilistic Matrix Factorization with mini-batch gradient descent."""
    np.random.seed(seed)
    n_users, n_items = train_matrix.shape
    
    # Initialize user and item factors
    U = np.random.normal(0, sigma_u, (n_users, k))
    V = np.random.normal(0, sigma_v, (n_items, k))
    
    # Initialize bias terms
    global_bias = np.mean(train_matrix[train_matrix != 0])
    user_bias = np.zeros(n_users)
    item_bias = np.zeros(n_items)
    
    # Pre-compute observed entries
    observed_mask = (train_matrix != 0)
    observed_users, observed_items = np.where(observed_mask)
    observed_ratings = train_matrix[observed_users, observed_items]
    
    n_observed = len(observed_ratings)
    
    # Precision parameters (inverse variances)
    lambda_u = 1.0 / (sigma_u ** 2)
    lambda_v = 1.0 / (sigma_v ** 2)
    lambda_r = 1.0 / (sigma_r ** 2)
    
    print(f"Training PMF with {n_observed} observed ratings (batch_size={batch_size})...")
    
    for epoch in range(n_epochs):
        # Shuffle observed entries for mini-batch gradient descent
        perm = np.random.permutation(n_observed)
        observed_users_shuf = observed_users[perm]
        observed_items_shuf = observed_items[perm]
        observed_ratings_shuf = observed_ratings[perm]
        
        # Mini-batch updates
        for start_idx in range(0, n_observed, batch_size):
            end_idx = min(start_idx + batch_size, n_observed)
            batch_users = observed_users_shuf[start_idx:end_idx]
            batch_items = observed_items_shuf[start_idx:end_idx]
            batch_ratings = observed_ratings_shuf[start_idx:end_idx]
            
            # Compute predictions for batch
            batch_pred = (global_bias + 
                         user_bias[batch_users] + 
                         item_bias[batch_items] + 
                         np.sum(U[batch_users] * V[batch_items], axis=1))
            
            # Compute errors
            errors = batch_ratings - batch_pred
            
            # Update user factors
            U[batch_users] += learning_rate * (errors[:, np.newaxis] * V[batch_items] - lambda_u * U[batch_users])
            
            # Update item factors
            V[batch_items] += learning_rate * (errors[:, np.newaxis] * U[batch_users] - lambda_v * V[batch_items])
            
            # Update biases
            user_bias[batch_users] += learning_rate * (errors - lambda_r * user_bias[batch_users])
            item_bias[batch_items] += learning_rate * (errors - lambda_r * item_bias[batch_items])
        # Optional: Print progress every 10 epochs
        if (epoch + 1) % 10 == 0:
            # Compute training RMSE
            train_pred = global_bias + user_bias[:, np.newaxis] + item_bias[np.newaxis, :] + U @ V.T
            train_rmse = np.sqrt(np.mean((train_pred[observed_mask] - observed_ratings) ** 2))
            print(f"  Epoch {epoch + 1}/{n_epochs} - Train RMSE: {train_rmse:.4f}")
    
    return U, V, global_bias, user_bias, item_bias


def train_svd(splits_file, k=10, sigma_u=0.1, sigma_v=0.1, sigma_r=1.0, 
             learning_rate=0.01, n_epochs=50, batch_size=1000, seed=42):
    """Train PMF model."""
    print(f"Loading splits from {splits_file}...")
    data = np.load(splits_file, allow_pickle=True)
    
    train_filled = data['train_filled'].astype(np.float32)
    user_means = data['user_means'].astype(np.float32)
    val_user = data['val_user'].astype(int)
    val_item = data['val_item'].astype(int)
    val_rating = data['val_rating'].astype(np.float32)
    test_user = data['test_user'].astype(int)
    test_item = data['test_item'].astype(int)
    test_rating = data['test_rating'].astype(np.float32)
    
    print(f"Training PMF with k={k}, sigma_u={sigma_u}, sigma_v={sigma_v}, lr={learning_rate}, epochs={n_epochs}...")
    U, V, global_bias, user_bias, item_bias = pmf_factorization(
        train_filled, k=k, sigma_u=sigma_u, sigma_v=sigma_v, sigma_r=sigma_r,
        learning_rate=learning_rate, n_epochs=n_epochs, batch_size=batch_size, seed=seed
    )
    
    # Predict centered ratings
    pred_centered = global_bias + user_bias[:, np.newaxis] + item_bias[np.newaxis, :] + U @ V.T
    
    # Add back user means for final predictions
    predictions = pred_centered + user_means[:, np.newaxis]
    
    # Evaluate
    val_rmse = rmse(predictions, val_user, val_item, val_rating)
    val_mae = mae(predictions, val_user, val_item, val_rating)
    val_ndcg = ndcg_at_k(predictions, val_user, val_item, val_rating, k=10)
    val_recall = recall_at_k(predictions, val_user, val_item, val_rating, k=10, threshold=0.0)

    test_rmse = rmse(predictions, test_user, test_item, test_rating)
    test_mae = mae(predictions, test_user, test_item, test_rating)
    test_ndcg = ndcg_at_k(predictions, test_user, test_item, test_rating, k=10)
    test_recall = recall_at_k(predictions, test_user, test_item, test_rating, k=10, threshold=0.0)
    
    print(f"✓ PMF training complete!")
    print(f"  Validation RMSE: {val_rmse:.4f}")
    print(f"  Validation MAE : {val_mae:.4f}")
    print(f"  Validation NDCG@10 : {val_ndcg:.4f}")
    print(f"  Validation Recall@10: {val_recall:.4f}")
    print(f"  Test RMSE      : {test_rmse:.4f}")
    print(f"  Test MAE       : {test_mae:.4f}")
    print(f"  Test NDCG@10   : {test_ndcg:.4f}")
    print(f"  Test Recall@10 : {test_recall:.4f}")
    
    # Save
    models_dir = Path(__file__).parent.parent / "models/pmf"
    models_dir.mkdir(parents=True, exist_ok=True)
    
    model_data = {
        'U': U, 'V': V, 
        'global_bias': global_bias, 
        'user_bias': user_bias, 
        'item_bias': item_bias,
        'user_means': user_means, 
        'k': k, 
        'sigma_u': sigma_u,
        'sigma_v': sigma_v,
        'sigma_r': sigma_r,
        'learning_rate': learning_rate,
        'n_epochs': n_epochs,
        'batch_size': batch_size
    }
    model_path = models_dir / f"pmf_k{k}_sigmaU{sigma_u}_sigmaV{sigma_v}_bs{batch_size}.pkl"
    with open(model_path, 'wb') as f:
        pickle.dump(model_data, f)
    
    metrics_path = models_dir / f"pmf_k{k}_sigmaU{sigma_u}_sigmaV{sigma_v}_bs{batch_size}_metrics.json"
    with open(metrics_path, 'w') as f:
        json.dump(
            {
                'val_rmse': float(val_rmse),
                'val_mae': float(val_mae),
                'val_ndcg_10': float(val_ndcg),
                'val_recall_10': float(val_recall),
                'test_rmse': float(test_rmse),
                'test_mae': float(test_mae),
                'test_ndcg_10': float(test_ndcg),
                'test_recall_10': float(test_recall),
            },
            f,
        )
    
    print(f"  Model: {model_path}")