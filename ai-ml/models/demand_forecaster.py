import numpy as np
import pandas as pd
import lightgbm as lgb
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, TensorDataset
from typing import Dict, Any, List, Tuple, Optional

class LightGBMForecaster:
    """Multi-quantile LightGBM demand forecaster outputting P10, P50, P90 for 7 horizon steps."""

    def __init__(self, quantiles=[0.10, 0.50, 0.90], horizon=7, n_estimators=100, learning_rate=0.05):
        self.quantiles = quantiles
        self.horizon = horizon
        self.n_estimators = n_estimators
        self.learning_rate = learning_rate
        self.models = {}
        self.feature_cols = []

    def fit(self, df: pd.DataFrame, target_col: str = "demand_units"):
        exclude_cols = ["date", "phc_id", "medicine_id", "district", "provenance", "event_id", target_col]
        self.feature_cols = [c for c in df.columns if c not in exclude_cols and pd.api.types.is_numeric_dtype(df[c])]

        X = df[self.feature_cols].apply(pd.to_numeric, errors="coerce").fillna(0).values.astype(np.float32)
        y = df[target_col].fillna(0).values.astype(np.float32)

        for h in range(1, self.horizon + 1):
            y_h = np.roll(y, -h)
            valid_mask = np.ones(len(y), dtype=bool)
            valid_mask[-h:] = False

            X_h = X[valid_mask]
            y_h_clean = y_h[valid_mask]

            for q in self.quantiles:
                model = lgb.LGBMRegressor(
                    objective="quantile",
                    alpha=q,
                    n_estimators=self.n_estimators,
                    learning_rate=self.learning_rate,
                    num_leaves=31,
                    verbose=-1,
                    random_state=42
                )
                model.fit(X_h, y_h_clean)
                self.models[(h, q)] = model

    def predict(self, df: pd.DataFrame) -> np.ndarray:
        X = df[self.feature_cols].apply(pd.to_numeric, errors="coerce").fillna(0).values.astype(np.float32)
        N = len(df)
        preds = np.zeros((N, self.horizon, len(self.quantiles)))

        for h in range(1, self.horizon + 1):
            for q_idx, q in enumerate(self.quantiles):
                model = self.models.get((h, q))
                if model is not None:
                    preds[:, h - 1, q_idx] = model.predict(X)

        # Enforce quantile non-crossing: P10 <= P50 <= P90
        preds[:, :, 0] = np.maximum(0, preds[:, :, 0])
        preds[:, :, 1] = np.maximum(preds[:, :, 0], preds[:, :, 1])
        preds[:, :, 2] = np.maximum(preds[:, :, 1], preds[:, :, 2])
        return preds

class DemandNetModule(nn.Module):
    """DemandNet PyTorch Module: GRU sequence encoder + Tabular encoder + Medicine embedding -> Multi-horizon quantile output."""

    def __init__(self, seq_in_dim: int, tab_in_dim: int, num_medicines: int = 25, embed_dim: int = 8, hidden_dim: int = 64, horizon: int = 7, num_quantiles: int = 3):
        super().__init__()
        self.med_embed = nn.Embedding(num_medicines, embed_dim)
        self.gru = nn.GRU(seq_in_dim, hidden_dim, num_layers=2, batch_first=True, dropout=0.1)
        self.tab_fc = nn.Sequential(
            nn.Linear(tab_in_dim, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, 32)
        )
        combined_dim = hidden_dim + 32 + embed_dim
        self.mlp = nn.Sequential(
            nn.Linear(combined_dim, 128),
            nn.ReLU(),
            nn.Dropout(0.1),
            nn.Linear(128, 64),
            nn.ReLU(),
            nn.Linear(64, horizon * num_quantiles)
        )
        self.horizon = horizon
        self.num_quantiles = num_quantiles

    def forward(self, x_seq: torch.Tensor, x_tab: torch.Tensor, x_med: torch.Tensor) -> torch.Tensor:
        _, h_n = self.gru(x_seq)
        seq_out = h_n[-1]

        tab_out = self.tab_fc(x_tab)
        med_out = self.med_embed(x_med)

        combined = torch.cat([seq_out, tab_out, med_out], dim=1)
        out = self.mlp(combined)
        return out.view(-1, self.horizon, self.num_quantiles)

class PinballLoss(nn.Module):
    """Multi-quantile Pinball / Quantile Loss."""

    def __init__(self, quantiles=[0.10, 0.50, 0.90]):
        super().__init__()
        self.quantiles = quantiles

    def forward(self, pred: torch.Tensor, target: torch.Tensor) -> torch.Tensor:
        target = target.unsqueeze(-1).expand_as(pred)
        errors = target - pred
        loss = 0.0
        for i, q in enumerate(self.quantiles):
            err = errors[:, :, i]
            loss += torch.max(q * err, (q - 1) * err).mean()
        return loss

