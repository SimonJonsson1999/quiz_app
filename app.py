import tkinter as tk
from tkinter import simpledialog, messagebox
from PIL import Image, ImageTk
from geopy.distance import geodesic

class MapApp:
    def __init__(self, root, num_teams):
        self.root = root
        self.root.title("Guess the Secret Location")
        
        # Load and display the map
        self.map_image = Image.open(r"images\sweden.jpg")
        self.map_photo = ImageTk.PhotoImage(self.map_image)
        
        self.canvas = tk.Canvas(root, width=self.map_photo.width(), height=self.map_photo.height())
        self.canvas.pack()
        self.canvas.create_image(0, 0, anchor=tk.NW, image=self.map_photo)
        
        self.secret_location = (37.7749, -122.4194)  # Replace with your secret location's coordinates (Example: San Francisco)
        
        self.num_teams = num_teams
        self.guesses = {team: None for team in range(1, num_teams + 1)}
        self.current_team = 1

        # Create a draggable pin
        self.pin_radius = 5
        self.pin = self.canvas.create_oval(50, 50, 50 + self.pin_radius * 2, 50 + self.pin_radius * 2, fill='red')
        
        self.canvas.tag_bind(self.pin, "<B1-Motion>", self.move_pin)
        
        # Confirm button
        self.confirm_button = tk.Button(root, text="Confirm Guess", command=self.confirm_guess)
        self.confirm_button.pack()
    
    def move_pin(self, event):
        x, y = event.x, event.y
        self.canvas.coords(self.pin, x - self.pin_radius, y - self.pin_radius, x + self.pin_radius, y + self.pin_radius)
    
    def confirm_guess(self):
        pin_coords = self.canvas.coords(self.pin)
        x = (pin_coords[0] + pin_coords[2]) / 2
        y = (pin_coords[1] + pin_coords[3]) / 2
        
        latitude, longitude = self.convert_to_latlon(x, y)
        self.guesses[self.current_team] = (latitude, longitude)
        
        # Move to next team
        if None in self.guesses.values():
            self.current_team = self.current_team % self.num_teams + 1
            messagebox.showinfo("Next Team", f"Team {self.current_team}'s turn to guess.")
        else:
            self.check_guesses()
    
    def convert_to_latlon(self, x, y):
        # Latitude and longitude bounds of the map image
        lat_min, lat_max = 34.0, 42.0  # Replace with actual latitude range of your map
        lon_min, lon_max = -125.0, -116.0  # Replace with actual longitude range of your map
        
        img_width, img_height = self.map_image.size
        latitude = lat_max - (y / img_height) * (lat_max - lat_min)
        longitude = lon_min + (x / img_width) * (lon_max - lon_min)
        
        return latitude, longitude
    
    def latlon_to_canvas(self, latitude, longitude):
        # Latitude and longitude bounds of the map image
        lat_min, lat_max = 34.0, 42.0  # Replace with actual latitude range of your map
        lon_min, lon_max = -125.0, -116.0  # Replace with actual longitude range of your map
        
        img_width, img_height = self.map_image.size
        x = (longitude - lon_min) / (lon_max - lon_min) * img_width
        y = (lat_max - latitude) / (lat_max - lat_min) * img_height
        
        return x, y
    
    def check_guesses(self):
        closest_distance = float('inf')
        closest_team = None
        
        for team, guess in self.guesses.items():
            if guess is not None:
                guess_distance = geodesic(guess, self.secret_location).km
                if guess_distance < closest_distance:
                    closest_distance = guess_distance
                    closest_team = team
        
        self.show_results(closest_team, closest_distance)
    
    def show_results(self, closest_team, closest_distance):
        # Reveal secret location
        secret_x, secret_y = self.latlon_to_canvas(*self.secret_location)
        self.canvas.create_oval(secret_x - self.pin_radius, secret_y - self.pin_radius, secret_x + self.pin_radius, secret_y + self.pin_radius, fill='blue')
        
        # Show all guesses
        for team, guess in self.guesses.items():
            guess_x, guess_y = self.latlon_to_canvas(*guess)
            self.canvas.create_oval(guess_x - self.pin_radius, guess_y - self.pin_radius, guess_x + self.pin_radius, guess_y + self.pin_radius, fill='green')
            self.canvas.create_text(guess_x, guess_y - 10, text=f'Team {team}', fill='white')
        
        messagebox.showinfo("Results", f"The closest guess is by Team {closest_team}, which is {closest_distance:.2f} km away from the secret location.")
        messagebox.showinfo("Secret Location", f"The secret location was at latitude {self.secret_location[0]} and longitude {self.secret_location[1]}.")

def start_app():
    root = tk.Tk()
    root.withdraw()  # Hide the main window initially
    
    num_teams = simpledialog.askinteger("Input", "Enter the number of teams:", minvalue=1, maxvalue=10)
    
    if num_teams:
        root.deiconify()  # Show the main window
        app = MapApp(root, num_teams)
        root.mainloop()

if __name__ == "__main__":
    start_app()
