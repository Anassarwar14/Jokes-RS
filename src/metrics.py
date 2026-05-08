"""Evaluation metrics for explicit rating recommenders."""
import numpy as np


def rmse(predictions, user_idx, item_idx, ratings):
    """Root mean squared error on indexed pairs."""
    pred = predictions[user_idx, item_idx]
    return float(np.sqrt(np.mean((pred - ratings) ** 2)))


def mae(predictions, user_idx, item_idx, ratings):
    """Mean absolute error on indexed pairs."""
    pred = predictions[user_idx, item_idx]
    return float(np.mean(np.abs(pred - ratings)))


def _group_by_user(user_idx, item_idx, ratings):
    """Group item indices and ratings by user id."""
    per_user = {}
    for u, i, r in zip(user_idx, item_idx, ratings):
        if u not in per_user:
            per_user[u] = {"items": [], "ratings": []}
        per_user[u]["items"].append(i)
        per_user[u]["ratings"].append(r)
    return per_user


def ndcg_at_k(predictions, user_idx, item_idx, ratings, k=10):
    """Compute mean NDCG@k using non-negative relevance from ratings."""
    per_user = _group_by_user(user_idx, item_idx, ratings)
    scores = []
    for u, data in per_user.items():
        items = np.array(data["items"], dtype=int)
        rel = np.maximum(0.0, np.array(data["ratings"], dtype=float))
        if rel.size == 0:
            continue

        pred = predictions[u, items]
        order = np.argsort(pred)[::-1][:k]
        rel_sorted = rel[order]

        denom = np.log2(np.arange(2, rel_sorted.size + 2))
        dcg = np.sum(rel_sorted / denom)

        ideal = np.sort(rel)[::-1][:k]
        ideal_denom = np.log2(np.arange(2, ideal.size + 2))
        idcg = np.sum(ideal / ideal_denom)

        if idcg > 0:
            scores.append(dcg / idcg)
    return float(np.mean(scores)) if scores else 0.0


def recall_at_k(predictions, user_idx, item_idx, ratings, k=10, threshold=0.0):
    """Compute mean Recall@k with relevant items defined by rating > threshold."""
    per_user = _group_by_user(user_idx, item_idx, ratings)
    scores = []
    for u, data in per_user.items():
        items = np.array(data["items"], dtype=int)
        rel = np.array(data["ratings"], dtype=float) > threshold
        if rel.sum() == 0:
            continue

        pred = predictions[u, items]
        order = np.argsort(pred)[::-1][:k]
        hits = rel[order].sum()
        scores.append(hits / rel.sum())
    return float(np.mean(scores)) if scores else 0.0


def ndcg_at_k_full(predictions, train_mask, val_user, val_item, val_rating, k=10):
    """Compute NDCG@k by ranking over all unseen items for each user."""
    n_users, n_items = predictions.shape
    scores = []
    
    # Group validation items by user
    val_per_user = _group_by_user(val_user, val_item, val_rating)
    
    for u in range(n_users):
        if u not in val_per_user:
            continue
            
        # Get validation items and ratings for this user
        val_items = np.array(val_per_user[u]["items"], dtype=int)
        val_rel = np.maximum(0.0, np.array(val_per_user[u]["ratings"], dtype=float))
        
        if len(val_items) == 0:
            continue
            
        # Get all candidate items (not seen in training)
        candidate_items = np.where(~train_mask[u])[0]
        
        if len(candidate_items) == 0:
            continue
            
        # Get predictions for all candidates
        candidate_pred = predictions[u, candidate_items]
        
        # Sort candidates by prediction score (descending)
        sort_idx = np.argsort(candidate_pred)[::-1]
        sorted_candidates = candidate_items[sort_idx]
        
        # Find positions of relevant items in the ranking
        rel_positions = []
        for rel_item in val_items:
            pos = np.where(sorted_candidates == rel_item)[0]
            if len(pos) > 0:
                rel_positions.append(pos[0])
        
        if not rel_positions:
            continue
            
        # Compute DCG@k
        dcg = 0.0
        for pos in rel_positions:
            if pos < k:  # Only count if within top-k
                dcg += val_rel[np.where(val_items == sorted_candidates[pos])[0][0]] / np.log2(pos + 2)
        
        # Compute IDCG@k (ideal DCG)
        ideal_rel = np.sort(val_rel)[::-1][:k]
        idcg = np.sum(ideal_rel / np.log2(np.arange(2, len(ideal_rel) + 2)))
        
        if idcg > 0:
            scores.append(dcg / idcg)
    
    return float(np.mean(scores)) if scores else 0.0


def recall_at_k_full(predictions, train_mask, val_user, val_item, val_rating, k=10, threshold=0.0):
    """Compute Recall@k by ranking over all unseen items for each user."""
    n_users, n_items = predictions.shape
    scores = []
    
    # Group validation items by user
    val_per_user = _group_by_user(val_user, val_item, val_rating)
    
    for u in range(n_users):
        if u not in val_per_user:
            continue
            
        # Get validation items and ratings for this user
        val_items = np.array(val_per_user[u]["items"], dtype=int)
        val_rel = np.array(val_per_user[u]["ratings"], dtype=float) > threshold
        
        if val_rel.sum() == 0:
            continue
            
        # Get all candidate items (not seen in training)
        candidate_items = np.where(~train_mask[u])[0]
        
        if len(candidate_items) == 0:
            continue
            
        # Get predictions for all candidates
        candidate_pred = predictions[u, candidate_items]
        
        # Sort candidates by prediction score (descending)
        sort_idx = np.argsort(candidate_pred)[::-1]
        sorted_candidates = candidate_items[sort_idx][:k]  # Top-k recommendations
        
        # Count relevant items in top-k
        hits = 0
        for item in sorted_candidates:
            if item in val_items:
                rel_idx = np.where(val_items == item)[0][0]
                if val_rel[rel_idx]:
                    hits += 1
        
        scores.append(hits / val_rel.sum())
    
    return float(np.mean(scores)) if scores else 0.0
