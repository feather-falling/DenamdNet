import numpy as np
import torch
import flwr as fl
from typing import Dict, List, Tuple
from ..models.demand_forecaster import DemandNetModule, PinballLoss

class CountryFlowerClient(fl.client.NumPyClient):
    """Flower client representing a national node (e.g. India, Brazil, South Africa).
    Keeps raw healthcare data strictly local to the node.
    """

    def __init__(self, country_code: str, model: DemandNetModule, train_loader: torch.utils.data.DataLoader, val_loader: torch.utils.data.DataLoader, lr: float = 0.001):
        self.country_code = country_code
        self.model = model
        self.train_loader = train_loader
        self.val_loader = val_loader
        self.lr = lr
        self.criterion = PinballLoss()
        self.optimizer = torch.optim.Adam(self.model.parameters(), lr=self.lr)

    def get_parameters(self, config: Dict[str, str]) -> List[np.ndarray]:
        return [val.cpu().numpy() for val in self.model.state_dict().values()]

    def set_parameters(self, parameters: List[np.ndarray]):
        params_dict = zip(self.model.state_dict().keys(), parameters)
        state_dict = {k: torch.tensor(v) for k, v in params_dict}
        self.model.load_state_dict(state_dict, strict=True)

    def fit(self, parameters: List[np.ndarray], config: Dict[str, str]) -> Tuple[List[np.ndarray], int, Dict]:
        self.set_parameters(parameters)
        self.model.train()

        epochs = int(config.get("local_epochs", 2))
        total_loss = 0.0
        num_samples = 0

        for epoch in range(epochs):
            for batch_seq, batch_tab, batch_med, batch_y in self.train_loader:
                self.optimizer.zero_grad()
                out = self.model(batch_seq, batch_tab, batch_med)
                loss = self.criterion(out, batch_y)
                loss.backward()
                self.optimizer.step()

                total_loss += loss.item() * len(batch_y)
                num_samples += len(batch_y)

        avg_loss = total_loss / max(1, num_samples)
        return self.get_parameters(config={}), num_samples, {"country": self.country_code, "train_loss": avg_loss}

    def evaluate(self, parameters: List[np.ndarray], config: Dict[str, str]) -> Tuple[float, int, Dict]:
        self.set_parameters(parameters)
        self.model.eval()

        total_loss = 0.0
        num_samples = 0

        with torch.no_grad():
            for batch_seq, batch_tab, batch_med, batch_y in self.val_loader:
                out = self.model(batch_seq, batch_tab, batch_med)
                loss = self.criterion(out, batch_y)
                total_loss += loss.item() * len(batch_y)
                num_samples += len(batch_y)

        avg_loss = total_loss / max(1, num_samples)
        return avg_loss, num_samples, {"country": self.country_code, "val_loss": avg_loss}
