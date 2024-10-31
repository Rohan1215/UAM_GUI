import tkinter as tk
from tkinter import ttk
import folium
import imgkit
import webbrowser
import os
import math
from PIL import Image, ImageTk, ImageDraw
import random
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time


class VertiportReservationGUI:
    def __init__(self, root, file_id):
        self.root = root
        self.root.title("Interactive Vertiport Reservation System")
        self.map_html_file = "maps/"+file_id+".html"
        self.map_png_file = "maps/"+file_id+".png"
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

    def add_marker(self, lat, lon):
        """Add a marker at the specified lat/lon and update the map."""
        if len(self.vertiports) < 5:
            self.vertiports.append((lat, lon))  # Add the selected vertiport
            self.generate_map()  # Regenerate the map with new markers

    def save(self):
        self.map.save(self.map_html_file)
        #webbrowser.open(f"file://{os.path.abspath(self.map_html_file)}")
        #imgkit.from_file(self.map_html_file,self.map_png_file)
        print("SAVED HTML")
        options = webdriver.ChromeOptions()
        options.headless = True  # Run in headless mode (no GUI)
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
        print("LOADING HTML FILE")
        # Load the HTML file
        driver.get("file://" + "/Users/rohan/Desktop/Research/airspacealloc/UAM_GUI/"+ self.map_html_file)  # Update this path to your map.html location

        # Wait for a few seconds to ensure the map is fully loaded
        time.sleep(5)  # Adjust the sleep time if needed
        print("BEFORE SAVING PNG")

        # Take a screenshot and save it
        driver.save_screenshot(self.map_png_file)

        print("AFTER SAVING PNG")

        # Clean up
        driver.quit()
        self.root.destroy()


        
    def draw_lines(self):
        """Draw lines between the selected vertiports."""
        for i in range(len(self.vertiports)):
            for j in range(i + 1, len(self.vertiports)):
                loc1 = self.vertiports[i]
                loc2 = self.vertiports[j]
                folium.PolyLine([loc1, loc2], color="blue", weight=5).add_to(self.map)


