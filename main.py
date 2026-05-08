#!/usr/bin/env python
"""Jokes recommendation system - single entry point."""
import sys
import argparse
from pathlib import Path
import numpy as np

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from preprocessing import preprocess
from svd import train_pmf
from autoencoder import train_autoencoder
from metrics import rmse, mae, ndcg_at_k_full, recall_at_k_full


def evaluate_model(model_path, splits_file):
    """Evaluate a saved model with full ranking metrics.
    
    Warning: Only load model files from trusted sources. While npz and torch formats
    are safer than pickle, always verify model provenance before loading.
    """
    import torch
    
    print(f"Loading model from {model_path}...")
    model_path = Path(model_path)
    
    if model_path.suffix == '.npz':
        # Load NPZ format (PMF)
        model_data = np.load(model_path, allow_pickle=False)
        # Convert scalar arrays back to scalars
        model_data = {k: (v.item() if v.size == 1 else v) for k, v in model_data.items()}
    else:
        # Load torch format (autoencoder) with map_location for portability
        model_data = torch.load(model_path, map_location='cpu')
    
    print(f"Loading splits from {splits_file}...")
    data = np.load(splits_file, allow_pickle=True)
    
    train_mask = data['train_mask'].astype(bool)
    user_means = data['user_means'].astype(np.float32)
    val_user = data['val_user'].astype(int)
    val_item = data['val_item'].astype(int)
    val_rating = data['val_rating'].astype(np.float32)
    test_user = data['test_user'].astype(int)
    test_item = data['test_item'].astype(int)
    test_rating = data['test_rating'].astype(np.float32)
    
    # Reconstruct predictions based on model type
    if 'U' in model_data and 'V' in model_data:  # PMF model
        U = model_data['U']
        V = model_data['V']
        global_bias = model_data['global_bias']
        user_bias = model_data['user_bias']
        item_bias = model_data['item_bias']
        
        pred_centered = U @ V.T + global_bias + user_bias[:, np.newaxis] + item_bias[np.newaxis, :]
        predictions = pred_centered + user_means[:, np.newaxis]
        
    elif 'state_dict' in model_data:  # Autoencoder model
        import torch
        from autoencoder import Autoencoder
        
        n_items = data['n_items']
        latent_dim = model_data.get('latent_dim', 32)
        
        model = Autoencoder(n_items, latent_dim=latent_dim)
        model.load_state_dict(model_data['state_dict'])
        model.eval()
        
        train_filled = data['train_filled'].astype(np.float32)
        train_tensor = torch.from_numpy(train_filled).float()
        
        with torch.no_grad():
            pred_centered = model(train_tensor).cpu().numpy()
        
        predictions = pred_centered + user_means[:, np.newaxis]
    
    else:
        raise ValueError("Unknown model format")
    
    # Evaluate with full ranking metrics
    print("Evaluating with full ranking metrics...")
    
    val_ndcg_full = ndcg_at_k_full(predictions, train_mask, val_user, val_item, val_rating, k=10)
    val_recall_full = recall_at_k_full(predictions, train_mask, val_user, val_item, val_rating, k=10, threshold=0.0)
    
    test_ndcg_full = ndcg_at_k_full(predictions, train_mask, test_user, test_item, test_rating, k=10)
    test_recall_full = recall_at_k_full(predictions, train_mask, test_user, test_item, test_rating, k=10, threshold=0.0)
    
    # Also compute point-wise metrics for comparison
    val_rmse = rmse(predictions, val_user, val_item, val_rating)
    val_mae = mae(predictions, val_user, val_item, val_rating)
    
    test_rmse = rmse(predictions, test_user, test_item, test_rating)
    test_mae = mae(predictions, test_user, test_item, test_rating)
    
    print("✓ Evaluation complete!")
    print("Point-wise metrics:")
    print(f"  Validation RMSE: {val_rmse:.4f}")
    print(f"  Validation MAE : {val_mae:.4f}")
    print(f"  Test RMSE      : {test_rmse:.4f}")
    print(f"  Test MAE       : {test_mae:.4f}")
    print("Ranking metrics (full candidate ranking):")
    print(f"  Validation NDCG@10 : {val_ndcg_full:.4f}")
    print(f"  Validation Recall@10: {val_recall_full:.4f}")
    print(f"  Test NDCG@10   : {test_ndcg_full:.4f}")
    print(f"  Test Recall@10 : {test_recall_full:.4f}")


