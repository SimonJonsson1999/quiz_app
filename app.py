import tkinter as tk
from tkinter import simpledialog, messagebox, ttk
from PIL import Image, ImageTk
from geopy.distance import geodesic

class MapApp:
    def __init__(self, root, num_teams, maps, secret_locations, questions):
        self.root = root
        self.root.title("Guess the Secret Location")
        self.root.attributes('-fullscreen', True)  # Start in fullscreen mode

        # Bind Esc key to the toggle_fullscreen function
        self.root.bind('<Escape>', self.toggle_fullscreen)

        self.maps = maps
        self.secret_locations = secret_locations
        self.questions = questions
        self.current_map_index = 0

        # Setup initial map image (will resize in self.configure_window)
        self.original_map_image = Image.open(self.maps[self.current_map_index])
        self.map_image = self.original_map_image.resize((800, 600), Image.Resampling.LANCZOS)
        self.map_photo = ImageTk.PhotoImage(self.map_image)

        # Canvas for displaying the map
        self.canvas = tk.Canvas(root)
        self.canvas.grid(row=1, column=0, columnspan=3, sticky='nsew')
        self.image_on_canvas = self.canvas.create_image(0, 0, anchor=tk.NW, image=self.map_photo)

        
        self.secret_location = self.secret_locations[self.current_map_index]
        self.question = self.questions[self.current_map_index]
        self.num_teams = num_teams
        self.guesses = {team: None for team in range(1, num_teams + 1)}
        self.score = {team: 0 for team in range(1, num_teams + 1)}
        self.current_team = 1


        self.team_colors = ['red', 'green', 'blue', 'orange', 'purple', 'magenta', 'yellow', 'cyan', 'brown', 'pink']
        self.pin_color = self.team_colors[0]

        # Create a draggable pin
        self.pin_radius = 5
        self.pin = self.canvas.create_oval(50, 50, 50 + self.pin_radius * 2, 50 + self.pin_radius * 2, fill=self.pin_color)

        # Label widget for displaying the current team's turn
        self.turn_label = tk.Label(root, text=f"Team {self.current_team}'s turn", bg=self.pin_color, fg='white', font=('Helvetica', 12, 'bold'))
        self.turn_label.grid(row=2, column=0, columnspan=3, sticky='', pady=(10, 0))
        
        self.question_label = tk.Label(root, text=f"{self.question}", bg="black", fg='white', font=('Helvetica', 12, 'bold'))
        self.question_label.grid(row=0, column=0, columnspan=3, sticky='', pady=(10, 0))

        # Text widget for results
        self.result_label = tk.Label(root, text="", bg='white', fg='black', font=('Helvetica', 12), anchor='w', justify='left')
        self.result_label.grid(row=3, column=2, columnspan=3, sticky='', pady=10)
        
        # Text widget for score
        self.score_label = tk.Label(root, text="", bg='white', fg='black', font=('Helvetica', 24), anchor='w', justify='left')
        self.score_label.grid(row=1, column=1, columnspan=2, sticky='', pady=10)
        
        self.canvas.tag_bind(self.pin, "<B1-Motion>", self.move_pin)

        # Create a style for ttk buttons
        style = ttk.Style()
        style.configure('Large.TButton', font=('Helvetica', 24), padding=10)

        # Buttons for controlling the application
        self.next_map_button = ttk.Button(root, text="Next Map", command=self.load_next_map, style='Large.TButton')
        self.next_map_button.grid(row=3, column=1, sticky='', padx=10, pady=10)
        
        self.confirm_button = ttk.Button(root, text="Confirm Guess", command=self.confirm_guess, style='Large.TButton')
        self.confirm_button.grid(row=3, column=0, sticky='', padx=10)
        
        self.confirm_button = ttk.Button(root, text="Show Result", command=self.check_guesses, style='Large.TButton')
        self.confirm_button.grid(row=4, column=0, sticky='', padx=10)

        # Configure the grid to scale with the window resizing
        self.root.grid_rowconfigure(1, weight=1)
        self.root.grid_columnconfigure(0, weight=1)

        # Ensure the canvas and text areas expand properly
        self.root.grid_columnconfigure(1, weight=1)

    

    def move_pin(self, event):
        x, y = event.x, event.y
        self.canvas.coords(self.pin, x - self.pin_radius, y - self.pin_radius, x + self.pin_radius, y + self.pin_radius)
        
    def toggle_fullscreen(self, event=None):
        self.root.attributes('-fullscreen', False)
    
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
        else:
            self.canvas.itemconfig(self.pin, state='hidden')
            self.turn_label.config(text="", bg='white')

    def load_next_map(self):    
        self.current_map_index = (self.current_map_index + 1) % len(self.maps)
        self.original_map_image = Image.open(self.maps[self.current_map_index])
        self.map_image = self.original_map_image.resize((800, 600), Image.Resampling.LANCZOS)
        self.map_photo = ImageTk.PhotoImage(self.map_image)
        
        # Clear the canvas and reset elements
        self.canvas.delete("all")
        self.image_on_canvas = self.canvas.create_image(0, 0, anchor=tk.NW, image=self.map_photo)
        
        self.secret_location = self.secret_locations[self.current_map_index]
        self.question = self.questions[self.current_map_index]
        self.question_label.config(text=self.question)
        
        # Reset pin position and guesses
        self.guesses = {team: None for team in range(1, self.num_teams + 1)}
        self.current_team = 1
        self.pin_color = self.team_colors[self.current_team - 1]
        self.pin = self.canvas.create_oval(50, 50, 50 + self.pin_radius * 2, 50 + self.pin_radius * 2, fill=self.pin_color)
        self.canvas.tag_bind(self.pin, "<B1-Motion>", self.move_pin)
        self.result_label.config(text="")
        self.turn_label.config(text=f"Team {self.current_team}'s turn", bg=self.pin_color)
            
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
        # Clear the turn label and set up results display
        self.turn_label.config(text="", bg=self.root.cget('bg'))
        
        # Reveal secret location
        secret_x, secret_y = self.secret_location
        self.canvas.create_oval(secret_x - self.pin_radius, secret_y - self.pin_radius, secret_x + self.pin_radius, secret_y + self.pin_radius, fill='black')
        self.canvas.create_text(secret_x, secret_y - 10, text='Goal', fill='black')

        # Show all guesses
        results_text = ""
        for team, guess in self.guesses.items():
            guess_x, guess_y = guess
            team_color = self.team_colors[team - 1]
            self.canvas.create_oval(guess_x - self.pin_radius, guess_y - self.pin_radius, guess_x + self.pin_radius, guess_y + self.pin_radius, fill=team_color)
            self.canvas.create_text(guess_x, guess_y - 10, text=f'Team {team}', fill='black')
            distance = next((dist[1] for dist in distances if dist[0] == team), None)
            results_text += f"Team {team}: {distance:.2f} units away\n"

        self.result_label.config(text=results_text.strip())
        for i, (team, distance) in enumerate(distances):
            self.score[team] += i + 1
            
        score_text = "Scoreboard:\n"
        sorted_scores = sorted(self.score.items(), key=lambda item: item[1])
        for team, score in sorted_scores:
            score_text += f"Team {team}: {score} points\n"
        self.score_label.config(text=score_text.strip())
        
        
        
        


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
        questions = [
            "Where is Linköping?",
            "Where is Degerfors?",
        ]
        new_size = (1000, 750)  # Set the new size for the map image
        
        root.deiconify()  # Show the main window
        app = MapApp(root, num_teams, maps,secret_locations,questions)
        root.mainloop()

if __name__ == "__main__":
    start_app()
