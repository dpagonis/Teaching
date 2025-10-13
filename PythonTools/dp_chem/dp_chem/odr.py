import numpy as np
import matplotlib.pyplot as plt
import os

class odr:
    def __init__(self, x=None, y=None):
        """
        Initialize the OrthogonalRegression object with optional datasets.
        """
        if x is not None and y is not None:
            unfiltered_x = np.array(x)
            unfiltered_y = np.array(y)
            valid_mask = ~np.isnan(unfiltered_x) & ~np.isnan(unfiltered_y)
            self.x = x[valid_mask]
            self.y = y[valid_mask]
            self.slope = None
            self.intercept = None
            self._compute_regression() #sets values of self.slope and self.intercept
            
            x_min_data = np.min(self.x.data)
            x_max_data = np.max(self.x.data)
            y_min = np.min(self.y.data)
            y_max = np.max(self.y.data)
            trendline_x_full = np.linspace(x_min_data, x_max_data, 500)  # 500 points for smoothness
            trendline_y_full = self.predict(trendline_x_full)
            valid_indices = (trendline_y_full >= y_min) & (trendline_y_full <= y_max)
            self.trendline_x = trendline_x_full[valid_indices]
            self.trendline_y = trendline_y_full[valid_indices]
        else:
            self.x = None
            self.y = None
            self.slope = None
            self.intercept = None

    def _compute_regression(self):
        """
        Private method to calculate the slope and intercept using orthogonal regression.
        """
        x_mean = np.mean(self.x)
        y_mean = np.mean(self.y)

        # Center the data
        x_centered = self.x - x_mean
        y_centered = self.y - y_mean

        # Singular value decomposition (SVD)
        data_matrix = np.vstack((x_centered, y_centered)).T
        u, s, vh = np.linalg.svd(data_matrix, full_matrices=False)

        # Compute slope (s = -vx / vy for orthogonal regression)
        vx, vy = vh.T[:, 0]
        self.slope = vy / vx

        # Compute intercept
        self.intercept = y_mean - self.slope * x_mean

    def predict(self, x_values):
        """
        Predict y values for a given set of x values.
        """
        x_values = np.array(x_values)
        return self.slope * x_values + self.intercept


    def plot_regression(self):
        """
        Plot the original data points and the regression line.
        """
        if self.x is None or self.y is None:
            print("No data to plot. Please load data first.")
            return

        # Scatter plot of original data
        plt.scatter(self.x, self.y, color='blue')

        # Regression line
        y_pred = self.predict(self.x)
        plt.plot(self.x, y_pred, color='red', label=f'Regression Line\n(slope={self.slope:.2f}, intercept={self.intercept:.2f})')

        # Labels and legend
        #plt.xlabel("X")
        #plt.ylabel("Y")
        plt.legend(loc='best')
        plt.title("Orthogonal Regression")
        plt.grid(False)

        # Display the plot
        plt.show()

    def save_plot_file_():
        file_content = "Plot.png"
        directory = ""
        file_name = "Plot.png"
        # Ensure the directory exists
        if not os.path.exists(directory):
            os.makedirs(directory)
        # Combine directory and filename to form the full path
        file_path = os.path.join(directory,file_name)
        # Write the content to the file
        with open(file_path, "w") as file:
            file.write(file_content)

        print(f"File has been saved to {file_path}")
        