class DemandNetForecaster:
    """Wrapper class for DemandNet training and inference."""

    def __init__(self, seq_len=28, horizon=7, quantiles=[0.10, 0.50, 0.90], epochs=5, batch_size=128, lr=0.001):
        self.seq_len = seq_len
        self.horizon = horizon
        self.quantiles = quantiles
        self.epochs = epochs
        self.batch_size = batch_size
        self.lr = lr
        self.net = None
        self.med_to_id = {}

    def _prepare_tensors(self, df: pd.DataFrame, target_col: str = "demand_units"):
        med_ids = df["medicine_id"].astype("category").cat.codes.values
        unique_meds = df["medicine_id"].unique()
        self.med_to_id = {m: i for i, m in enumerate(unique_meds)}

        exclude = ["date", "phc_id", "medicine_id", "district", "provenance", "event_id", target_col]
        feature_cols = [c for c in df.columns if c not in exclude and pd.api.types.is_numeric_dtype(df[c])]

        X_num = df[feature_cols].apply(pd.to_numeric, errors="coerce").fillna(0).values.astype(np.float32)
        y_val = df[target_col].fillna(0).values.astype(np.float32)

        N = len(df)
        seq_features = []
        tab_features = []
        med_features = []
        targets = []

        step_sample = max(1, N // 10000)
        for i in range(self.seq_len, N - self.horizon, step_sample):
            seq = X_num[i - self.seq_len : i]
            tab = X_num[i]
            med = med_ids[i]
            targ = y_val[i : i + self.horizon]

            seq_features.append(seq)
            tab_features.append(tab)
            med_features.append(med)
            targets.append(targ)

        return (
            torch.tensor(np.array(seq_features), dtype=torch.float32),
            torch.tensor(np.array(tab_features), dtype=torch.float32),
            torch.tensor(np.array(med_features), dtype=torch.long),
            torch.tensor(np.array(targets), dtype=torch.float32),
            feature_cols
        )

    def fit(self, df: pd.DataFrame, target_col: str = "demand_units"):
        x_seq, x_tab, x_med, y_targ, feature_cols = self._prepare_tensors(df, target_col)
        num_meds = max(len(self.med_to_id), 30)

        self.net = DemandNetModule(
            seq_in_dim=x_seq.shape[2],
            tab_in_dim=x_tab.shape[1],
            num_medicines=num_meds,
            horizon=self.horizon,
            num_quantiles=len(self.quantiles)
        )

        dataset = TensorDataset(x_seq, x_tab, x_med, y_targ)
        loader = DataLoader(dataset, batch_size=self.batch_size, shuffle=True)

        optimizer = optim.Adam(self.net.parameters(), lr=self.lr)
        criterion = PinballLoss(self.quantiles)

        self.net.train()
        for epoch in range(self.epochs):
            for batch_seq, batch_tab, batch_med, batch_y in loader:
                optimizer.zero_grad()
                out = self.net(batch_seq, batch_tab, batch_med)
                loss = criterion(out, batch_y)
                loss.backward()
                optimizer.step()

    def predict(self, df: pd.DataFrame) -> np.ndarray:
        if self.net is None:
            raise RuntimeError("DemandNet is not trained yet.")
        self.net.eval()

        exclude = ["date", "phc_id", "medicine_id", "district", "provenance", "event_id", "demand_units"]
        feature_cols = [c for c in df.columns if c not in exclude and pd.api.types.is_numeric_dtype(df[c])]

        X_num = df[feature_cols].apply(pd.to_numeric, errors="coerce").fillna(0).values.astype(np.float32)
        med_codes = df["medicine_id"].map(lambda m: self.med_to_id.get(m, 0)).values

        N = len(df)
        preds = np.zeros((N, self.horizon, len(self.quantiles)))

        batch_size = 512
        with torch.no_grad():
            for i in range(0, N, batch_size):
                end_idx = min(N, i + batch_size)
                seq_batch = []
                tab_batch = []
                med_batch = []

                for idx in range(i, end_idx):
                    if idx < self.seq_len:
                        seq = np.tile(X_num[idx], (self.seq_len, 1))
                    else:
                        seq = X_num[idx - self.seq_len : idx]
                    seq_batch.append(seq)
                    tab_batch.append(X_num[idx])
                    med_batch.append(med_codes[idx])

                t_seq = torch.tensor(np.array(seq_batch), dtype=torch.float32)
                t_tab = torch.tensor(np.array(tab_batch), dtype=torch.float32)
                t_med = torch.tensor(np.array(med_batch), dtype=torch.long)

                out = self.net(t_seq, t_tab, t_med)
                preds[i:end_idx] = out.cpu().numpy()

        preds[:, :, 0] = np.maximum(0, preds[:, :, 0])
        preds[:, :, 1] = np.maximum(preds[:, :, 0], preds[:, :, 1])
        preds[:, :, 2] = np.maximum(preds[:, :, 1], preds[:, :, 2])
        return preds
