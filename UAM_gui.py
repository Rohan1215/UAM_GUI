import tkinter as tk
import folium
import webbrowser
import os
from PIL import Image, ImageTk

class VertiportReservationGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Interactive Vertiport Reservation System")
        self.map_file = "interactive_map_with_network.html"
        self.vertiports = []  # List to store vertiport coordinates

        # Create a button to generate the map
        self.generate_map_button = tk.Button(root, text="Generate Interactive Map", command=self.generate_map)
        self.generate_map_button.pack(pady=10)

    def generate_map(self):
        """Generate an interactive map for selecting vertiports."""
        # Initialize the Folium map centered at San Francisco
        self.map = folium.Map(location=[37.7749, -122.4194], zoom_start=12, control_scale=True, zoom_control=True)

        # Add pre-existing markers (if any) and lines between them
        for lat, lon in self.vertiports:
            folium.Marker([lat, lon], popup=f"Vertiport at {lat}, {lon}").add_to(self.map)
        
        # If 5 vertiports have been selected, draw lines between them
        if len(self.vertiports) == 5:
            self.draw_lines()

        # Save the map and display it in a browser
        self.map.save(self.map_file)
        webbrowser.open(f"file://{os.path.abspath(self.map_file)}")

    def add_marker(self, lat, lon):
        """Add a marker at the specified lat/lon and update the map."""
        if len(self.vertiports) < 5:
            self.vertiports.append((lat, lon))  # Add the selected vertiport
            self.generate_map()  # Regenerate the map with new markers
        
    def draw_lines(self):
        """Draw lines between the selected vertiports."""
        for i in range(len(self.vertiports)):
            for j in range(i + 1, len(self.vertiports)):
                loc1 = self.vertiports[i]
                loc2 = self.vertiports[j]
                folium.PolyLine([loc1, loc2], color="blue", weight=5).add_to(self.map)


class DragAndDrawApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Drag and Draw Rectangles")
        
        self.canvas = tk.Canvas(self.root, bg="white", width=1100, height=735)
        self.canvas.pack(fill="both", expand=True)


        # Load an image (in PNG or GIF format)
        self.background_image = Image.open("maps/bayarea.png")
        self.background_image = self.background_image.resize((1100, 735))  # Resize as needed
        self.bg_photo = ImageTk.PhotoImage(self.background_image)

        # Add the image to the canvas
        self.canvas.create_image(0, 0, image=self.bg_photo, anchor = 'nw') 

        # Variables to track the initial click and current rectangle
        self.start_x = None
        self.start_y = None
        self.rect = None
        self.vertiports = []

        # Bind mouse events
        self.canvas.bind("<Button-1>", self.place_vertiport)
        #self.canvas.bind("<Button-1>", self.on_button_press)
        #self.canvas.bind("<B1-Motion>", self.on_move_press)
        #self.canvas.bind("<ButtonRelease-1>", self.on_button_release)

    def on_button_press(self, event):
        # Save the initial coordinates when the mouse is clicked
        self.start_x = event.x
        self.start_y = event.y

        # Create a new rectangle (initially with no size)
        self.rect = self.canvas.create_rectangle(self.start_x, self.start_y, self.start_x, self.start_y, outline='black', fill='')

    def place_vertiport(self, event):
        # Save the initial coordinates when the mouse is clicked
        self.start_x = event.x
        self.start_y = event.y

        self.vertiports += [[self.start_x, self.start_y]]
        print(self.vertiports)

        # Create a new rectangle (initially with no size)
        self.rect = self.canvas.create_rectangle(self.start_x - 5, self.start_y - 5, self.start_x + 5, self.start_y + 5, outline='blue', fill='blue')

    def on_move_press(self, event):
        # Update the rectangle size as the mouse is dragged
        cur_x, cur_y = (event.x, event.y)
        self.canvas.coords(self.rect, self.start_x, self.start_y, cur_x, cur_y)

    def on_button_release(self, event):
        # Finalize the rectangle creation
        pass

# Create the main window and run the application

# Mock function to simulate user input for lat/lon (since `folium` can't do live dynamic input in Tkinter)
def simulate_clicks(app):
    """Simulate user clicks to add vertiports at selected coordinates."""
    # These would be replaced by actual clicks/input from the user
    clicks = [
        (37.7749, -122.4194),  # San Francisco
        (37.8044, -122.2711),  # Oakland
        (37.6879, -122.4702),  # Daly City
        (37.6391, -122.4158),  # South San Francisco
        (37.8048, -122.4105)   # Emeryville
    ]

    for lat, lon in clicks:
        app.add_marker(lat, lon)

# Main application
if __name__ == "__main__":
    root = tk.Tk()
    #app = VertiportReservationGUI(root)

    # Simulate user selecting points (since real-time click handling isn't possible in `folium` with Tkinter)
    #simulate_clicks(app)

    #root = tk.Tk()
    app = DragAndDrawApp(root)
    root.mainloop()


    #root.mainloop()
