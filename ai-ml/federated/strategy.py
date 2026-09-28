import numpy as np
import flwr as fl
from typing import Dict, List, Tuple, Optional

class FedProxStrategy(fl.server.strategy.FedAvg):
    """FedProx Strategy for non-IID cross-country healthcare data."""

    def __init__(self, mu: float = 0.01, **kwargs):
        super().__init__(**kwargs)
        self.mu = mu

    def aggregate_fit(
        self,
        server_round: int,
        results: List[Tuple[fl.server.client_proxy.ClientProxy, fl.common.FitRes]],
        failures: List[Tuple[fl.server.client_proxy.ClientProxy, fl.common.FitRes]]
    ) -> Tuple[Optional[fl.common.Parameters], Dict[str, float]]:
        """Aggregated parameters using FedAvg weighting with proximal term consideration."""
        aggregated_parameters, metrics = super().aggregate_fit(server_round, results, failures)
        metrics["mu"] = self.mu
        return aggregated_parameters, metrics
