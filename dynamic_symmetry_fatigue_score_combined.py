# -*- coding: utf-8 -*-
"""dynamic symmetry/fatigue score combined

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1gELQriynXj8VD4u-i1TorUhrpI0qYSH_
"""

from scipy.interpolate import Rbf
import matplotlib
matplotlib.use('Agg')  # Use a non-GUI backend
import matplotlib.pyplot as plt

import os
import numpy as np
import pandas as pd
from matplotlib.path import Path
from scipy.interpolate import splprep, splev
import git
import shutil
import time

# Load the Excel file (ensure it's uploaded to the Colab environment)
filename = "Copy of test_lab shortening.xlsx"  # Ensure this path is correct

# Read the data from the Excel file
data = pd.read_excel(filename)

# Extract timestamps and relevant pressure values
timestamps = data["Time"].values
sensor_pressures = [data[f"Sensor_{i+1}"].values for i in range(22)]

# Sensor coordinates
sensor_coords = np.array([
    [5.8,2.2],[7.0,4.9],[4.8,6.2],[6.4,9.6],[4.5,12.4],[2.8,15.1],[6.8,15.0],[4.9,16.9],[6.5,18.9],[2.2,19.2],[4.6,21.4],
    [-5.8,2.2],[-7.0,4.9],[-4.8,6.2],[-6.4,9.6],[-4.5,12.4],[-2.8,15.1],[-6.8,15.0],[-4.9,16.9],[-6.5,18.9],[-2.2,19.2],[-4.6,21.4]
])

# Foot outline
foot_outline = np.array([
    [6,0.4],[3.6,2.2],[3.7,7],[3,10.8],[1.2,15.7],[1.3,19.8],[4,23.6],[7,22],[8.5,19.2],[9.2,15.2],[9,11.5],[8.5,6.6],[8.4,2.3],[7.9,0.9],[6,0.4]
])

# Generate a smooth Bézier curve
tck, u = splprep(foot_outline.T, s=2)
u_fine = np.linspace(0, 1, 300)
smooth_foot_outline = np.array(splev(u_fine, tck)).T
left_foot_outline = smooth_foot_outline.copy()
left_foot_outline[:, 0] *= -1

# Grid setup
min_x, max_x = np.min(left_foot_outline[:, 0]), np.max(smooth_foot_outline[:, 0])
min_y, max_y = np.min(smooth_foot_outline[:, 1]), np.max(smooth_foot_outline[:, 1])
X, Y = np.meshgrid(np.linspace(min_x, max_x, 120), np.linspace(min_y, max_y, 300))

def create_foot_path(smooth_x, smooth_y):
    return Path(np.column_stack([smooth_x, smooth_y]))

r_foot_path = create_foot_path(smooth_foot_outline[:, 0], smooth_foot_outline[:, 1])
l_foot_path = create_foot_path(left_foot_outline[:, 0], left_foot_outline[:, 1])

# Compute pressure mapping
avg_sensor_pressures = np.mean(sensor_pressures, axis=1)
rbf = Rbf(sensor_coords[:, 0], sensor_coords[:, 1], avg_sensor_pressures, function='multiquadric')
pressure_data_grid = rbf(X, Y)

# Mask points inside foot outlines
points = np.column_stack([X.flatten(), Y.flatten()])
inside_right = r_foot_path.contains_points(points).reshape(X.shape)
inside_left = l_foot_path.contains_points(points).reshape(X.shape)
combined_pressure_data = np.where(inside_right | inside_left, pressure_data_grid, np.nan)

# Normalize pressure data
min_pressure, max_pressure = np.nanmin(combined_pressure_data), np.nanmax(combined_pressure_data)
normalized_pressure_data = (combined_pressure_data - min_pressure) / (max_pressure - min_pressure)

