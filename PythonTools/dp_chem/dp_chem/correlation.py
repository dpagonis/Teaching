import matplotlib.pyplot as plt
import numpy as np

from .odr import odr
from . import _fig_tools



class correlation:
    _counter = 0

    def __init__(self, ts1, ts2):
        """
        Initialize the Correlation class for time series analysis. Order is x axis, y axis

        :param ts1: First merged timeseries object.
        :param ts2: Second merged timeseries object.
        """
        if ts1.is_merged(ts2):
            self.ts1 = ts1
            self.ts2 = ts2
        else:
            raise ValueError("Time series are not merged")

        # Attributes for basic correlation
        self.regression = odr(ts1.data,ts2.data)
        self.slope = self.regression.slope
        self.intercept = self.regression.intercept
        self.R2 = self._calc_r2() 

    def _calc_r2(self):
        # Calculate R^2
        x=self.ts1.data
        y = self.ts2.data
        valid_mask = ~np.isnan(x) & ~np.isnan(y)
        x = x[valid_mask]
        y = y[valid_mask]
        if len(x) < 2:
            raise ValueError("Insufficient valid data points to calculate R².")
        y_pred = self.slope * x + self.intercept
        ss_residual = np.sum((y - y_pred) ** 2)  # Residual sum of squares
        ss_total = np.sum((y - np.mean(y)) ** 2)  # Total sum of squares
        r2 = 1 - (ss_residual / ss_total)
        return r2
    
    def plot(self, include_1_1 =False, show=True, save = False):
        """
        Plot the correlation between the two time series and return the figure object.
        """
        if self.ts1.data is None or self.ts2.data is None:
            raise ValueError("Time series data is missing.")

        fig, ax = plt.subplots(figsize=(4, 4))
        
        ax.scatter(self.ts1.data, self.ts2.data, alpha=0.7)
        
        ax.plot(
            self.regression.trendline_x,
            self.regression.trendline_y,
            'k-',
            label=f"ODR: y = {self.slope:.02g} x {'+' if self.intercept > 0 else '-'} {abs(self.intercept):.02g}\n$R^2$ = {self.R2:.03f}"
        )

        if include_1_1: 
            ax.plot([min(self.ts2.data), max(self.ts2.data)],[min(self.ts2.data), max(self.ts2.data)],'k--', label="1:1 Line" )

        ax.set_xlabel(f"{self.ts1.name}")
        ax.set_ylabel(f"{self.ts2.name}")
        ax.legend()
        ax.grid(alpha=0.2)
        fig.tight_layout()

        if save: _fig_tools.save(fig)
        if show: plt.show()
        plt.close(fig)
        return fig
     
