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
    """Evaluate a saved model and return a metrics dict.

    Returns a dict with point-wise and ranking metrics so callers can
    aggregate and compare multiple models.
    """
    import torch

    model_path = Path(model_path)

    if model_path.suffix == '.npz':
        model_data = np.load(model_path, allow_pickle=False)
        model_data = {k: (v.item() if getattr(v, 'size', 1) == 1 else v) for k, v in model_data.items()}
    else:
        loaded = torch.load(model_path, map_location='cpu')
        # Normalize several common save formats into a dict with 'state_dict' when possible
        if isinstance(loaded, dict):
            # If dict already contains state_dict, use it
            if 'state_dict' in loaded:
                model_data = loaded
            # Some code saves {'model': <Module>} or {'model_state': state_dict}
            elif 'model' in loaded and hasattr(loaded['model'], 'state_dict'):
                model_obj = loaded['model']
                model_data = {'state_dict': model_obj.state_dict()}
                if 'latent_dim' in loaded:
                    model_data['latent_dim'] = loaded['latent_dim']
            elif 'model_state' in loaded:
                model_data = {'state_dict': loaded['model_state']}
                if 'latent_dim' in loaded:
                    model_data['latent_dim'] = loaded['latent_dim']
            else:
                # If dict contains tensors like 'encoder.weight' etc, treat as state_dict
                # Heuristic: keys containing '.' and tensor values
                keys = list(loaded.keys())
                if keys and all(isinstance(k, str) and '.' in k for k in keys):
                    model_data = {'state_dict': loaded}
                else:
                    model_data = loaded
        else:
            # Could be a Module instance
            if hasattr(loaded, 'state_dict'):
                model_data = {'state_dict': loaded.state_dict()}
                # Try to copy any latent_dim attribute if present
                if hasattr(loaded, 'latent_dim'):
                    model_data['latent_dim'] = getattr(loaded, 'latent_dim')
            else:
                model_data = loaded

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
        global_bias = model_data.get('global_bias', 0.0)
        user_bias = model_data.get('user_bias', np.zeros(U.shape[0]))
        item_bias = model_data.get('item_bias', np.zeros(V.shape[0]))

        pred_centered = U @ V.T + global_bias + user_bias[:, np.newaxis] + item_bias[np.newaxis, :]
        predictions = pred_centered + user_means[:, np.newaxis]

    elif 'state_dict' in model_data:  # Autoencoder model
        from autoencoder import Autoencoder

        n_items = int(data['n_items'])
        # Try to infer latent_dim from model metadata or state_dict
        if 'latent_dim' in model_data:
            latent_dim = int(model_data['latent_dim'])
        else:
            # Heuristic: look for encoder weight shapes (latent_dim, hidden_dim)
            state = model_data['state_dict']
            inferred = None
            # More robust inference: pick the encoder weight with the largest index (final layer)
            encoder_weight_keys = [k for k in state.keys() if k.startswith('encoder.') and k.endswith('.weight')]
            inferred = None
            if encoder_weight_keys:
                def key_index(key):
                    parts = key.split('.')
                    try:
                        return int(parts[1])
                    except Exception:
                        return -1
                # choose the encoder weight with the highest numeric index
                final_key = max(encoder_weight_keys, key=key_index)
                inferred = int(getattr(state[final_key], 'shape', (None,))[0])
            if inferred is None:
                # Fallback: use decoder weight with smallest index (first decoder linear)
                decoder_weight_keys = [k for k in state.keys() if k.startswith('decoder.') and k.endswith('.weight')]
                if decoder_weight_keys:
                    def key_index_dec(key):
                        parts = key.split('.')
                        try:
                            return int(parts[1])
                        except Exception:
                            return 999
                    first_dec_key = min(decoder_weight_keys, key=key_index_dec)
                    shape = getattr(state[first_dec_key], 'shape', None)
                    if shape and len(shape) > 1:
                        inferred = int(shape[1])
            latent_dim = int(inferred) if inferred is not None else 32

        model = Autoencoder(n_items, latent_dim=latent_dim)
        model.load_state_dict(model_data['state_dict'])
        model.eval()

        train_filled = data['train_filled'].astype(np.float32)
        train_tensor = torch.from_numpy(train_filled).float()

        with torch.no_grad():
            pred_centered = model(train_tensor).cpu().numpy()

        predictions = pred_centered + user_means[:, np.newaxis]

    else:
        raise ValueError(f"Unknown model format for {model_path}")

    # Compute metrics
    val_ndcg_full = ndcg_at_k_full(predictions, train_mask, val_user, val_item, val_rating, k=10)
    val_recall_full = recall_at_k_full(predictions, train_mask, val_user, val_item, val_rating, k=10, threshold=0.0)

    test_ndcg_full = ndcg_at_k_full(predictions, train_mask, test_user, test_item, test_rating, k=10)
    test_recall_full = recall_at_k_full(predictions, train_mask, test_user, test_item, test_rating, k=10, threshold=0.0)

    val_rmse = rmse(predictions, val_user, val_item, val_rating)
    val_mae = mae(predictions, val_user, val_item, val_rating)

    test_rmse = rmse(predictions, test_user, test_item, test_rating)
    test_mae = mae(predictions, test_user, test_item, test_rating)

    return {
        'model_path': str(model_path),
        'val_rmse': float(val_rmse),
        'val_mae': float(val_mae),
        'test_rmse': float(test_rmse),
        'test_mae': float(test_mae),
        'val_ndcg10': float(val_ndcg_full),
        'val_recall10': float(val_recall_full),
        'test_ndcg10': float(test_ndcg_full),
        'test_recall10': float(test_recall_full),
    }


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
    
    # Evaluate command (optional paths; will auto-discover models if none provided)
    eval_parser = subparsers.add_parser("evaluate", help="Evaluate model(s) with full ranking metrics")
    eval_parser.add_argument("--model-path", required=False, help="Path to saved model (optional)")
    eval_parser.add_argument("--splits-file", required=False, help="Path to splits file (optional)")
    
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
        # Resolve splits file: prefer user-supplied, otherwise use processed data folder
        if getattr(args, 'splits_file', None):
            splits_file = Path(args.splits_file)
        else:
            splits_file = data_processed / "splits.npz"

        if not splits_file.exists():
            print(f"Error: splits file {splits_file} not found. Run 'preprocess' first or supply --splits-file.")
            sys.exit(1)

        # If user provided a specific model path, evaluate just that one
        if getattr(args, 'model_path', None):
            metrics = evaluate_model(args.model_path, splits_file)
            print(f"Results for {metrics['model_path']}:")
            print(f"  Val RMSE: {metrics['val_rmse']:.4f}  Test RMSE: {metrics['test_rmse']:.4f}  Test NDCG@10: {metrics['test_ndcg10']:.4f}")
            return

        # Otherwise, discover models under the repository's models/ folder
        models_root = Path(__file__).parent / "models"
        if not models_root.exists():
            print(f"No models directory found at {models_root}")
            sys.exit(1)

        candidates = list(models_root.rglob("*.npz")) + list(models_root.rglob("*.pt")) + list(models_root.rglob("*.pth"))
        if not candidates:
            print(f"No model files found under {models_root}")
            sys.exit(1)

        results = []
        for fp in sorted(candidates):
            try:
                m = evaluate_model(fp, splits_file)
                results.append(m)
                print(f"Evaluated {fp.name}: test NDCG@10={m['test_ndcg10']:.4f}")
            except Exception as e:
                print(f"Failed to evaluate {fp}: {e}")

        # Print a simple comparison sorted by test NDCG@10
        if results:
            results.sort(key=lambda r: r['test_ndcg10'], reverse=True)
            print('\nModel comparison (sorted by test NDCG@10):')
            print('Model\tTest NDCG@10\tTest Recall@10\tTest RMSE')
            for r in results:
                name = Path(r['model_path']).name
                print(f"{name}\t{r['test_ndcg10']:.4f}\t{r['test_recall10']:.4f}\t{r['test_rmse']:.4f}")


if __name__ == "__main__":
    main()
