import tkinter as tk
from ui.app import WeatherDashboard
from utils.logger import logger


def main():
    try:
        logger.info("Starting Weather Dashboard application")
        with open("api_key.txt", "rt") as f:
            api_key = f.read().strip()

        root = tk.Tk()
        app = WeatherDashboard(root, api_key)
        root.mainloop()
    except Exception as e:
        logger.critical(f"Critical error in main loop: {str(e)}")
        raise


if __name__ == "__main__":
    main()
