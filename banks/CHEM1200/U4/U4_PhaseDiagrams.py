import matplotlib.pyplot as plt
import numpy as np

# Create a figure
plt.figure(figsize=(6, 4))

# Generate a concave up curve for the liquid-gas boundary
T = np.linspace(-0.5, 1, 400)  # Temperature, arbitrary units
P = T**2  # Pressure, arbitrary units, creating a simple concave up curve

plt.plot(T, P, label="Liquid-Gas Boundary")

# Line bending back for the critical point and supercritical region
T_critical = [1, 1.2]  # Extend beyond the critical point, arbitrary units
P_critical = [1, 0.8]  # Bending back, arbitrary units

plt.plot(T_critical, P_critical, label="Critical Point and Beyond")

# Customize the plot
plt.title('Qualitative Water Phase Diagram')
plt.xlabel('Temperature')
plt.ylabel('Pressure')
plt.legend()
plt.grid(True)

# Remove numbers from axes
plt.xticks([])
plt.yticks([])

plt.show()
