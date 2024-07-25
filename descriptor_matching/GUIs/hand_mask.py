import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageTk, ImageDraw
import numpy as np

class ImageMaskingApp:
    def __init__(self, root):
        """
        Initializes the ImageMaskingApp with the given root window.

        Parameters:
            root (tk.Tk): The root window to initialize the application.

        Returns:
            None
        """
        self.root = root
        self.root.title("Image Masking App")

        self.canvas = tk.Canvas(root, cursor="cross")
        self.canvas.pack(fill=tk.BOTH, expand=True)

        self.load_button = tk.Button(root, text="Load Image", command=self.load_image)
        self.load_button.pack(side=tk.LEFT)

        self.save_button = tk.Button(root, text="Save Mask", command=self.save_mask, state=tk.DISABLED)
        self.save_button.pack(side=tk.RIGHT)

        self.image = None
        self.tk_image = None
        self.draw = None
        self.mask = None
        self.polygon_vertices = []
        self.polygon_drawn = False

        self.canvas.bind("<Button-1>", self.on_button_press)
        self.canvas.bind("<Button-3>", self.on_right_button_press)
        self.canvas.bind("<Motion>", self.on_mouse_move)

    def load_image(self):
        """
        Load an image from a file dialog and display it on the canvas.

        This function opens a file dialog to select an image file. If a file is selected, it opens the image file using the PIL library and converts it to RGB mode. It then creates a PhotoImage object from the image and displays it on the canvas.

        Additionally, it creates a new black and white mask image with the same size as the loaded image and initializes a draw object for the mask image. Finally, it enables the save button on the GUI.

        Parameters:
            self (ImageMaskingApp): The instance of the ImageMaskingApp class.

        Returns:
            None
        """
        file_path = filedialog.askopenfilename(filetypes=[("Image files", "*.jpg *.jpeg *.png")])
        if file_path:
            self.image = Image.open(file_path).convert("RGB")
            self.tk_image = ImageTk.PhotoImage(self.image)
            self.canvas.create_image(0, 0, anchor=tk.NW, image=self.tk_image)

            self.mask = Image.new("L", self.image.size, 0)
            self.draw = ImageDraw.Draw(self.mask)

            self.save_button.config(state=tk.NORMAL)

    def on_button_press(self, event):
        """
        Adds a new point to the polygon vertices list when the left mouse button is pressed.
        If there are at least two points in the vertices list, draws a line between the last two points on the canvas.
        
        Parameters:
            event (tkinter.Event): The event object representing the mouse button press.
        
        Returns:
            None
        """
        self.polygon_vertices.append((event.x, event.y))
        if len(self.polygon_vertices) > 1:
            self.canvas.create_line(self.polygon_vertices[-2], self.polygon_vertices[-1], fill="red", width=2)

    def on_right_button_press(self, event):
        """
        Checks the number of polygon vertices and creates a line and polygon based on the vertices if more than 2 are present.
        """
        if len(self.polygon_vertices) > 2:
            self.canvas.create_line(self.polygon_vertices[-1], self.polygon_vertices[0], fill="red", width=2)
            self.draw.polygon(self.polygon_vertices, fill=255)
            self.polygon_vertices = []

    def on_mouse_move(self, event):
        """
        Handle the mouse move event.

        Parameters:
            event (Event): The mouse move event object.

        Returns:
            None

        This function is called when the mouse is moved over the canvas. It checks if there are any vertices in the polygon_vertices list. If there are, it deletes the temporary line on the canvas and creates a new line from the last vertex to the current mouse position. The new line is drawn in red with a width of 2 and is tagged as "temp_line" for easy deletion later.
        """
        if self.polygon_vertices:
            self.canvas.delete("temp_line")
            self.canvas.create_line(self.polygon_vertices[-1], (event.x, event.y), fill="red", width=2, tags="temp_line")

    def save_mask(self):
        """
        Saves the mask image to a file.

        This function checks if the mask image exists. If it does, it opens a file dialog to prompt the user to select a save location and file name. The selected file path is then used to save the mask image.

        Parameters:
            self (object): The instance of the class.

        Returns:
            None
        """
        if self.mask:
            save_path = filedialog.asksaveasfilename(defaultextension=".png", filetypes=[("PNG files", "*.png")])
            if save_path:
                self.mask.save(save_path)

if __name__ == "__main__":
    root = tk.Tk()
    app = ImageMaskingApp(root)
    root.mainloop()
