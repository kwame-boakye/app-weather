import tkinter as tk
from tkinter import ttk
from ui.components.weather_tab import WeatherTab


def main():
    root = tk.Tk()
    root.title("Weather Dashboard")

    # Set a minimum window size
    root.minsize(600, 400)

    # Create notebook (tabbed interface)
    notebook = ttk.Notebook(root)
    notebook.pack(expand=True, fill="both", padx=10, pady=10)

    # Add Weather Tab
    weather_tab = WeatherTab(notebook)
    notebook.add(weather_tab, text="Weather")

    root.mainloop()


if __name__ == "__main__":
    main()
