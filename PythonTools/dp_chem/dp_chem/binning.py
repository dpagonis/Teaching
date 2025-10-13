import warnings
import numpy as np

from .timeseries import timeseries
from . import _fig_tools

# Suppress specific warnings related to empty slices and degrees of freedom -- we are set up to handle these just fine
warnings.filterwarnings("ignore", message="Mean of empty slice")
warnings.filterwarnings("ignore", message="Degrees of freedom <= 0 for slice")

class binning:
    def __init__(self, reference_ts, target_ts, bins=10, fixed_width=False):
        """
        Initialize the binned_data class.

        :param reference_ts: `timeseries` object used to determine bin edges.
        :param target_ts: `timeseries` object to be binned.
        :param bins: Number of bins or an array of bin edges.
        :param fixed_width: If True, use fixed-width bins with the width derived from the range of reference data.
                            If a number (int or float), use this as the fixed width of each bin.
        """
        # Ensure both inputs are timeseries and merged
        if not isinstance(reference_ts, timeseries) or not isinstance(target_ts, timeseries):
            raise TypeError("Both inputs must be instances of the `timeseries` class.")
        if not reference_ts.is_merged(target_ts):
            raise ValueError("The time series must be merged.")

        self.reference_ts = reference_ts
        self.target_ts = target_ts
        self._bins = bins
        self.fixed_width = fixed_width

        # Calculate bin edges
        ref_min, ref_max = np.nanmin(reference_ts.data), np.nanmax(reference_ts.data)
        if isinstance(fixed_width, (int, float)) and not isinstance(fixed_width, bool):  # Explicit fixed-width binning
            start = np.floor(ref_min / fixed_width) * fixed_width
            stop = np.ceil(ref_max / fixed_width) * fixed_width
            self.bin_edges = np.arange(start, stop + fixed_width, fixed_width)
        elif fixed_width is True:  # Fixed-width based on the number of bins
            # Divide the range into `bins` equal-width intervals
            bin_width = (ref_max - ref_min) / bins
            start = np.floor(ref_min / bin_width) * bin_width
            stop = np.ceil(ref_max / bin_width) * bin_width
            self.bin_edges = np.linspace(start, stop, bins + 1)  # Ensure `bins` equal-width intervals
        elif isinstance(self._bins, (list, np.ndarray)):  # Custom bin edges
            self.bin_edges = np.array(self._bins)
        elif isinstance(self._bins, int):  # Percentile-based binning
            self.bin_edges = np.nanpercentile(reference_ts.data, np.linspace(0, 100, self._bins + 1))
        else:
            raise TypeError("Bins must be an integer, an array of bin edges, or fixed_width must be specified.")

        #calculate bin centers
        if isinstance(self._bins, int) and not fixed_width:  # Percentile-based binning
            # Use the 50th percentile (median) for each bin's center
            self.bin_centers = []
            for i in range(len(self.bin_edges) - 1):
                in_bin = (reference_ts.data >= self.bin_edges[i]) & (reference_ts.data < self.bin_edges[i + 1])
                bin_data = reference_ts.data[in_bin]
                if len(bin_data) > 0:
                    self.bin_centers.append(np.nanpercentile(bin_data, 50))  # Median
                else:
                    self.bin_centers.append((self.bin_edges[i] + self.bin_edges[i + 1]) / 2)  # Fallback to midpoint
            self.bin_centers = np.array(self.bin_centers)
        else:
            # Fixed-width or custom bin edges: use midpoint of bin edges
            self.bin_centers = (self.bin_edges[:-1] + self.bin_edges[1:]) / 2


        # Bin the target data, calculate statistics, and fit
        self.binned_indices = self._binEm()
        self.bin_means, self.bin_n, self.bin_stdev = self._calculate_bin_stats()
        self.slope, self.intercept, self.R2 = self._fit_bin_means()

    def _calculate_bin_stats(self):
        """
        Calculate statistics (mean, count, standard deviation) of the target data for each bin.

        Returns:
            tuple: (np array of means, np array of counts, np array of standard deviations)
        """
        bin_means = []
        bin_counts = []
        bin_stdevs = []
        
        for i in range(1, len(self.bin_edges)):
            in_bin = (self.binned_indices == i)
            bin_data = self.target_ts.data[in_bin]

            # Mean
            bin_means.append(np.nanmean(bin_data))  # Handle NaNs gracefully

            # Count
            bin_counts.append(np.sum(~np.isnan(bin_data)))  # Exclude NaNs in count

            # Standard Deviation
            bin_stdevs.append(np.nanstd(bin_data))  # Handle NaNs gracefully

        return np.array(bin_means), np.array(bin_counts), np.array(bin_stdevs)
    
    def _binEm(self):
        # Manually calculate bin indices for each point in target data
        binned_indices = []
        for value in self.reference_ts.data:
            if np.isnan(value):  # Handle NaNs explicitly
                binned_indices.append(np.nan)
            else:
                for i in range(len(self.bin_edges) - 1):
                    if self.bin_edges[i] <= value < self.bin_edges[i + 1]:
                        binned_indices.append(i + 1)  # Bin indices start at 1
                        break
                else:
                    # Value falls outside the bin range
                    binned_indices.append(0 if value < self.bin_edges[0] else len(self.bin_edges))

        return np.array(binned_indices, dtype=np.float64)
    
    def _fit_bin_means(self):
        """
        Perform a weighted linear fit of bin_means vs. bin_centers.
        Weights are based on the number of points (bin_n) in each bin.

        Returns:
            fit_slope (float): Slope of the fit.
            fit_intercept (float): Intercept of the fit.
            r2 (float): Coefficient of determination (R^2) for the fit.
        """
        # Ensure we have valid data for fitting
        valid_bins = ~np.isnan(self.bin_means) & (self.bin_n > 0)
        x = self.bin_centers[valid_bins]
        y = self.bin_means[valid_bins]
        weights = self.bin_n[valid_bins]

        if len(x) < 2:
            raise ValueError("Not enough valid bins to perform a fit.")

        # Perform weighted least squares regression
        W = np.diag(weights)  # Weight matrix
        X = np.vstack((x, np.ones_like(x))).T  # Design matrix: [x, 1]
        beta = np.linalg.inv(X.T @ W @ X) @ X.T @ W @ y  # Weighted least squares solution

        fit_slope = beta[0]  # Slope of the fit
        fit_intercept = beta[1]  # Intercept of the fit

        # Calculate R^2
        y_pred = fit_slope * x + fit_intercept
        ss_residual = np.sum(weights * (y - y_pred) ** 2)  # Weighted residual sum of squares
        ss_total = np.sum(weights * (y - np.average(y, weights=weights)) ** 2)  # Weighted total sum of squares
        r2 = 1 - (ss_residual / ss_total)

        return fit_slope, fit_intercept, r2



    def plot(self, include_fit=True, show=True, save=False):
        """
        Plot the entire dataset and the binned data with error bars.

        Parameters:
            include_fit (bool, optional): Whether to include the fit line for bin_means 
                vs. bin_centers. The fit line is labeled with the slope, intercept, 
                and R² value. Defaults to True.
            show (bool, optional): Whether to display the plot interactively. 
                If False, the plot is not shown, which is useful for batch processing. 
                Defaults to True.
            save (bool, optional): Whether to save the plot as a PNG file in the 
                directory of the outermost script (`__main__`). The file name will 
                match the script name, replacing the `.py` extension with `.png`. 
                Defaults to False.

        Returns:
            matplotlib.figure.Figure: The Matplotlib figure object for the plot.
        """
        import matplotlib.pyplot as plt

        # Bin labels for special cases
        bin_labels = {
            2: "Halves", 3: "Tertiles", 4: "Quartiles", 5: "Quintiles",
            6: "Sextiles", 7: "Septiles", 8: "Octiles", 10: "Deciles",
            12: "Dodeciles", 20: "Vigintiles"
        }
        
        if self.fixed_width is True:  
            sLabel = f"Binned data\n(Fixed width N={len(self.bin_centers)})"
        elif self.fixed_width is False: #percentile naming
            sLabel = bin_labels.get(self._bins, f"Binned data (N={len(self.bin_centers)})")
        elif isinstance(self.fixed_width, (int, float)): # Explicit fixed-width binning
            sLabel = f"Binned data (width={self.fixed_width})"
        else: #catch-all
            sLabel = bin_labels.get(self._bins, f"Binned data")

        # Plot the entire dataset
        fig,ax = plt.subplots(figsize=(5, 4))

        all_handle = ax.scatter(
            self.reference_ts.data,
            self.target_ts.data,
            alpha=0.3,  # Transparency for all data points
            color='grey',
            s=2,
            edgecolors=None,
            label='All data'
        )

        # Overlay binned data with error bars
        binned_handle = ax.errorbar(
            self.bin_centers,
            self.bin_means,
            yerr=self.bin_stdev,
            fmt='o',
            color='black',
            ecolor='black',
            elinewidth=1,
            capsize=3,
            label=sLabel
        )

        # Include the fit line if requested
        if include_fit:
            x_fit = np.array([self.bin_centers.min(), self.bin_centers.max()])
            y_fit = self.slope * x_fit + self.intercept
            fit_handle = ax.plot(
                x_fit, y_fit, color='black', linestyle='-', label=f"y = {self.slope:.2g}x {'+' if self.intercept >= 0 else '-'} {abs(self.intercept):.2g}\n(R²={self.R2:.2f})"
            )
            fit_handle=fit_handle[0]
        else: 
            fit_handle = None

        # Add labels, legend, and grid
        ax.set_xlabel(f"{self.reference_ts.name}")
        ax.set_ylabel(f"{self.target_ts.name}")
        if fit_handle is not None:
            ax.legend(handles=[all_handle,binned_handle,fit_handle])
        else:
            ax.legend()
        
        ax.grid(alpha=0.2)
        fig.tight_layout()

        if save: _fig_tools.save(fig)
        if show: 
            plt.show()
            plt.close(fig)
        return fig