import tkinter as tk
from tkinter import ttk


class WeatherTab(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)  # This line is crucial - it initializes the Frame

        # Setup the weather tab UI components
        self.setup_ui()

    def setup_ui(self):
        # Create your weather tab widgets here
        self.weather_info = ttk.Label(self, text="Weather Information")
        self.weather_info.pack(pady=20)

        # Add more widgets as needed
