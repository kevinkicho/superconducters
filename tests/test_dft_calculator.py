# Reference: Lu et al., Transfer learning for physics-informed neural networks, CMAME, 2021. https://doi.org/10.1016/j.cma.2021.113933
import pytest
import torch
import torch.nn as nn
from torch_geometric.data import Data
from dft_calculator import fine_tune_pinn_on_real_data, get_device


class SimpleModel(nn.Module):
    """Minimal model that processes a graph's node features to predict Tc."""
    def __init__(self, in_dim=10, hidden=16):
        super().__init__()
        self.lin1 = nn.Linear(in_dim, hidden)
        self.lin2 = nn.Linear(hidden, 1)

    def forward(self, data):
        x = data.x
        x = torch.relu(self.lin1(x))
        return self.lin2(x).squeeze()


def test_fine_tune_pinn_on_real_data():
    """Validate that fine-tuning reduces RMSE on synthetic real data."""
    device = get_device()
    model = SimpleModel().to(device)

    # Create 5 synthetic graphs with random node features and target Tc values
    real_data = []
    for _ in range(5):
        x = torch.randn(1, 10)
        edge_index = torch.tensor([[0], [0]], dtype=torch.long)  # self-loop
        graph = Data(x=x, edge_index=edge_index)
        tc = torch.randn(1).item() * 10 + 100
        real_data.append((graph, tc))

    # Compute initial RMSE
    model.eval()
    initial_losses = []
    for graph, tc in real_data:
        graph = graph.to(device)
        pred = model(graph).squeeze()
        loss = nn.MSELoss()(pred, torch.tensor(tc, device=device))
        initial_losses.append(loss.item())
    initial_rmse = (sum(initial_losses) / len(initial_losses)) ** 0.5

    # Fine-tune
    model = fine_tune_pinn_on_real_data(model, real_data, epochs=10, lr=1e-3, device=device)

    # Compute final RMSE
    model.eval()
    final_losses = []
    for graph, tc in real_data:
        graph = graph.to(device)
        pred = model(graph).squeeze()
        loss = nn.MSELoss()(pred, torch.tensor(tc, device=device))
        final_losses.append(loss.item())
    final_rmse = (sum(final_losses) / len(final_losses)) ** 0.5

    # Assert RMSE decreased significantly
    assert final_rmse < initial_rmse, (
        f"RMSE did not decrease: initial {initial_rmse:.4f}, final {final_rmse:.4f}"
    )
    assert final_rmse < 0.5 * initial_rmse, (
        f"RMSE reduction insufficient: {final_rmse / initial_rmse:.2%} of initial"
    )


def test_get_device():
    """Test get_device returns a torch device."""
    device = get_device()
    assert isinstance(device, torch.device)


def test_fine_tune_pinn_on_real_data_no_improvement():
    """Test fine-tuning with zero epochs does not change model."""
    device = get_device()
    model = SimpleModel().to(device)
    initial_params = [p.clone() for p in model.parameters()]
    real_data = []
    for _ in range(2):
        x = torch.randn(1, 10)
        edge_index = torch.tensor([[0], [0]], dtype=torch.long)
        graph = Data(x=x, edge_index=edge_index)
        tc = torch.randn(1).item() * 10 + 100
        real_data.append((graph, tc))
    model = fine_tune_pinn_on_real_data(model, real_data, epochs=0, lr=1e-3, device=device)
    final_params = [p for p in model.parameters()]
    for p_initial, p_final in zip(initial_params, final_params):
        assert torch.equal(p_initial, p_final)


def test_fine_tune_pinn_on_real_data_empty_data():
    """Test fine-tuning with empty data returns model unchanged."""
    device = get_device()
    model = SimpleModel().to(device)
    model = fine_tune_pinn_on_real_data(model, [], epochs=5, lr=1e-3, device=device)
    assert model is not None