def main():
    parser = argparse.ArgumentParser(description="Jokes recommendation system")
    subparsers = parser.add_subparsers(dest="command", help="Command to run")
    
    # Preprocess command
    prep_parser = subparsers.add_parser("preprocess", help="Generate train/val/test splits")
    prep_parser.add_argument("--seed", type=int, default=42)
    prep_parser.add_argument("--val-ratio", type=float, default=0.1, help="Validation ratio")
    prep_parser.add_argument("--test-ratio", type=float, default=0.1, help="Test ratio")
    
    # PMF command
    pmf_parser = subparsers.add_parser("pmf", help="Train Probabilistic Matrix Factorization")
    pmf_parser.add_argument("--k", type=int, default=10, help="Number of latent factors")
    pmf_parser.add_argument("--sigma-u", type=float, default=0.1, help="User factor prior std")
    pmf_parser.add_argument("--sigma-v", type=float, default=0.1, help="Item factor prior std")
    pmf_parser.add_argument("--sigma-r", type=float, default=1.0, help="Rating noise std")
    pmf_parser.add_argument("--learning-rate", type=float, default=0.01, help="Learning rate")
    pmf_parser.add_argument("--n-epochs", type=int, default=50, help="Number of training epochs")
    pmf_parser.add_argument("--batch-size", type=int, default=1000, help="Mini-batch size")
    pmf_parser.add_argument("--seed", type=int, default=42)
    
    # Autoencoder command
    ae_parser = subparsers.add_parser("autoencoder", help="Train autoencoder")
    ae_parser.add_argument("--latent-dim", type=int, default=32)
    ae_parser.add_argument("--epochs", type=int, default=20)
    ae_parser.add_argument("--patience", type=int, default=5)
    ae_parser.add_argument("--device", default="cpu", choices=["cpu", "cuda"])
    
    # Evaluate command
    eval_parser = subparsers.add_parser("evaluate", help="Evaluate model with full ranking metrics")
    eval_parser.add_argument("--model-path", required=True, help="Path to saved model")
    eval_parser.add_argument("--splits-file", required=True, help="Path to splits file")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    data_processed = Path(__file__).parent / "data" / "processed" / f"seed_{getattr(args, 'seed', 42)}"
    splits_file = data_processed / "splits.npz"
    
    if args.command == "preprocess":
        preprocess(seed=args.seed, val_ratio=args.val_ratio, test_ratio=args.test_ratio)
    
    elif args.command == "pmf":
        if not splits_file.exists():
            print(f"Error: {splits_file} not found. Run 'preprocess' first.")
            sys.exit(1)
        train_pmf(splits_file, k=args.k, sigma_u=args.sigma_u, sigma_v=args.sigma_v, 
                 sigma_r=args.sigma_r, learning_rate=args.learning_rate, 
                 n_epochs=args.n_epochs, batch_size=args.batch_size, seed=args.seed)
    
    elif args.command == "autoencoder":
        if not splits_file.exists():
            print(f"Error: {splits_file} not found. Run 'preprocess' first.")
            sys.exit(1)
        train_autoencoder(splits_file, latent_dim=args.latent_dim, epochs=args.epochs,
                         patience=args.patience, device=args.device)
    
    elif args.command == "evaluate":
        evaluate_model(args.model_path, args.splits_file)


if __name__ == "__main__":
    main()
