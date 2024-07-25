import tkinter as tk
from tkinter import filedialog, messagebox
import subprocess
import os

class VideoFrameExtractorApp:
    def __init__(self, root):
        """
        Initializes a new instance of the VideoFrameExtractorApp class.

        Args:
            root (tkinter.Tk): The root tkinter window.

        Returns:
            None
        """
        self.root = root
        self.root.title("Video Frame Extractor")

        self.video_path = tk.StringVar()
        self.seconds_per_frame = tk.DoubleVar(value=1.0)

        self.create_widgets()

    def create_widgets(self):
        """
        Creates widgets for selecting a video file, entering seconds per frame, and running frame extraction.
        """
        # Video file selection
        tk.Label(self.root, text="Select Video File:").grid(row=0, column=0, padx=10, pady=10, sticky=tk.W)
        tk.Entry(self.root, textvariable=self.video_path, width=50).grid(row=0, column=1, padx=10, pady=10)
        tk.Button(self.root, text="Browse", command=self.browse_video).grid(row=0, column=2, padx=10, pady=10)

        # Seconds per frame input
        tk.Label(self.root, text="Seconds Per Frame:").grid(row=1, column=0, padx=10, pady=10, sticky=tk.W)
        tk.Entry(self.root, textvariable=self.seconds_per_frame).grid(row=1, column=1, padx=10, pady=10)

        # Run button
        tk.Button(self.root, text="Extract Frames", command=self.extract_frames).grid(row=2, column=0, columnspan=3, pady=20)

    def browse_video(self):
        """
        This function allows the user to browse for a video file and sets the video path if a file is selected.
        """
        file_path = filedialog.askopenfilename()
        if file_path:
            self.video_path.set(file_path)
        else:
            print("No file selected or file path not found.")

    def extract_frames(self):
        """
        Extracts frames from a video file and saves them to a specified output directory.

        This function retrieves the video path and seconds per frame from the GUI input fields.
        It checks if the video path is valid and if the seconds per frame is a positive number.
        If either of these conditions is not met, an error message is displayed and the function returns.

        The function then creates the output directory based on the video path and saves the frames
        with a naming convention of "frame_%04d.png" in the output directory.

        The frames are extracted using the ffmpeg command-line tool with the specified input video path,
        frames per second, and output directory.

        If the extraction is successful, a success message is displayed with the output directory path.
        If an error occurs during the extraction, an error message is displayed with the error details.

        Parameters:
            None

        Returns:
            None
        """
        video_path = self.video_path.get()
        seconds_per_frame = self.seconds_per_frame.get()

        if not video_path or not os.path.exists(video_path):
            messagebox.showerror("Error", "Please select a valid video file.")
            return

        if seconds_per_frame <= 0:
            messagebox.showerror("Error", "Seconds per frame must be a positive number.")
            return

        output_dir = os.path.splitext(video_path)[0] + "_frames"
        os.makedirs(output_dir, exist_ok=True)

        command = [
            "ffmpeg",
            "-i", video_path,
            "-vf", f"fps=1/{seconds_per_frame}",
            os.path.join(output_dir, "frame_%04d.png")
        ]

        try:
            subprocess.run(command, check=True)
            messagebox.showinfo("Success", f"Frames extracted successfully to {output_dir}")
        except subprocess.CalledProcessError as e:
            messagebox.showerror("Error", f"Failed to extract frames: {e}")

if __name__ == "__main__":
    root = tk.Tk()
    app = VideoFrameExtractorApp(root)
    root.mainloop()
