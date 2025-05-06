import tkinter as tk
from tkinter import ttk
from utils.logger import logger
from ui.components.header import Header
from ui.components.weather_tab import WeatherTab
from ui.components.forecast_tab import ForecastTab
from models.user_preferences import UserPreferences
from services.weather_service import WeatherService
from config.constants import DEFAULT_WINDOW_SIZE, MIN_WINDOW_SIZE


class WeatherDashboard:
    def __init__(self, root, api_key):
        self.root = root
        self.api_key = api_key

        # Create notebook first
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(expand=True, fill="both")

        # Create tabs with notebook as parent
        self.weather_tab = WeatherTab(self.notebook)  # Important: parent is notebook

        # Add tab to notebook
        self.notebook.add(self.weather_tab, text="Current Weather")

        self.setup_window()
        self.weather_service = WeatherService(api_key)
        self.preferences = UserPreferences()

        self.setup_ui()
        self.setup_bindings()

        # Voice assistant initialization removed

    def setup_window(self):
        """Configure the main window"""
        self.root.title("Weather Dashboard")
        self.root.geometry(DEFAULT_WINDOW_SIZE)
        self.root.minsize(*MIN_WINDOW_SIZE)

        style = ttk.Style()
        style.configure("tooltip.TLabel", background="#1a1a1a", foreground="white")
        style.configure("legend.TLabel", foreground="white")

    def on_refresh(self):
        """Refresh weather data"""
        logger.info("Refreshing weather data")
        try:
            # Add logic to update weather data
            pass
        except Exception as e:
            logger.error(f"Error refreshing weather data: {e}")

    def on_theme_change(self):
        """Toggle theme between light and dark"""
        logger.info("Changing theme")
        try:
            # Add logic to change theme
            pass
        except Exception as e:
            logger.error(f"Error changing theme: {e}")

    def setup_ui(self):
        """Setup the main UI components"""
        self.main_frame = ttk.Frame(self.root)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # Create header
        self.header = Header(self.main_frame, self.on_refresh, self.on_theme_change)

        # Create notebook
        self.notebook = ttk.Notebook(self.main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True, pady=(20, 0))

        # Create tabs
        self.weather_tab = WeatherTab(self.notebook)
        self.forecast_tab = ForecastTab(self.notebook)

        self.notebook.add(self.weather_tab, text="Current Weather")
        self.notebook.add(self.forecast_tab, text="7-Day Forecast")

    def setup_bindings(self):
        """Setup event bindings"""
        self.root.bind("<Configure>", self.on_window_resize)

    def setup_voice_controls(self):
        """Setup voice control button and functionality"""
        voice_button = ttk.Button(
            self.header.control_frame,
            text="🎤",
            width=3,
            command=self.toggle_voice_listening,
        )
        voice_button.pack(side="right", padx=5)

        self.is_listening = False
        self.voice_button = voice_button

    def toggle_voice_listening(self):
        """Toggle voice command listening"""
        if self.is_listening:
            self.voice_assistant.stop_listening()
            self.voice_button.configure(text="🎤")
            self.is_listening = False
        else:
            self.voice_assistant.start_listening(self.handle_voice_command)
            self.voice_button.configure(text="🔴")
            self.is_listening = True

    def handle_voice_command(self, command):
        """Handle voice commands"""
        command_type = command.get("type")
        location = command.get("location")

        try:
            if command_type == "weather":
                if location:
                    self.city_var.set(location)
                    self.refresh_weather()
                weather_data = self.weather_service.get_current_weather(
                    self.city_var.get()
                )
                self.voice_assistant.speak_weather(weather_data)

            elif command_type == "forecast":
                if location:
                    self.city_var.set(location)
                    self.refresh_weather()
                forecast_data = self.weather_service.get_forecast(self.city_var.get())
                self.voice_assistant.speak_forecast(forecast_data)
                self.notebook.select(1)  # Switch to forecast tab

            elif command_type == "temperature":
                weather_data = self.weather_service.get_current_weather(
                    self.city_var.get()
                )
                temp = weather_data["main"]["temp"]
                self.voice_assistant.speak(
                    f"The current temperature is {temp:.1f} degrees Celsius"
                )

        except Exception as e:
            logger.error(f"Error handling voice command: {str(e)}")
            self.voice_assistant.speak("I'm sorry, I couldn't process that request")