# Plotting
fig, ax = plt.subplots(figsize=(12, 8))
pressure_img = ax.imshow(normalized_pressure_data, extent=[min_x, max_x, min_y, max_y], origin='lower', cmap="YlOrRd", vmin=0, vmax=1)
ax.plot(smooth_foot_outline[:, 0], smooth_foot_outline[:, 1], color="red", lw=2, label="Right Foot")
ax.plot(left_foot_outline[:, 0], left_foot_outline[:, 1], color="blue", lw=2, label="Left Foot")
ax.scatter(sensor_coords[:, 0], sensor_coords[:, 1], color="black", s=100)
ax.scatter(0, 0, color="green", s=150, marker="x", label="Origin")
ax.set_xlim([min_x, max_x])
ax.set_ylim([min_y, max_y])
ax.set_xlabel("X (cm)")
ax.set_ylabel("Y (cm)")
ax.set_title("Average Foot Pressure Mapping")
ax.legend()
cbar = fig.colorbar(pressure_img, ax=ax)
cbar.set_label('Pressure Value (Normalized from 0 to 1)', rotation=270, labelpad=20)


output_file = "dynamic_symmetry_score_visualization.png"

plt.savefig(output_file, bbox_inches='tight')
plt.show()

# Wait until file is actually saved
time.sleep(2)

if not os.path.exists(output_file):
    raise FileNotFoundError(f"File {output_file} was not created successfully.")

print("File saved successfully!")


import os
import shutil
import time
import git

# Directory and file settings
repo_dir = "srdesign"  # Assuming this is your repo folder
repo_root = os.getcwd()  # Assuming current working directory is the root where the script runs
output_file = "dynamic_symmetry_score_visualization.png"  # The generated image file
photo_file_in_repo = os.path.join(repo_root, repo_dir, output_file)  # Correct path inside the repo
repo_url = "https://github.com/jakewang21/srdesign.git"

# GitHub PAT from an environment variable
pat = os.getenv('EK_TOKEN')  # Ensure your PAT is set as an environment variable
if not pat:
    raise ValueError("EK_TOKEN is not set in the environment.")

# Clone the repo if it doesn't exist locally
if not os.path.isdir(repo_dir):
    repo = git.Repo.clone_from(repo_url, repo_dir)
else:
    repo = git.Repo(repo_dir)
    repo.git.config("pull.rebase", "false")
    repo.git.pull()

# Ensure the output file exists before proceeding
# The file should be inside the repository folder
if not os.path.exists(photo_file_in_repo):
    raise FileNotFoundError(f"Output file '{output_file}' not found in the expected location: {os.path.abspath(photo_file_in_repo)}")

# Force Git to recognize the file as changed by updating its timestamp
os.utime(photo_file_in_repo, (time.time(), time.time()))

# Set the remote URL with the PAT
remote_url = f"https://{pat}@github.com/jakewang21/srdesign.git"
repo.git.remote("set-url", "origin", remote_url)

# Configure git user settings
repo.git.config("user.name", "eugeniakritsuk")
repo.git.config("user.email", "eugeniakritsuk@gmail.com")

# Check the git status to ensure the file is detected as new or modified
print("Git status output:")
repo.git.status()

# Add the file to Git (force add in case the file is being ignored)
repo.git.add(photo_file_in_repo)

# Check if the file is staged for commit
print("Git status after adding:")
repo.git.status()

# Commit the change
repo.git.commit("-m", "Update photo")

# Push to the GitHub repository
repo.git.push(verbose=True)

print("Photo uploaded to GitHub successfully!")




from scipy.interpolate import Rbf

import os
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')  # Use a non-GUI backend
import matplotlib.pyplot as plt
from matplotlib.path import Path
from scipy.interpolate import griddata, splprep, splev

filename = "Copy of test_lab shortening.xlsx"  # Ensure this path is correct

# Read the data from the Excel file
data = pd.read_excel(filename)

# Extract timestamps and relevant pressure values
timestamps = data["Time"].values  # Extract the "Time" column

# Sensor pressure values (22 sensors)
sensor_pressures = [data[f"Sensor_{i+1}"].values for i in range(22)]

# Sensor coordinates (x, y) for 22 sensors
sensor_coords = np.array([
    [5.8,2.2],[7.0,4.9],[4.8,6.2],[6.4,9.6],[4.5,12.4],[2.8,15.1],[6.8,15.0],[4.9,16.9],[6.5,18.9],[2.2,19.2],[4.6,21.4],
    [-5.8,2.2],[-7.0,4.9],[-4.8,6.2],[-6.4,9.6],[-4.5,12.4],[-2.8,15.1],[-6.8,15.0],[-4.9,16.9],[-6.5,18.9],[-2.2,19.2],[-4.6,21.4] # Mirrored for left foot
])