class DragAndDrawApp:
    def __init__(self, root, bg_file):
        self.root = root
        self.root.title("Airspace Allocation Interface")

        # Load an image (in PNG or GIF format)
        self.background_image = Image.open(bg_file)

        print(self.background_image.size)
        

        W, H = self.background_image.size
        scaledown = 900/max(W,H)

        self.background_image = self.background_image.resize((math.floor(W * scaledown), math.floor(H * scaledown)))

        W, H = self.background_image.size

        rows = 60
        cols = 60

        self.cell_sizeX = W//cols
        self.cell_sizeY = H//rows

        W = self.cell_sizeX * cols
        H = self.cell_sizeY * rows

        self.background_image = self.background_image.resize((W, H))  # Resize as needed

        self.placing_vertiports = True 
        self.drawing_regions = False 
        self.done = False

        self.method = ""
        self.discretization = 15
        self.horizon = 30
        self.period = 5
        
        self.canvas = tk.Canvas(self.root, bg="white", width = W, height=H)
        self.canvas.pack(side = tk.LEFT, fill="both", expand=True)

        self.overlay_image = Image.new("RGBA", (W, H), (255, 255, 255, 0))
        self.draw_overlay = ImageDraw.Draw(self.overlay_image)

        

        self.bgAverage(self.overlay_image)
        #blended_bg = Image.blend(self.background_image, self.overlay_image)
        #self.tk_blended_bg = ImageTk.PhotoImage(blended_bg)

        #self.tk_overlay_image = ImageTk.PhotoImage(self.overlay_image)
        #self.bg_photo = ImageTk.PhotoImage(self.background_image)

        self.canvas_image = self.canvas.create_image(0, 0, anchor=tk.NW, image=self.tk_blended_bg)

        # Add the image to the canvas
        #self.canvas.create_image(0, 0, image=self.bg_photo, anchor = 'nw') 

       
        self.grid = {}
        for row in range(rows):
            for col in range(cols):
                x1 = col * self.cell_sizeX
                y1 = row * self.cell_sizeY
                x2 = x1 + self.cell_sizeX
                y2 = y1 + self.cell_sizeY
                cell = self.canvas.create_rectangle(x1, y1, x2, y2, fill="", outline="black")
                self.grid[(row, col)] = cell

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
        #self.canvas.bind("<Button-1>", self.paint_cell)  # Left-click to paint
        #self.canvas.bind("<B1-Motion>", self.paint_cell)  # Dragging with left button

        frame = tk.Frame()
        frame.pack(side = tk.RIGHT, padx=10, pady=10)

        self.inputInstructions = tk.Label(frame, text="Place Vertiports", font=('Arial', 12))
        self.inputInstructions.grid(row=0, column=0, columnspan= 2, padx=5, pady=5, sticky='ew')

        self.button_edit_region = tk.Button(frame, text="Confirm Vertiports", command = self.button_click)
        self.button_edit_region.grid(row=1, column = 0, columnspan= 2, padx=5, pady=(5, 200), sticky='ew')


        # Method Dropdown
        selected_method = tk.StringVar()
        selected_method.set("Ascending Auction")  # Set the default option

        label2 = tk.Label(frame, text="Select Method:")
        label2.grid(row = 2, column = 0, padx = 5, pady = 15)
        self.method_dropdown = tk.OptionMenu(frame, selected_method, *["Ascending Auction", "Fisher", "VCG", "FF"], command=self.on_select_method)
        self.method_dropdown.grid(row = 2, column = 1, padx = 5, pady = 15)


        # Discretization Dropdown
        selected_discretization = tk.StringVar()
        selected_discretization.set("15s")  # Set the default option

        label3 = tk.Label(frame, text="Select Discretization (seconds):")
        label3.grid(row = 3, column = 0, padx = 5, pady = 15)
        self.discretization_dropdown = tk.OptionMenu(frame, selected_discretization, *["15s","30s","60s","90s"], command=self.on_select_discretization)
        self.discretization_dropdown.grid(row = 3, column = 1, padx = 5, pady = 15)


        # Horizon Dropdown
        selected_horizon = tk.StringVar()
        selected_horizon.set("30 min")  # Set the default option

        label4 = tk.Label(frame, text="Select Horizon (minutes):")
        label4.grid(row = 4, column = 0, padx = 5, pady = 5)
        self.horizon_dropdown = tk.OptionMenu(frame, selected_horizon, *["15 min", "30 min", "60 min", "90 min", "120 min"], command=self.on_select_horizon)
        self.horizon_dropdown.grid(row = 4, column = 1, padx = 5, pady = 15)


        # Horizon Dropdown
        selected_period = tk.StringVar()
        selected_period.set("5 min")  # Set the default option

        label5 = tk.Label(frame, text="Select Period (minutes):")
        label5.grid(row = 5, column = 0, padx = 5, pady = 15)
        self.period_dropdown = tk.OptionMenu(frame, selected_period, *["1 min", "2 min", "5 min", "10 min"], command=self.on_select_period)
        self.period_dropdown.grid(row = 5, column = 1, padx = 5, pady = 15)
        


        
    def on_select_discretization(self, value):
        self.discretization = value
    def on_select_horizon(self, value):
        self.horizon = value
    def on_select_period(self, value):
        self.period = value
    def on_select_method(self, value):
        self.method = value
    

    def button_click(self):
        if(self.placing_vertiports):
            print("Done placing vertiports")
            self.placing_vertiports = False 
            self.drawing_regions = True 
            
            self.inputInstructions.config(text="Identify Regions")
            self.button_edit_region.config(text = "Confirm Regions")

            self.canvas.unbind("<Button-1>")
            self.canvas.bind("<Button-1>", self.on_button_press)
            self.canvas.bind("<B1-Motion>", self.on_move_press)
            self.canvas.bind("<ButtonRelease-1>", self.on_button_release)

        elif(self.drawing_regions):
            print("Done drawing regions")
            self.drawing_regions = False 
            self.done = True 
            self.inputInstructions.config(text="Finalize Case")
            self.button_edit_region.config(text = "Submit")

            self.canvas.unbind("<Button-1>")
            self.canvas.unbind("<B1-Motion>")
            self.canvas.unbind("<ButtonRelease-1>")
        elif(self.done):
            print("Method: ", self.method)
            print("Discretization: ", self.discretization)
            print("Horizon: ", self.horizon)
            print("Period: ", self.period)




    def on_button_press(self, event):
        # Save the initial coordinates when the mouse is clicked
        self.rect_start_x = event.x
        self.rect_start_y = event.y

        self.start_x = event.x // self.cell_sizeX
        self.start_y = event.y // self.cell_sizeY

        # Create a new rectangle (initially with no size)
        self.rect = self.canvas.create_rectangle(event.x, event.y, event.x, event.y, outline='black', fill='', dash = (2,2))

    def place_vertiport(self, event):
        # Save the initial coordinates when the mouse is clicked

        self.vertiports += [[event.x, event.y]]
        print(self.vertiports[-1])

        # Create a new rectangle (initially with no size)
        self.rect = self.canvas.create_rectangle(event.x - 5, event.y - 5, event.x + 5, event.y + 5, outline='blue', fill='blue')

    def on_move_press(self, event):
        # Update the rectangle size as the mouse is dragged
        cur_x, cur_y = (event.x, event.y)
        self.canvas.coords(self.rect, self.rect_start_x, self.rect_start_y, cur_x, cur_y)

    def on_button_release(self, event):
        end_x = event.x // self.cell_sizeX
        end_y = event.y // self.cell_sizeY

        if(self.rect):
            self.canvas.delete(self.rect)

        print("TOPL: ", self.start_x, self.start_y, "BOTR: ", end_x, end_y)
        
        self.fill_cells(self.start_x, self. start_y, end_x, end_y)

        self.bgAverage(self.overlay_image)
        #self.tk_overlay_image = ImageTk.PhotoImage(self.overlay_image)
        
        self.canvas.itemconfig(self.canvas_image, image=self.tk_blended_bg)

    def bgAverage(self, overlay):
        print(self.background_image.size)
        print(overlay.size)
        self.background_image = self.background_image.convert("RGBA")
        overlay = overlay.convert("RGBA")
        blended_bg = Image.blend(self.background_image, overlay, 0.3)
        self.tk_blended_bg = ImageTk.PhotoImage(blended_bg)


    def fill_cells(self, start_x, start_y, end_x, end_y):
        # Ensure the rectangle is properly ordered (swap if dragging in reverse)
        x1, x2 = sorted([start_x, end_x])
        y1, y2 = sorted([start_y, end_y])

        # Define a translucent color (with alpha transparency)
        color = (random.randint(0,255), random.randint(0,255), random.randint(0, 255), 220)  # semi-transparent blue


        # Fill the grid cells within the selected area
        for row in range(y1, y2 + 1):
            for col in range(x1, x2 + 1):
                # Calculate the pixel coordinates for each cell
                x1_pixel = col * self.cell_sizeX
                y1_pixel = row * self.cell_sizeY
                x2_pixel = x1_pixel + self.cell_sizeX
                y2_pixel = y1_pixel + self.cell_sizeY

                # Draw the rectangle on the overlay image with translucent color
                self.draw_overlay.rectangle([x1_pixel, y1_pixel, x2_pixel, y2_pixel], fill=color)
                #self.draw_overlay.rectangle([x1_pixel, y1_pixel, x2_pixel, y2_pixel], outline = 'black', width = 2)
    
   



    

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
    app.save()

