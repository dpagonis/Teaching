import matplotlib.pyplot as plt
import numpy as np
import hashlib
import os
import logging



def create_nucleus_with_legend(protons, neutrons):
    # Define the size of the figure and the circles
    fig, ax = plt.subplots()
    circle_radius = 0.1  # Circle radius
    
    # Function to place a circle and add it to the plot
    def place_circle(x, y, is_proton, label=None):
        color = 'darkgrey' if is_proton else 'white'
        circle = plt.Circle((x, y), circle_radius, color=color, ec='black', label=label)
        ax.add_patch(circle)
    
    # Initialize counters for placed protons and neutrons
    placed_protons = 0
    placed_neutrons = 0
    
    # Function to create a ring of circles
    def create_ring(center_x, center_y, ring_radius, num_particles, start_with_proton):
        nonlocal placed_protons, placed_neutrons  # Access the outer scope variables
        # Calculate angle step for placing particles in the ring
        angle_step = 2 * np.pi / num_particles
        for i in range(num_particles):
            angle = i * angle_step
            x = center_x + ring_radius * np.cos(angle)
            y = center_y + ring_radius * np.sin(angle)
            
            # Determine if the current particle is a proton or neutron
            if start_with_proton and placed_protons < protons:
                label = 'Proton' if placed_protons == 0 else None  # Label only the first proton
                place_circle(x, y, True, label)
                placed_protons += 1
            elif not start_with_proton and placed_neutrons < neutrons:
                label = 'Neutron' if placed_neutrons == 0 else None  # Label only the first neutron
                place_circle(x, y, False, label)
                placed_neutrons += 1
            
            # Alternate between placing a proton and neutron
            start_with_proton = not start_with_proton
        
        return placed_protons, placed_neutrons

    # Place the first ring with one particle, which will be the center particle
    if protons > 0:
        place_circle(0, 0, True, label='Proton')
        placed_protons += 1
    elif neutrons > 0:
        place_circle(0, 0, False, label='Neutron')  # Place the first neutron at the center if no protons
        placed_neutrons += 1

    # Determine the number of particles in the second ring and place them
    ring_number = 1
    num_particles = 6  # Start with 6 particles for the second ring
    ring_radius = 2 * circle_radius
    while placed_protons < protons or placed_neutrons < neutrons:
        placed_protons, placed_neutrons = create_ring(0, 0, ring_radius, num_particles, placed_protons % 2 == 0)
        ring_radius += 2 * circle_radius  # Increase the ring radius for each new ring
        num_particles += 6  # Increase the number of particles for each new ring

    # Set the axis limits and aspect ratio
    ax.set_xlim(-ring_radius, ring_radius)
    ax.set_ylim(-ring_radius, ring_radius)
    ax.set_aspect('equal')
    plt.axis('off')

    # Add a legend to the plot
    handles, labels = ax.get_legend_handles_labels()
    ax.legend(handles=handles, labels=labels, loc='upper right', frameon=False)

    # Hash the filename
    hash_name = hashlib.sha256(f'{protons}_{neutrons}'.encode()).hexdigest()

    output_dir = 'png'
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)  # Create the directory if it does not exist
    
    output_path = f'{output_dir}/{hash_name}.png'
    
    if not os.path.exists(output_path):  # Check if the file exists
        try:
            plt.savefig(output_path, dpi=300, bbox_inches='tight', pad_inches=0)
            print(f"Image saved: {output_path}")
        except Exception as e:  # Catch any exception during save
            logging.error(f"Error saving image {output_path}: {e}")
            # Handle the error, e.g., by continuing to the next image or re-raising the exception
        finally:
            plt.close()  # Ensure the figure is closed in any case
    else:
        global counter
        counter += 1

    return output_path

counter = 0
for n_p in range(1,13):
    for n_n in range(n_p-3,n_p+3+1):
        nn_screened = max(0,n_n)
        create_nucleus_with_legend(n_p,nn_screened)
print(counter,'files not overwritten')