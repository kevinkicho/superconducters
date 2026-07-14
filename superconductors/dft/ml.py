"""Optional Torch helpers kept outside the DFT execution core."""

from __future__ import annotations

from typing import Any


def get_device(force_cpu: bool = False) -> Any:
    torch = _torch()
    if force_cpu:
        return torch.device("cpu")
    return torch.device("cuda" if torch.cuda.is_available() else "cpu")


def fine_tune_pinn_on_real_data(
    model: Any,
    real_data: list[tuple[Any, float]],
    epochs: int = 10,
    lr: float = 1e-4,
    device: Any = None,
) -> Any:
    if epochs < 0:
        raise ValueError("epochs cannot be negative")
    if not real_data or epochs == 0:
        return model
    torch = _torch()
    device = device or get_device()
    model = model.to(device)
    model.train()
    optimizer = torch.optim.Adam(model.parameters(), lr=lr)
    loss_fn = torch.nn.MSELoss()
    for _ in range(epochs):
        for graph, measured_tc in real_data:
            graph = graph.to(device)
            optimizer.zero_grad()
            prediction = model(graph).squeeze()
            target = torch.as_tensor(measured_tc, dtype=prediction.dtype, device=device)
            loss = loss_fn(prediction, target)
            loss.backward()
            optimizer.step()
    return model


def _torch() -> Any:
    try:
        import torch
    except ImportError as exc:
        raise RuntimeError('Install Torch helpers with: pip install -e ".[ml]"') from exc
    return torch
