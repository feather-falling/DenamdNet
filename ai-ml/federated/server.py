import flwr as fl
from typing import Dict, Any
from .strategy import FedProxStrategy

class FederationServer:
    """Flower Server for aggregating models from India, Brazil, and South Africa."""

    def __init__(self, num_rounds: int = 5, mu: float = 0.01):
        self.num_rounds = num_rounds
        self.mu = mu
        self.strategy = FedProxStrategy(
            mu=self.mu,
            min_fit_clients=3,
            min_available_clients=3
        )

    def start(self, server_address: str = "0.0.0.0:8080"):
        """Starts Flower server."""
        fl.server.start_server(
            server_address=server_address,
            config=fl.server.ServerConfig(num_rounds=self.num_rounds),
            strategy=self.strategy
        )
