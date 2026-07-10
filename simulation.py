"""
Simulation module for superconductor discovery pipeline.

Provides multi-fidelity GP and simulation classes.
"""

import numpy as np
from sklearn.gaussian_process import GaussianProcessRegressor
from sklearn.gaussian_process.kernels import RBF, WhiteKernel, ConstantKernel


class MultiFidelityGP:
    """
    Multi-fidelity Gaussian Process model combining low-fidelity ML predictions
    with high-fidelity DFT calculations.

    Uses a linear multi-fidelity scheme: f_high(x) = rho * f_low(x) + delta(x)
    where rho is a scaling factor and delta is a GP modeling the discrepancy.
    """

    def __init__(self, kernel_low=None, kernel_delta=None):
        if kernel_low is None:
            kernel_low = ConstantKernel(1.0) * RBF(length_scale=1.0) + WhiteKernel(noise_level=0.1)
        if kernel_delta is None:
            kernel_delta = ConstantKernel(1.0) * RBF(length_scale=1.0) + WhiteKernel(noise_level=0.1)
        self.gp_low = GaussianProcessRegressor(kernel=kernel_low, n_restarts_optimizer=5)
        self.gp_delta = GaussianProcessRegressor(kernel=kernel_delta, n_restarts_optimizer=5)
        self.rho = 1.0

    def fit(self, X_low, y_low, X_high, y_high):
        """Fit the multi-fidelity GP model."""
        self.gp_low.fit(X_low, y_low)
        y_low_pred = self.gp_low.predict(X_high)
        # Estimate rho and fit delta GP
        delta = y_high - y_low_pred
        self.rho = np.cov(y_low_pred.flatten(), y_high.flatten())[0, 1] / (np.var(y_low_pred) + 1e-10)
        self.gp_delta.fit(X_high, delta)
        return self

    def predict(self, X, return_std=False):
        """Predict using the multi-fidelity model."""
        y_low_mean, y_low_std = self.gp_low.predict(X, return_std=True)
        y_delta_mean, y_delta_std = self.gp_delta.predict(X, return_std=True)
        y_mean = self.rho * y_low_mean + y_delta_mean
        if return_std:
            y_std = np.sqrt(self.rho**2 * y_low_std**2 + y_delta_std**2)
            return y_mean, y_std
        return y_mean