# Main application
if __name__ == "__main__":
    root = tk.Tk()
    case_id = "bayarea2"
    app = VertiportReservationGUI(root, case_id)

    # Simulate user selecting points (since real-time click handling isn't possible in `folium` with Tkinter)
    simulate_clicks(app)
    """
    self.map.save(self.map_html_file)
    #webbrowser.open(f"file://{os.path.abspath(self.map_html_file)}")
    #imgkit.from_file(self.map_html_file,self.map_png_file)
    print("SAVED HTML")
    options = webdriver.ChromeOptions()
    options.headless = True  # Run in headless mode (no GUI)
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    print("LOADING HTML FILE")
    # Load the HTML file
    driver.get("file://" + "/Users/rohan/Desktop/Research/airspacealloc/UAM_GUI/"+ self.map_html_file)  # Update this path to your map.html location

    # Wait for a few seconds to ensure the map is fully loaded
    time.sleep(5)  # Adjust the sleep time if needed
    print("BEFORE SAVING PNG")

    # Take a screenshot and save it
    driver.save_screenshot(self.map_png_file)

    print("AFTER SAVING PNG")

    # Clean up
    driver.quit()
    """
    root = tk.Tk()
    app = DragAndDrawApp(root, "maps/" + case_id + ".png")
    root.mainloop()


    #root.mainloop()
