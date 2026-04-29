"""SVD baseline recommendation model."""
from pathlib import Path
import numpy as np
import pickle
import json
from sklearn.decomposition import TruncatedSVD
from metrics import rmse, mae, ndcg_at_k, recall_at_k


def train_svd(splits_file, k=10, seed=42):
    """Train SVD model."""
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
    
    print(f"Training SVD with k={k}...")
    svd = TruncatedSVD(n_components=k, random_state=seed)
    U = svd.fit_transform(train_filled)
    Vt = svd.components_
    
    # Predict
    pred_centered = U @ Vt
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
    
    print(f"✓ SVD training complete!")
    print(f"  Validation RMSE: {val_rmse:.4f}")
    print(f"  Validation MAE : {val_mae:.4f}")
    print(f"  Validation NDCG@10 : {val_ndcg:.4f}")
    print(f"  Validation Recall@10: {val_recall:.4f}")
    print(f"  Test RMSE      : {test_rmse:.4f}")
    print(f"  Test MAE       : {test_mae:.4f}")
    print(f"  Test NDCG@10   : {test_ndcg:.4f}")
    print(f"  Test Recall@10 : {test_recall:.4f}")
    
    # Save
    models_dir = Path(__file__).parent.parent / "models/svd"
    models_dir.mkdir(exist_ok=True)
    
    model_data = {'U': U, 'Vt': Vt, 'user_means': user_means, 'k': k}
    model_path = models_dir / f"svd_k{k}.pkl"
    with open(model_path, 'wb') as f:
        pickle.dump(model_data, f)
    
    metrics_path = models_dir / f"svd_k{k}_metrics.json"
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
