"""Optional multi-fidelity Gaussian Process implementation."""

from __future__ import annotations

from typing import Any


class MultiFidelityGP:
    """Linear autoregressive multi-fidelity Gaussian Process."""

    def __init__(self, kernel_low: Any = None, kernel_delta: Any = None):
        try:
            import numpy as np
            from sklearn.gaussian_process import GaussianProcessRegressor
            from sklearn.gaussian_process.kernels import RBF, ConstantKernel, WhiteKernel
        except ImportError as exc:
            raise RuntimeError(
                'Install analysis support with: pip install -e ".[analysis]"'
            ) from exc
        default_low = ConstantKernel(1.0) * RBF(1.0) + WhiteKernel(0.1)
        default_delta = ConstantKernel(1.0) * RBF(1.0) + WhiteKernel(0.1)
        self._np = np
        self.gp_low = GaussianProcessRegressor(
            kernel=kernel_low if kernel_low is not None else default_low,
            n_restarts_optimizer=5,
        )
        self.gp_delta = GaussianProcessRegressor(
            kernel=kernel_delta if kernel_delta is not None else default_delta,
            n_restarts_optimizer=5,
        )
        self.rho = 1.0

    def fit(self, x_low: Any, y_low: Any, x_high: Any, y_high: Any) -> MultiFidelityGP:
        self.gp_low.fit(x_low, y_low)
        low_at_high = self.gp_low.predict(x_high)
        denominator = float(self._np.dot(low_at_high, low_at_high)) + 1e-12
        self.rho = float(self._np.dot(low_at_high, y_high)) / denominator
        self.gp_delta.fit(x_high, y_high - self.rho * low_at_high)
        return self

    def predict(self, values: Any, return_std: bool = False) -> Any:
        low_mean, low_std = self.gp_low.predict(values, return_std=True)
        delta_mean, delta_std = self.gp_delta.predict(values, return_std=True)
        mean = self.rho * low_mean + delta_mean
        if not return_std:
            return mean
        std = self._np.sqrt(self.rho**2 * low_std**2 + delta_std**2)
        return mean, std
