import numpy as np
from typing import Dict, Any

def mean_absolute_error(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    return float(np.mean(np.abs(y_true - y_pred)))

def root_mean_squared_error(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    return float(np.sqrt(np.mean((y_true - y_pred) ** 2)))

def weighted_absolute_percentage_error(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    total_true = np.sum(np.abs(y_true))
    if total_true == 0:
        return 0.0
    return float(np.sum(np.abs(y_true - y_pred)) / total_true)

def forecast_bias(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    total_true = np.sum(y_true)
    if total_true == 0:
        return 0.0
    return float(np.sum(y_pred - y_true) / total_true)

def quantile_coverage(y_true: np.ndarray, y_pred_p10: np.ndarray, y_pred_p90: np.ndarray) -> float:
    within_interval = (y_true >= y_pred_p10) & (y_true <= y_pred_p90)
    return float(np.mean(within_interval))

def binary_classification_metrics(y_true: np.ndarray, y_pred: np.ndarray) -> Dict[str, float]:
    y_true_b = (y_true > 0).astype(int)
    y_pred_b = (y_pred > 0).astype(int)

    tp = np.sum((y_true_b == 1) & (y_pred_b == 1))
    fp = np.sum((y_true_b == 0) & (y_pred_b == 1))
    fn = np.sum((y_true_b == 1) & (y_pred_b == 0))

    precision = float(tp / (tp + fp)) if (tp + fp) > 0 else 0.0
    recall = float(tp / (tp + fn)) if (tp + fn) > 0 else 0.0
    f1 = float(2 * precision * recall / (precision + recall)) if (precision + recall) > 0 else 0.0

    return {"precision": precision, "recall": recall, "f1": f1}
