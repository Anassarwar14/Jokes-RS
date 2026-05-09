"""PyTorch autoencoder for recommendation."""
from pathlib import Path
import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
import json
import sys
from pathlib import Path

# Add project root to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.metrics import rmse, mae, ndcg_at_k, recall_at_k


class Autoencoder(nn.Module):
    def __init__(self, n_items, latent_dim=32, hidden_dim=128, dropout=0.3):
        super().__init__()
        self.encoder = nn.Sequential(
            nn.Linear(n_items, hidden_dim),
            nn.ReLU(),
            nn.Dropout(dropout),
            nn.Linear(hidden_dim, latent_dim),
        )
        self.decoder = nn.Sequential(
            nn.Linear(latent_dim, hidden_dim),
            nn.ReLU(),
            nn.Dropout(dropout),
            nn.Linear(hidden_dim, n_items),
        )
    
    def forward(self, x):
        return self.decoder(self.encoder(x))


def train_autoencoder(splits_file, latent_dim=32, epochs=20, patience=5, device='cpu'):
    """Train autoencoder model."""
    print(f"Loading splits from {splits_file}...")
    data = np.load(splits_file, allow_pickle=True)
    
    train_filled = data['train_filled'].astype(np.float32)
    train_mask = data['train_mask'].astype(bool)
    user_means = data['user_means'].astype(np.float32)
    val_user = data['val_user'].astype(int)
    val_item = data['val_item'].astype(int)
    val_rating = data['val_rating'].astype(np.float32)
    test_user = data['test_user'].astype(int)
    test_item = data['test_item'].astype(int)
    test_rating = data['test_rating'].astype(np.float32)
    
    n_users, n_items = train_filled.shape
    device_obj = torch.device(device)
    
    print(f"Training Autoencoder (latent_dim={latent_dim}, epochs={epochs})...")
    model = Autoencoder(n_items, latent_dim=latent_dim).to(device_obj)
    optimizer = optim.Adam(model.parameters(), lr=1e-4)
    
    train_tensor = torch.from_numpy(train_filled).float().to(device_obj)
    train_mask_tensor = torch.from_numpy(train_mask).float().to(device_obj)
    
    best_val_rmse = float('inf')
    patience_cnt = 0
    
    for epoch in range(epochs):
        model.train()
        for i in range(0, n_users, 32):
            batch_end = min(i + 32, n_users)
            batch_data = train_tensor[i:batch_end]
            batch_mask = train_mask_tensor[i:batch_end]
            
            recon = model(batch_data)
            loss = (((recon - batch_data) ** 2) * batch_mask).sum() / batch_mask.sum()
            
            optimizer.zero_grad()
            loss.backward()
            optimizer.step()
        
        # Validate
        model.eval()
        with torch.no_grad():
            pred_centered = model(train_tensor).cpu().numpy()
        
        predictions = pred_centered + user_means[:, np.newaxis]
        val_rmse = rmse(predictions, val_user, val_item, val_rating)
        
        if epoch % 2 == 0:
            print(f"  Epoch {epoch + 1}/{epochs} - Val RMSE: {val_rmse:.4f}")
        
        if val_rmse < best_val_rmse:
            best_val_rmse = val_rmse
            patience_cnt = 0
            best_state = model.state_dict().copy()
        else:
            patience_cnt += 1
            if patience_cnt >= patience:
                print(f"  Early stopping at epoch {epoch + 1}")
                model.load_state_dict(best_state)
                break
    
    # Final evaluation
    with torch.no_grad():
        pred_centered = model(train_tensor).cpu().numpy()
    predictions = pred_centered + user_means[:, np.newaxis]
    
    val_rmse = rmse(predictions, val_user, val_item, val_rating)
    val_mae = mae(predictions, val_user, val_item, val_rating)
    val_ndcg = ndcg_at_k(predictions, val_user, val_item, val_rating, k=10)
    val_recall = recall_at_k(predictions, val_user, val_item, val_rating, k=10, threshold=0.0)

    test_rmse = rmse(predictions, test_user, test_item, test_rating)
    test_mae = mae(predictions, test_user, test_item, test_rating)
    test_ndcg = ndcg_at_k(predictions, test_user, test_item, test_rating, k=10)
    test_recall = recall_at_k(predictions, test_user, test_item, test_rating, k=10, threshold=0.0)
    
    print(f"Autoencoder training complete!")
    print(f"  Validation RMSE: {val_rmse:.4f}")
    print(f"  Validation MAE : {val_mae:.4f}")
    print(f"  Validation NDCG@10 : {val_ndcg:.4f}")
    print(f"  Validation Recall@10: {val_recall:.4f}")
    print(f"  Test RMSE      : {test_rmse:.4f}")
    print(f"  Test MAE       : {test_mae:.4f}")
    print(f"  Test NDCG@10   : {test_ndcg:.4f}")
    print(f"  Test Recall@10 : {test_recall:.4f}")
    
    # Save
    models_dir = Path(__file__).parent.parent / "models/autoencoder"
    models_dir.mkdir(parents=True, exist_ok=True)
    
    model_data = {
        'state_dict': {k: v.cpu() for k, v in model.state_dict().items()},
        'latent_dim': latent_dim,
        'n_items': n_items
    }
    model_path = models_dir / f"autoencoder_latent{latent_dim}.pt"
    torch.save(model_data, model_path)
    
    metrics_path = models_dir / f"autoencoder_latent{latent_dim}_metrics.json"
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
