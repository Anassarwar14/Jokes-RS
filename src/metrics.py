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