# Sample coordinates of foot outline (x, y)
foot_outline = np.array([
    [6,0.4],[3.6,2.2],[3.7,7],[3,10.8],[1.2,15.7],[1.3,19.8],[4,23.6],[7,22],[8.5,19.2],[9.2,15.2],[9,11.5],[8.5,6.6],[8.4,2.3],[7.9,0.9],[6,0.4]  # Close the loop
])

# Generate a smooth Bézier curve for the foot outline
tck, u = splprep(foot_outline.T, s=2)
u_fine = np.linspace(0, 1, 300)
smooth_foot_outline = np.array(splev(u_fine, tck)).T

# Create a mirrored outline for the left foot
left_foot_outline = np.copy(smooth_foot_outline)
left_foot_outline[:, 0] *= -1  # Flip x-coordinates for the left foot

# Create the grid for pressure mapping based on the bounding box of both feet
min_x = min(np.min(smooth_foot_outline[:, 0]), np.min(left_foot_outline[:, 0]))
max_x = max(np.max(smooth_foot_outline[:, 0]), np.max(left_foot_outline[:, 0]))
min_y = np.min(smooth_foot_outline[:, 1])
max_y = np.max(smooth_foot_outline[:, 1])

x_grid = np.linspace(min_x, max_x, 120)
y_grid = np.linspace(min_y, max_y, 300)
X, Y = np.meshgrid(x_grid, y_grid)

def create_foot_path(smooth_x, smooth_y):
    smooth_foot_outline = np.column_stack([smooth_x, smooth_y])
    return Path(smooth_foot_outline)

# Paths for masking
r_foot_path = create_foot_path(smooth_foot_outline[:, 0], smooth_foot_outline[:, 1])
l_foot_path = create_foot_path(left_foot_outline[:, 0], left_foot_outline[:, 1])

# Calculate indices to split the data into thirds
num_timestamps = len(timestamps)
first_third_end = num_timestamps // 3
second_third_end = 2 * num_timestamps // 3

# Split the data into three parts based on timestamps
first_third_pressures = [sensor_pressure[:first_third_end] for sensor_pressure in sensor_pressures]
second_third_pressures = [sensor_pressure[first_third_end:second_third_end] for sensor_pressure in sensor_pressures]
third_third_pressures = [sensor_pressure[second_third_end:] for sensor_pressure in sensor_pressures]

# Calculate average pressures for each third
avg_first_third = np.mean(first_third_pressures, axis=1)
avg_second_third = np.mean(second_third_pressures, axis=1)
avg_third_third = np.mean(third_third_pressures, axis=1)

from scipy.interpolate import Rbf

# RBF Interpolation for each third
rbf_first_third = Rbf(sensor_coords[:, 0], sensor_coords[:, 1], avg_first_third, function='multiquadric')
rbf_second_third = Rbf(sensor_coords[:, 0], sensor_coords[:, 1], avg_second_third, function='multiquadric')
rbf_third_third = Rbf(sensor_coords[:, 0], sensor_coords[:, 1], avg_third_third, function='multiquadric')

# Interpolate the pressure values over the grid for each third
first_third_pressure_grid = rbf_first_third(X, Y)
second_third_pressure_grid = rbf_second_third(X, Y)
third_third_pressure_grid = rbf_third_third(X, Y)

# Apply foot mask for each section
first_third_combined_pressure_data = np.where(inside_right | inside_left, first_third_pressure_grid, np.nan)
second_third_combined_pressure_data = np.where(inside_right | inside_left, second_third_pressure_grid, np.nan)
third_third_combined_pressure_data = np.where(inside_right | inside_left, third_third_pressure_grid, np.nan)

# Normalize the pressure data for each section
min_first_third = np.nanmin(first_third_combined_pressure_data)
max_first_third = np.nanmax(first_third_combined_pressure_data)
normalized_first_third = (first_third_combined_pressure_data - min_first_third) / (max_first_third - min_first_third)

min_second_third = np.nanmin(second_third_combined_pressure_data)
max_second_third = np.nanmax(second_third_combined_pressure_data)
normalized_second_third = (second_third_combined_pressure_data - min_second_third) / (max_second_third - min_second_third)

