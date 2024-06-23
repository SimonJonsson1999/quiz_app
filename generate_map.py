import geopandas as gpd
import matplotlib.pyplot as plt
from geopy.geocoders import Nominatim

# Load Sweden shapefile from SimpleMaps
shapefile_path = r"se_shp\se.shp"  # Update this path to your local directory
sweden = gpd.read_file(shapefile_path)

# List of cities including Degerfors and Linköping
cities = ["Degerfors", "Linköping"]

# Initialize geolocator
geolocator = Nominatim(user_agent="sweden_map")

# Function to get city coordinates
def get_city_coordinates(city):
    location = geolocator.geocode(city + ", Sweden")
    return (location.latitude, location.longitude)

# Get coordinates for each city
city_coords = {city: get_city_coordinates(city) for city in cities}


# Create a GeoDataFrame for the cities
city_gdf = gpd.GeoDataFrame(
    city_coords.items(), 
    columns=['City', 'Coordinates'], 
    geometry=gpd.points_from_xy([coord[1] for coord in city_coords.values()], [coord[0] for coord in city_coords.values()])
)

def get_pixel_coords(ax, geo_x, geo_y, save_dpi):
    # Convert geographical coordinates (longitude, latitude) to display coordinates
    display_coords = ax.transData.transform((geo_x, geo_y))
    
    # Display coordinates are in points (1 point = 1/72 inches). 
    # To convert to pixels, multiply by the save_dpi and divide by 72 (points per inch).
    pixel_coords = (display_coords[0] * save_dpi / 72, display_coords[1] * save_dpi / 72)
    return pixel_coords

def plot_map_with_cities():
    fig, ax = plt.subplots(figsize=(10, 8))  # Set the figure size
    sweden.plot(ax=ax, color='white', edgecolor='black')  # Plot the Sweden map
    
    # Plotting the cities with red markers for visibility
    city_gdf.plot(ax=ax, marker='o', color='red', markersize=2, alpha=1.0)
    
    # Remove axis to clean up the plot
    ax.axis('off')
    
    dpi = 300  # Set a high DPI for better accuracy in image saving
    plt.savefig("images/sweden_cities.png", dpi=dpi, bbox_inches='tight', pad_inches=0)

    plt.show()

# Plotting the map without cities and saving it
def plot_map_without_cities():
    fig, ax = plt.subplots(figsize=(10, 8))  # Larger size for better quality
    sweden.plot(ax=ax, color='white', edgecolor='black')
    
    # Remove axis
    ax.axis('off')
    city_gdf.plot(ax=ax, color='red', alpha=0.0)
    
    # Save the figure with high DPI
    dpi = 300
    plt.savefig("images/sweden.png", dpi=dpi, bbox_inches='tight', pad_inches=0)  # High DPI for high quality

    plt.show()

# Plot and save maps
plot_map_with_cities()
plot_map_without_cities()


from PIL import Image
import numpy as np

# Load the image
image_path = r"images\sweden_cities.png"
image = Image.open(image_path)
image_data = np.array(image)

image_data_rgb = image_data[:, :, :3]

# Define the red color range
red_min = np.array([250, 0, 0], dtype="uint8")
red_max = np.array([255, 100, 100], dtype="uint8")

# Find red dots
red_points = np.where(np.all(image_data_rgb >= red_min, axis=-1) & np.all(image_data_rgb <= red_max, axis=-1))

# Get coordinates of red dots
red_coordinates = list(zip(red_points[1], red_points[0]))  # Swap x and y
# print("Red dot coordinates:", red_coordinates)
red_coordinates = np.array(red_coordinates)
from sklearn.cluster import DBSCAN

dbscan = DBSCAN(eps=10, min_samples=5)
clusters = dbscan.fit_predict(red_coordinates)

# Extract cluster centers
unique_clusters = set(clusters)
cluster_centers = []
for cluster in unique_clusters:
    if cluster != -1: 
        points_in_cluster = red_coordinates[clusters == cluster]
        center = points_in_cluster.mean(axis=0)
        cluster_centers.append((int(center[0]), int(center[1])))

print("Cluster centers:", cluster_centers)
