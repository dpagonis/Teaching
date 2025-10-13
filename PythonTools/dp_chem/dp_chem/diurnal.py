import numpy as np
import matplotlib.pyplot as plt

from .timeseries import timeseries
from . import _fig_tools

class diurnal:
    def __init__(self, ts):
        """
        Initialize the diurnal class, grouping the timeseries data by hour of the day.

        Parameters:
            ts (timeseries): A timeseries object containing data and timestamps.
        """
        if not isinstance(ts, timeseries):
            raise TypeError("Input must be an instance of the `timeseries` class.")

        self.ts = ts

        # Extract hours from timestamps
        hours = np.array([t.hour for t in ts.t])

        # Initialize storage for hourly statistics
        self.hours = np.arange(24)
        self.mean = np.full(24, np.nan)
        self.stdev = np.full(24, np.nan)
        self.n = np.zeros(24, dtype=int)

        # Calculate statistics for each hour
        for hour in self.hours:
            in_hour = (hours == hour)
            data_in_hour = ts.data[in_hour]

            if len(data_in_hour) > 0:
                self.mean[hour] = np.nanmean(data_in_hour)
                self.stdev[hour] = np.nanstd(data_in_hour)
                self.n[hour] = np.sum(~np.isnan(data_in_hour))

    def plot(self, show=True, save=False):
        """
        Plot the diurnal cycle, including error bars for standard deviation.

        Parameters:
            show (bool, optional): Whether to display the plot. Defaults to True.

        Returns:
            matplotlib.figure.Figure: The figure object for the plot.
        """
        fig, ax = plt.subplots(figsize=(6, 4))

        fractional_hours = np.array([t.hour + t.minute/60 for t in self.ts.t])

        ax.scatter(fractional_hours,self.ts.data,alpha=0.7,color='grey',s=2,edgecolors=None,label='All data')

        ax.errorbar(
            self.hours+0.5, self.mean, yerr=self.stdev,
            fmt='o-', color='black', ecolor='black', elinewidth=2, capsize=3,
            label='Mean ± Stdev'
        )

        ax.set_xlabel('Hour of the Day')
        ax.set_ylabel(f"{self.ts.name}")
        ax.set_xticks(self.hours)
        ax.legend()
        ax.grid(alpha=0.2)

        plt.tight_layout()

        if save: _fig_tools.save(fig)
        if show: plt.show()
        plt.close(fig)
        return fig