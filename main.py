#!/usr/bin/env python
"""Jokes recommendation system - single entry point."""
import sys
import argparse
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from preprocessing import preprocess
from svd import train_svd
from autoencoder import train_autoencoder


def main():
    parser = argparse.ArgumentParser(description="Jokes recommendation system")
    subparsers = parser.add_subparsers(dest="command", help="Command to run")
    
    # Preprocess command
    prep_parser = subparsers.add_parser("preprocess", help="Generate train/val/test splits")
    prep_parser.add_argument("--seed", type=int, default=42)
    
    # SVD command
    svd_parser = subparsers.add_parser("svd", help="Train SVD baseline")
    svd_parser.add_argument("--k", type=int, default=10, help="SVD rank")
    svd_parser.add_argument("--seed", type=int, default=42)
    
    # Autoencoder command
    ae_parser = subparsers.add_parser("autoencoder", help="Train autoencoder")
    ae_parser.add_argument("--latent-dim", type=int, default=32)
    ae_parser.add_argument("--epochs", type=int, default=20)
    ae_parser.add_argument("--patience", type=int, default=5)
    ae_parser.add_argument("--device", default="cpu", choices=["cpu", "cuda"])
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    data_processed = Path(__file__).parent / "data" / "processed" / f"seed_{getattr(args, 'seed', 42)}"
    splits_file = data_processed / "splits.npz"
    
    if args.command == "preprocess":
        preprocess(seed=args.seed)
    
    elif args.command == "svd":
        if not splits_file.exists():
            print(f"Error: {splits_file} not found. Run 'preprocess' first.")
            sys.exit(1)
        train_svd(splits_file, k=args.k, seed=args.seed)
    
    elif args.command == "autoencoder":
        if not splits_file.exists():
            print(f"Error: {splits_file} not found. Run 'preprocess' first.")
            sys.exit(1)
        train_autoencoder(splits_file, latent_dim=args.latent_dim, epochs=args.epochs,
                         patience=args.patience, device=args.device)


if __name__ == "__main__":
    main()
