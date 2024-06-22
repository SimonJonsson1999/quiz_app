import tkinter as tk
from tkinter import simpledialog, messagebox
from PIL import Image, ImageTk
from geopy.distance import geodesic

class MapApp:
    def __init__(self, root, num_teams, maps, secret_locations, new_size, developer_mode=False):
        self.root = root
        self.root.title("Guess the Secret Location")
        
        self.maps = maps
        self.secret_locations = secret_locations
        self.current_map_index = 0

        # Load and resize the map
        self.original_map_image = Image.open(self.maps[self.current_map_index])
        self.map_image = self.original_map_image.resize(new_size, Image.Resampling.LANCZOS)
        self.map_photo = ImageTk.PhotoImage(self.map_image)
        
        self.canvas = tk.Canvas(root, width=self.map_photo.width(), height=self.map_photo.height())
        self.canvas.pack()
        self.canvas.create_image(0, 0, anchor=tk.NW, image=self.map_photo)
        
        self.secret_location = self.secret_locations[self.current_map_index]
        
        self.num_teams = num_teams
        self.guesses = {team: None for team in range(1, num_teams + 1)}
        self.current_team = 1

        self.developer_mode = developer_mode
        if self.developer_mode:
            self.canvas.bind("<Button-1>", self.print_coordinates)

        self.team_colors = ['red', 'green', 'blue', 'orange','purple','magenta', 'yellow',  'cyan',  'brown', 'pink']
        self.pin_color = self.team_colors[0]

        # Create a draggable pin
        self.pin_radius = 5
        self.pin = self.canvas.create_oval(50, 50, 50 + self.pin_radius * 2, 50 + self.pin_radius * 2, fill=self.pin_color)

        # Add a Label widget for displaying the current team's turn
        self.turn_label = tk.Label(root, text=f"Team {self.current_team}'s turn", bg=self.pin_color, fg='white', font=('Helvetica', 12, 'bold'))
        self.turn_label.pack()

        self.result_text = tk.Text(root, height=10, width=80)
        self.result_text.pack()
        
        self.canvas.tag_bind(self.pin, "<B1-Motion>", self.move_pin)

        # Next Map button
        self.next_map_button = tk.Button(root, text="Next Map", command=self.load_next_map)
        self.next_map_button.place(x=850, y=50)
        
        # Confirm button
        self.confirm_button = tk.Button(root, text="Confirm Guess", command=self.confirm_guess)
        self.confirm_button.pack()
    
    def print_coordinates(self, event):
        x, y = event.x, event.y
        print(f"Clicked at x: {x}, y: {y}")

    def move_pin(self, event):
        x, y = event.x, event.y
        self.canvas.coords(self.pin, x - self.pin_radius, y - self.pin_radius, x + self.pin_radius, y + self.pin_radius)
    
    def confirm_guess(self):
        pin_coords = self.canvas.coords(self.pin)
        x = (pin_coords[0] + pin_coords[2]) / 2
        y = (pin_coords[1] + pin_coords[3]) / 2
        
        self.guesses[self.current_team] = (x, y)
        
        # Move to next team
        if None in self.guesses.values():
            self.current_team = self.current_team % self.num_teams + 1
            self.pin_color = self.team_colors[self.current_team - 1]
            self.canvas.itemconfig(self.pin, fill=self.pin_color)
            self.canvas.coords(self.pin, 50, 50, 50 + self.pin_radius * 2, 50 + self.pin_radius * 2)
            self.turn_label.config(text=f"Team {self.current_team}'s turn", bg=self.pin_color)
            # messagebox.showinfo("Next Team", f"Team {self.current_team}'s turn to guess.")
        else:
            self.check_guesses()

    def load_next_map(self):
        self.current_map_index = (self.current_map_index + 1) % len(self.maps)
        self.original_map_image = Image.open(self.maps[self.current_map_index])
        self.map_image = self.original_map_image.resize((800, 600), Image.Resampling.LANCZOS)
        self.map_photo = ImageTk.PhotoImage(self.map_image)
        
        # Clear the canvas
        self.canvas.delete("all")
        self.canvas.create_image(0, 0, anchor=tk.NW, image=self.map_photo)
        
        # Update the secret location for the new map
        self.secret_location = self.secret_locations[self.current_map_index]
        
        # Reset pin position and guesses
        self.guesses = {team: None for team in range(1, self.num_teams + 1)}
        self.current_team = 1
        self.pin_color = self.team_colors[self.current_team - 1]
        self.pin = self.canvas.create_oval(50, 50, 50 + self.pin_radius * 2, 50 + self.pin_radius * 2, fill=self.pin_color)
        self.canvas.tag_bind(self.pin, "<B1-Motion>", self.move_pin)
        self.result_label.config(text="")
        self.turn_label.config(text=f"Team {self.current_team}'s turn", bg=self.pin_color)
        # messagebox.showinfo("Next Map", "Loaded the next map.")
            
    def calculate_distance(self, guess, target):
        return ((guess[0] - target[0]) ** 2 + (guess[1] - target[1]) ** 2) ** 0.5
    
    def check_guesses(self):
        distances = []

        for team, guess in self.guesses.items():
            if guess is not None:
                guess_distance = self.calculate_distance(guess, self.secret_location)
                distances.append((team, guess_distance))

        distances.sort(key=lambda x: x[1])
        self.show_results(distances)
    
    def show_results(self, distances):
        # Clear the turn label
        self.turn_label.config(text="", bg=self.root.cget('bg'))

        # Reveal secret location
        secret_x, secret_y = self.secret_location
        self.canvas.create_oval(secret_x - self.pin_radius, secret_y - self.pin_radius, secret_x + self.pin_radius, secret_y + self.pin_radius, fill='black')
        self.canvas.create_text(secret_x, secret_y - 10, text='Goal', fill='black')

        # Show all guesses
        for team, guess in self.guesses.items():
            guess_x, guess_y = guess
            team_color = self.team_colors[team - 1]
            self.canvas.create_oval(guess_x - self.pin_radius, guess_y - self.pin_radius, guess_x + self.pin_radius, guess_y + self.pin_radius, fill=team_color)
            self.canvas.create_text(guess_x, guess_y - 10, text=f'Team {team}', fill='black')

        self.result_text.config(state=tk.NORMAL)
        self.result_text.delete('1.0', tk.END)

        # self.result_text.insert(tk.END, f"The closest guess is by Team {distances[0][0]}, which is {distances[0][1]:.2f} units away from the secret location.\n")
        # self.result_text.insert(tk.END, f"The secret location was at x = {self.secret_location[0]} and y = {self.secret_location[1]}.\n\nTeam Distances:\n")

        for i, (team, distance) in enumerate(distances):
            self.result_text.insert(tk.END, f"{i+1}: ", f'black')
            self.result_text.insert(tk.END, f"Team {team}: ", f'team_color_{team}')
            self.result_text.insert(tk.END, f"{distance:.2f} units away\n")

        for team in self.guesses.keys():
            self.result_text.tag_config(f'team_color_{team}', foreground=self.team_colors[team - 1])

        self.result_text.config(state=tk.DISABLED)


def start_app():
    root = tk.Tk()
    root.withdraw()  # Hide the main window initially
    
    num_teams = simpledialog.askinteger("Input", "Enter the number of teams:", minvalue=1, maxvalue=10)
    
    if num_teams:
        maps = [
            r"images\sweden1.jpg",
            r"images\sweden.jpg",
        ]
        secret_locations = [
            (340, 480),  # Secret location for first map
            (200, 300),  # Secret location for second map
        ]
        new_size = (1000, 750)  # Set the new size for the map image
        developer_mode = False
        
        root.deiconify()  # Show the main window
        app = MapApp(root, num_teams, maps,secret_locations, new_size, developer_mode)
        root.mainloop()

if __name__ == "__main__":
    start_app()
