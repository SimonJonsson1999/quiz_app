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

# Print the coordinates for Degerfors and Linköping
degerfors_coords = city_coords['Degerfors']
linkoping_coords = city_coords['Linköping']
print(f"Degerfors coordinates: {degerfors_coords}")
print(f"Linköping coordinates: {linkoping_coords}")

# Create a GeoDataFrame for the cities
city_gdf = gpd.GeoDataFrame(
    city_coords.items(), 
    columns=['City', 'Coordinates'], 
    geometry=gpd.points_from_xy([coord[1] for coord in city_coords.values()], [coord[0] for coord in city_coords.values()])
)

# Function to calculate pixel coordinates in the saved image
def get_pixel_coords(ax, geo_x, geo_y, fig_dpi):
    display_coords = ax.transData.transform((geo_x, geo_y))
    pixel_coords = display_coords * fig_dpi / ax.figure.dpi
    return pixel_coords

# Plotting the map with cities and saving it
def plot_map_with_cities():
    fig, ax = plt.subplots(figsize=(10, 8))  # Larger size for better quality
    sweden.plot(ax=ax, color='white', edgecolor='black')
    
    # Plotting the cities
    city_gdf.plot(ax=ax, color='red', alpha=1.0)
    
    # Remove axis
    ax.axis('off')
    
    # Save the figure with high DPI
    dpi = 600
    plt.savefig("images/sweden_cities.png", dpi=dpi, bbox_inches='tight', pad_inches=0)  # High DPI for high quality

    # Calculate and print pixel coordinates for each city in the saved image
    for city, row in city_gdf.iterrows():
        geo_x, geo_y = row['geometry'].x, row['geometry'].y
        pixel_x, pixel_y = get_pixel_coords(ax, geo_x, geo_y, dpi)
        print(f"{row['City']} pixel coordinates in saved image: ({pixel_x:.2f}, {pixel_y:.2f})")

    plt.show()

# Plotting the map without cities and saving it
def plot_map_without_cities():
    fig, ax = plt.subplots(figsize=(10, 8))  # Larger size for better quality
    sweden.plot(ax=ax, color='white', edgecolor='black')
    
    # Remove axis
    ax.axis('off')
    city_gdf.plot(ax=ax, color='red', alpha=0.0)
    
    # Save the figure with high DPI
    dpi = 600
    plt.savefig("images/sweden.png", dpi=dpi, bbox_inches='tight', pad_inches=0)  # High DPI for high quality

    plt.show()

# Plot and save maps
plot_map_with_cities()
plot_map_without_cities()