min_third_third = np.nanmin(third_third_combined_pressure_data)
max_third_third = np.nanmax(third_third_combined_pressure_data)
normalized_third_third = (third_third_combined_pressure_data - min_third_third) / (max_third_third - min_third_third)

# Helper function to create and save the heatmap images for each third
def create_heatmap_image(normalized_pressure_data, title, output_file):
    fig, ax = plt.subplots(figsize=(12, 8))
    pressure_img = ax.imshow(normalized_pressure_data, extent=[min_x, max_x, min_y, max_y], origin='lower', cmap="YlOrRd", vmin=0, vmax=1)

    # Plot the smooth foot outlines
    ax.plot(smooth_foot_outline[:, 0], smooth_foot_outline[:, 1], color="red", lw=2, label="Right Foot")
    ax.plot(left_foot_outline[:, 0], left_foot_outline[:, 1], color="blue", lw=2, label="Left Foot")

    # Plot sensor locations
    ax.scatter(sensor_coords[:, 0], sensor_coords[:, 1], color="black", s=100, zorder=5)

    # Label the sensors with their respective numbers
    for i, (x, y) in enumerate(sensor_coords):
        ax.text(x + 0.5, y + 0.5, f"{i+1}", fontsize=10, color="black", zorder=6)

    # Mark the origin
    ax.scatter(0, 0, color="green", s=150, marker="x", label="Origin")

    ax.set_xlim([min_x, max_x])
    ax.set_ylim([min_y, max_y])
    ax.set_xlabel("X (cm)")
    ax.set_ylabel("Y (cm)")
    ax.set_title(title)
    ax.legend()

    # Add colorbar
    cbar = fig.colorbar(pressure_img, ax=ax)
    cbar.set_label('Pressure Value (Normalized from 0 to 1)', rotation=270, labelpad=20)

    # Save the image
    plt.savefig(output_file, bbox_inches='tight')
    plt.close()

# Generate and save the heatmaps for each third
create_heatmap_image(normalized_first_third, "Dynamic First Third of the Run (0-33%)", "dynamic_first_third_pressure_map.png")
create_heatmap_image(normalized_second_third, "Dynamic Second Third of the Run (33-66%)", "dynamic_second_third_pressure_map.png")
create_heatmap_image(normalized_third_third, "Dynamic Third Third of the Run (66-100%)", "dynamic_third_third_pressure_map.png")


import git
import shutil
import os

# Define the repository directory
repo_dir = "srdesign"

# Define the list of PNG files to be uploaded
photo_files = [
    "dynamic_first_third_pressure_map.png",
    "dynamic_second_third_pressure_map.png",
    "dynamic_third_third_pressure_map.png"
]

# Corresponding file names in the repo
photo_files_in_repo = [
    os.path.join(repo_dir, "dynamic_first_third_pressure_map.png"),
    os.path.join(repo_dir, "dynamic_second_third_pressure_map.png"),
    os.path.join(repo_dir, "dynamic_third_third_pressure_map.png")
]

# GitHub repository details
repo_url = "https://github.com/jakewang21/srdesign.git"
pat = "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"  # Replace with your actual PAT

# Clone the repo if not already present (or pull latest changes)
if not os.path.isdir(repo_dir):
    repo = git.Repo.clone_from(repo_url, repo_dir)
else:
    repo = git.Repo(repo_dir)
    repo.git.config("pull.rebase", "false")
    repo.git.pull()

# Set up remote URL with PAT for authentication
remote_url = f"https://{pat}@github.com/jakewang21/srdesign.git"
repo.git.remote("set-url", "origin", remote_url)

# Set username and email for the commit
repo.git.config("user.name", "eugeniakritsuk")  # Replace with your GitHub username
repo.git.config("user.email", "eugeniakritsuk@gmail.com")  # Replace with your GitHub email

# Loop through and upload each PNG file
for src, dest in zip(photo_files, photo_files_in_repo):
    if os.path.exists(src):
        shutil.copy(src, dest)
        repo.git.add(os.path.abspath(dest))
    else:
        print(f"File not found: {src}")

# Commit the changes with a message
repo.git.commit("-m", "Update multiple PNG files")

# Push the changes to GitHub
repo.git.push()

print("All photos uploaded to GitHub successfully!")
