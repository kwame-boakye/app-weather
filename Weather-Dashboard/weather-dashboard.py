import datetime as dt
import requests
import sys
import json
from colorama import init, Fore, Style
from difflib import get_close_matches
from functools import lru_cache
import time
from datetime import datetime
import pytz
from zoneinfo import ZoneInfo
import tkinter as tk
from tkinter import ttk, messagebox
import threading
import os
import logging
from logging.handlers import RotatingFileHandler
from datetime import timedelta
import sqlite3
from geopy.geocoders import Nominatim
from geopy.distance import geodesic


# Setup logging configuration
def setup_logging():
    """Configure logging with rotation and formatting"""
    log_directory = "logs"
    if not os.path.exists(log_directory):
        os.makedirs(log_directory)

    log_file = os.path.join(log_directory, "weather_app.log")

    # Create a rotating file handler (max 5MB per file, keep 5 backup files)
    file_handler = RotatingFileHandler(
        log_file, maxBytes=5 * 1024 * 1024, backupCount=5, encoding="utf-8"  # 5MB
    )

    # Create console handler
    console_handler = logging.StreamHandler()

    # Define log format
    log_format = logging.Formatter(
        "%(asctime)s - %(levelname)s - %(message)s", datefmt="%Y-%m-%d %H:%M:%S"
    )

    # Set format for both handlers
    file_handler.setFormatter(log_format)
    console_handler.setFormatter(log_format)

    # Get the logger
    logger = logging.getLogger("WeatherDashboard")
    logger.setLevel(logging.INFO)

    # Add handlers to logger
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger


# Initialize logger
logger = setup_logging()

# Initialize colorama
init()

# Weather emoji mappings
WEATHER_EMOJIS = {
    # Clear conditions
    "clear sky": "☀️",
    "sunny": "☀️",
    # Cloudy conditions
    "few clouds": "🌤️",
    "scattered clouds": "⛅",
    "broken clouds": "☁️",
    "overcast clouds": "☁️",
    "cloudy": "☁️",
    # Rain conditions
    "light rain": "🌦️",
    "moderate rain": "🌧️",
    "heavy rain": "🌧️",
    "shower rain": "🌧️",
    "rain": "🌧️",
    "drizzle": "🌧️",
    "light intensity drizzle": "🌧️",
    "heavy intensity drizzle": "🌧️",
    "light intensity shower rain": "🌧️",
    "heavy intensity shower rain": "🌧️",
    "very heavy rain": "🌧️",
    "extreme rain": "🌧️",
    # Thunderstorm conditions
    "thunderstorm": "⛈️",
    "light thunderstorm": "⛈️",
    "heavy thunderstorm": "⛈️",
    "thunderstorm with light rain": "⛈️",
    "thunderstorm with rain": "⛈️",
    "thunderstorm with heavy rain": "⛈️",
    # Snow conditions
    "snow": "🌨️",
    "light snow": "🌨️",
    "heavy snow": "🌨️",
    "sleet": "🌨️",
    "light shower sleet": "🌨️",
    "shower sleet": "🌨️",
    "light rain and snow": "🌨️",
    "rain and snow": "🌨️",
    # Atmospheric conditions
    "mist": "🌫️",
    "smoke": "🌫️",
    "haze": "🌫️",
    "fog": "🌫️",
    "sand": "🌫️",
    "dust": "🌫️",
    "volcanic ash": "🌫️",
    "squalls": "💨",
    "tornado": "🌪️",
    # Additional conditions
    "light intensity drizzle rain": "🌧️",
    "heavy intensity drizzle rain": "🌧️",
    "shower rain and drizzle": "🌧️",
    "heavy shower rain and drizzle": "🌧️",
    "shower drizzle": "🌧️",
}

BASE_URL = "http://api.openweathermap.org/data/2.5/weather?"
GEOCODING_URL = "http://ip-api.com/json/"  # Free geolocation API
FORECAST_URL = "http://api.openweathermap.org/data/2.5/forecast?"

try:
    Api_Key = open("api_key.txt", "rt").read().strip()
except FileNotFoundError:
    print(f"{Fore.RED}Error: api_key.txt file not found{Style.RESET_ALL}")
    sys.exit(1)
except Exception as e:
    print(f"{Fore.RED}Error reading API key: {e}{Style.RESET_ALL}")
    sys.exit(1)

# Create a session for better performance
session = requests.Session()


# Cache for storing weather data (TTL: 10 minutes)
@lru_cache(maxsize=32)
def get_cached_weather(location, timestamp):
    """Get weather data with caching. Timestamp ensures cache invalidation."""
    return fetch_weather_data(location)


def get_cache_timestamp():
    """Return current timestamp rounded to nearest 10 minutes for cache control"""
    return int(time.time() / 600) * 600


def fetch_weather_data(location):
    """Fetch weather data from API with proper error handling and logging"""
    try:
        logger.info(f"Fetching weather data for location: {location}")
        params = {"appid": Api_Key, "q": location}
        response = session.get(BASE_URL, params=params)

        if response.status_code != 200:
            logger.error(f"API request failed with status code {response.status_code}")
            logger.debug(f"API Response: {response.text}")

        if response.status_code == 401:
            logger.error("Invalid API key detected")
            raise Exception("Invalid API key. Please check your API key and try again.")
        elif response.status_code == 404:
            logger.warning(f"City not found: {location}")
            raise Exception(f"City not found: {location}")
        elif response.status_code == 429:
            logger.warning("API rate limit exceeded")
            raise Exception("API rate limit exceeded. Please try again later.")
        elif response.status_code >= 500:
            logger.error(f"Server error: {response.status_code}")
            raise Exception(
                "Weather service is currently unavailable. Please try again later."
            )

        response.raise_for_status()
        weather_data = response.json()
        logger.info("Weather data successfully retrieved")
        return weather_data

    except requests.exceptions.ConnectionError as e:
        logger.error(f"Connection error: {str(e)}")
        raise Exception(
            "Unable to connect to weather service. Please check your internet connection."
        )
    except requests.exceptions.Timeout as e:
        logger.error(f"Request timeout: {str(e)}")
        raise Exception("Request timed out. Please try again.")
    except requests.exceptions.RequestException as e:
        logger.error(f"Request error: {str(e)}")
        raise Exception(f"Error accessing weather service: {str(e)}")
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        raise


def get_user_location():
    """Get user's location using IP-based geolocation with better error handling"""
    try:
        response = session.get(GEOCODING_URL, timeout=5)
        response.raise_for_status()
        data = response.json()
        city = data.get("city")
        country = data.get("countryCode")

        if not city or not country:
            raise Exception("Could not determine location from IP address")

        return city, country

    except Exception as e:
        print(
            f"{Fore.YELLOW}Could not determine location automatically: {str(e)}{Style.RESET_ALL}"
        )
        print(f"{Fore.YELLOW}Falling back to default location...{Style.RESET_ALL}")
        return "London", "UK"


def get_user_preferences():
    """Get user's preferred city and temperature unit"""
    print(f"\n{Fore.CYAN}Weather Dashboard Settings{Style.RESET_ALL}")
    print("1. Enter city manually")
    print("2. Use current location")
    choice = (
        input(f"\n{Fore.YELLOW}Choose an option (1/2) [2]: {Style.RESET_ALL}").strip()
        or "2"
    )

    if choice == "1":
        city = input(f"{Fore.YELLOW}Enter city name: {Style.RESET_ALL}").strip()
        country_code = input(
            f"{Fore.YELLOW}Enter country code (optional, e.g., US): {Style.RESET_ALL}"
        ).strip()
        location = f"{city},{country_code}" if country_code else city
    else:
        city, country_code = get_user_location()
        location = f"{city},{country_code}"
        print(f"{Fore.GREEN}Using detected location: {location}{Style.RESET_ALL}")

    unit_choice = (
        input(f"{Fore.YELLOW}Preferred temperature unit (C/F) [C]: {Style.RESET_ALL}")
        .strip()
        .upper()
        or "C"
    )
    return location, unit_choice


def kelvin_to_preferred_unit(kelvin, unit="C"):
    """Convert Kelvin to preferred temperature unit"""
    celsius = kelvin - 273.15
    if unit == "F":
        return celsius * (9 / 5) + 32, "°F"
    return celsius, "°C"


def get_local_timezone():
    """Get the local timezone name"""
    try:
        # Try to get system timezone
        return str(datetime.now().astimezone().tzinfo)
    except:
        return "UTC"  # Fallback to UTC if local timezone can't be determined


def format_local_time(timestamp, timezone_str=None):
    """Convert UTC timestamp to local time"""
    try:
        utc_time = datetime.fromtimestamp(timestamp, tz=pytz.UTC)
        if timezone_str:
            local_tz = pytz.timezone(timezone_str)
            local_time = utc_time.astimezone(local_tz)
        else:
            local_time = utc_time.astimezone()
        return local_time.strftime("%H:%M:%S %Z")
    except:
        # Fallback to UTC if conversion fails
        return datetime.fromtimestamp(timestamp, tz=pytz.UTC).strftime("%H:%M:%S UTC")


def get_uv_index(lat, lon):
    """Fetch UV index data from OpenWeatherMap API"""
    try:
        params = {
            "appid": Api_Key,
            "lat": lat,
            "lon": lon,
            "exclude": "minutely,hourly,daily,alerts",
        }
        response = session.get(
            "https://api.openweathermap.org/data/2.5/onecall", params=params, timeout=5
        )
        response.raise_for_status()
        data = response.json()
        return data.get("current", {}).get("uvi", None)
    except:
        return None


def format_visibility(meters):
    """Convert visibility from meters to kilometers with proper formatting"""
    if meters > 1000:
        return f"{meters/1000:.1f} km"
    return f"{meters} m"


def get_wind_direction(degrees):
    """Convert wind direction degrees to cardinal direction"""
    directions = [
        "N",
        "NNE",
        "NE",
        "ENE",
        "E",
        "ESE",
        "SE",
        "SSE",
        "S",
        "SSW",
        "SW",
        "WSW",
        "W",
        "WNW",
        "NW",
        "NNW",
    ]
    index = round(degrees / (360 / len(directions))) % len(directions)
    return directions[index]


def get_weather_emoji(description):
    """Get weather emoji with logging for unknown conditions"""
    emoji = WEATHER_EMOJIS.get(description.lower())
    if emoji is None:
        logger.warning(f"Unknown weather condition: {description}")
        return "❓"
    return emoji


def display_weather(weather_data, location, temp_unit):
    """Display enhanced weather information with additional metrics"""
    description = weather_data["weather"][0]["description"]
    weather_emoji = get_weather_emoji(description)

    # Get coordinates for UV index
    lat = weather_data["coord"]["lat"]
    lon = weather_data["coord"]["lon"]
    uv_index = get_uv_index(lat, lon)

    # Get local timezone from coordinates
    timezone_str = weather_data.get("timezone", get_local_timezone())

    # Temperature calculations
    temp_kelvin = weather_data["main"]["temp"]
    feels_like_kelvin = weather_data["main"]["feels_like"]
    temp, unit = kelvin_to_preferred_unit(temp_kelvin, temp_unit)
    feels_like, _ = kelvin_to_preferred_unit(feels_like_kelvin, temp_unit)

    # Wind information
    wind_speed = weather_data["wind"]["speed"]
    wind_direction = get_wind_direction(weather_data["wind"].get("deg", 0))
    wind_gust = weather_data["wind"].get("gust")

    # Format times
    sunrise_time = format_local_time(weather_data["sys"]["sunrise"], timezone_str)
    sunset_time = format_local_time(weather_data["sys"]["sunset"], timezone_str)

    header = f"\n{Fore.CYAN}{'='*60}{Style.RESET_ALL}"

    output = (
        f"{header}\n"
        f"{Fore.YELLOW}📍 Weather in {Fore.WHITE}{location}{Style.RESET_ALL}\n"
        f"{weather_emoji} {Fore.CYAN}{description.capitalize()}{Style.RESET_ALL}\n\n"
        f"{Fore.GREEN}🌡️ Temperature:{Style.RESET_ALL}\n"
        f"   Current: {Fore.WHITE}{temp:.1f}{unit}{Style.RESET_ALL}\n"
        f"   Feels Like: {Fore.WHITE}{feels_like:.1f}{unit}{Style.RESET_ALL}\n"
        f"   Min: {Fore.WHITE}{kelvin_to_preferred_unit(weather_data['main']['temp_min'], temp_unit)[0]:.1f}{unit}{Style.RESET_ALL}\n"
        f"   Max: {Fore.WHITE}{kelvin_to_preferred_unit(weather_data['main']['temp_max'], temp_unit)[0]:.1f}{unit}{Style.RESET_ALL}\n\n"
        f"{Fore.BLUE}💨 Wind:{Style.RESET_ALL}\n"
        f"   Speed: {Fore.WHITE}{wind_speed} m/s{Style.RESET_ALL}\n"
        f"   Direction: {Fore.WHITE}{wind_direction} ({weather_data['wind'].get('deg', 0)}°){Style.RESET_ALL}"
    )

    if wind_gust:
        output += f"\n   Gusts up to: {Fore.WHITE}{wind_gust} m/s{Style.RESET_ALL}"

    output += (
        f"\n\n{Fore.BLUE}🌍 Atmospheric Conditions:{Style.RESET_ALL}\n"
        f"   Humidity: {Fore.WHITE}{weather_data['main']['humidity']}%{Style.RESET_ALL}\n"
        f"   Pressure: {Fore.WHITE}{weather_data['main']['pressure']} hPa{Style.RESET_ALL}\n"
        f"   Visibility: {Fore.WHITE}{format_visibility(weather_data.get('visibility', 0))}{Style.RESET_ALL}"
    )

    if uv_index is not None:
        output += f"\n   UV Index: {Fore.WHITE}{uv_index:.1f}{Style.RESET_ALL}"

    output += (
        f"\n\n{Fore.YELLOW}☀️ Sun Schedule:{Style.RESET_ALL}\n"
        f"   Sunrise: {Fore.WHITE}{sunrise_time}{Style.RESET_ALL}\n"
        f"   Sunset: {Fore.WHITE}{sunset_time}{Style.RESET_ALL}"
        f"{header}"
    )

    print(output)


def display_error(error_msg, suggestion=None):
    """Display formatted error message with optional suggestion"""
    print(f"\n{Fore.RED}{'='*50}{Style.RESET_ALL}")
    print(f"{Fore.RED}Error: {error_msg}{Style.RESET_ALL}")
    if suggestion:
        print(f"\n{Fore.YELLOW}Suggestion: {suggestion}{Style.RESET_ALL}")
    print(f"{Fore.RED}{'='*50}{Style.RESET_ALL}")


class UserPreferences:
    def __init__(self):
        self.db_path = "weather_preferences.db"
        self.setup_database()
        self.load_preferences()

    def setup_database(self):
        """Create database and tables if they don't exist"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS preferences (
                    key TEXT PRIMARY KEY,
                    value TEXT
                )
            """
            )
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS favorite_locations (
                    city TEXT PRIMARY KEY,
                    country TEXT,
                    lat REAL,
                    lon REAL
                )
            """
            )
            conn.commit()

    def load_preferences(self):
        """Load user preferences from database"""
        defaults = {
            "units": "metric",  # metric or imperial
            "default_city": "",
            "refresh_interval": "30",  # minutes
            "auto_detect_location": "true",
        }

        self.preferences = defaults.copy()

        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT key, value FROM preferences")
            for key, value in cursor.fetchall():
                self.preferences[key] = value

    def save_preference(self, key, value):
        """Save a single preference to database"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT OR REPLACE INTO preferences (key, value) VALUES (?, ?)",
                (key, str(value)),
            )
            conn.commit()
        self.preferences[key] = value

    def add_favorite(self, city, country, lat, lon):
        """Add a location to favorites"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                """INSERT OR REPLACE INTO favorite_locations 
                   (city, country, lat, lon) VALUES (?, ?, ?, ?)""",
                (city, country, lat, lon),
            )
            conn.commit()

    def remove_favorite(self, city):
        """Remove a location from favorites"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM favorite_locations WHERE city = ?", (city,))
            conn.commit()

    def get_favorites(self):
        """Get list of favorite locations"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT city, country FROM favorite_locations")
            return cursor.fetchall()


class WeatherDashboardGUI:
    def __init__(self, root):
        # Configure the root window with standard tkinter
        self.root = root
        self.root.title("Weather Dashboard")
        self.root.geometry("800x600")
        self.root.minsize(600, 400)

        # Configure styles
        style = ttk.Style()
        style.configure("tooltip.TLabel", background="#1a1a1a", foreground="white")
        style.configure("legend.TLabel", foreground="white")

        # Create main frame
        self.main_frame = ttk.Frame(self.root)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # Create header with search and theme toggle
        self.setup_header()

        # Create notebook for tabs
        self.notebook = ttk.Notebook(self.main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True, pady=(20, 0))

        # Create tabs using ttk
        self.current_weather_tab = ttk.Frame(self.notebook)
        self.forecast_tab = ttk.Frame(self.notebook)

        self.notebook.add(self.current_weather_tab, text="Current Weather")
        self.notebook.add(self.forecast_tab, text="7-Day Forecast")

        # Setup both tabs
        self.setup_current_weather_tab()
        self.setup_forecast_tab()

        # Initialize user preferences
        self.preferences = UserPreferences()

        # Setup menu
        self.setup_menu()

        # Setup favorites dropdown
        self.setup_favorites_dropdown()

    def setup_header(self):
        """Setup header with search bar and theme toggle"""
        # Create header frame first
        self.header_frame = ttk.Frame(self.main_frame)
        self.header_frame.pack(fill="x", pady=(0, 10))

        # Search frame with city entry and refresh button
        search_frame = ttk.Frame(self.header_frame)
        search_frame.pack(side="left", fill="x", expand=True)

        self.city_var = tk.StringVar()
        city_entry = ttk.Entry(
            search_frame,
            textvariable=self.city_var,
            width=40,
        )
        city_entry.insert(0, "Enter city name")
        city_entry.pack(side="left", padx=(0, 10))

        # Bind Enter key to refresh
        city_entry.bind("<Return>", lambda e: self.refresh_weather())

        self.refresh_btn = ttk.Button(
            search_frame,
            text="Refresh",
            command=self.refresh_weather,
            width=10,
        )
        self.refresh_btn.pack(side="left")

        # Theme toggle button
        self.theme_btn = ttk.Button(
            self.header_frame, text="🌙", command=self.toggle_theme, width=3
        )
        self.theme_btn.pack(side="right", padx=(10, 0))

    def setup_current_weather_tab(self):
        """Setup current weather display with improved layout"""
        # Main info frame
        main_info = ttk.Frame(self.current_weather_tab)
        main_info.pack(fill="x", pady=(0, 20))

        # Location and time
        self.location_label = ttk.Label(main_info, text="", font=("Helvetica", 24))
        self.location_label.pack(anchor="w")

        self.last_update_label = ttk.Label(main_info, text="")
        self.last_update_label.pack(anchor="w")

        # Current conditions frame
        conditions_frame = ttk.Frame(self.current_weather_tab)
        conditions_frame.pack(fill="both", expand=True)

        # Temperature and weather icon (left side)
        temp_frame = ttk.Frame(conditions_frame)
        temp_frame.pack(side="left", padx=(0, 20))

        self.weather_icon = ttk.Label(temp_frame, text="", font=("Segoe UI Emoji", 64))
        self.weather_icon.pack()

        self.temp_label = ttk.Label(temp_frame, text="", font=("Helvetica", 48))
        self.temp_label.pack()

        self.feels_like_label = ttk.Label(temp_frame, text="")
        self.feels_like_label.pack()

        # Details grid (right side)
        details_frame = ttk.Frame(conditions_frame)
        details_frame.pack(side="left", fill="both", expand=True, padx=10, pady=10)

        # Create grid for details
        self.detail_labels = {}
        details = [
            ("Humidity", "humidity"),
            ("Wind", "wind"),
            ("Pressure", "pressure"),
            ("Visibility", "visibility"),
            ("Sunrise", "sunrise"),
            ("Sunset", "sunset"),
        ]

        for i, (label, key) in enumerate(details):
            row = i // 2
            col = i % 2

            # Label
            ttk.Label(details_frame, text=f"{label}:").grid(
                row=row, column=col * 2, sticky="w", padx=(10, 5), pady=5
            )

            # Value
            value_label = ttk.Label(details_frame, text="")
            value_label.grid(
                row=row, column=col * 2 + 1, sticky="w", padx=(0, 10), pady=5
            )
            self.detail_labels[key] = value_label

    def toggle_theme(self):
        """Toggle between light and dark theme"""
        current_theme = getattr(self, "theme_mode", "dark")
        if current_theme == "dark":
            # Switch to light theme
            self.theme_mode = "light"
            self.theme_btn.configure(text="🌞")
            self.root.configure(bg="white")
            style = ttk.Style()
            style.configure("TFrame", background="white")
            style.configure("TLabel", background="white", foreground="black")
            style.configure("TButton", background="white")
        else:
            # Switch to dark theme
            self.theme_mode = "dark"
            self.theme_btn.configure(text="🌙")
            self.root.configure(bg="#2c2c2c")
            style = ttk.Style()
            style.configure("TFrame", background="#2c2c2c")
            style.configure("TLabel", background="#2c2c2c", foreground="white")
            style.configure("TButton", background="#2c2c2c")

    def refresh_weather(self):
        city = self.city_var.get().strip()
        if not city:
            logger.warning("Attempted refresh with empty city name")
            messagebox.showwarning("Input Error", "Please enter a city name")
            return

        logger.info(f"Refreshing weather data for city: {city}")
        self.refresh_btn.config(state="disabled")
        threading.Thread(target=self.fetch_all_weather_data, args=(city,)).start()

    def fetch_all_weather_data(self, city):
        """Fetch both current weather and forecast data"""
        try:
            weather_data = fetch_weather_data(city)
            forecast_data = fetch_forecast_data(city)

            self.root.after(0, self.update_weather_display, weather_data)
            self.root.after(0, self.update_forecast_display, forecast_data)

        except Exception as e:
            logger.error(f"Error fetching weather data: {str(e)}")
            self.root.after(0, self.show_error, str(e))
        finally:
            self.root.after(0, lambda: self.refresh_btn.config(state="normal"))

    def update_weather_display(self, weather_data):
        try:
            logger.info("Updating weather display")
            self.last_update_label.config(
                text=f"Updated {datetime.now().strftime('%H:%M:%S')} UTC"
            )

            # Update location
            self.location_label.config(
                text=f"📍 {weather_data['name']}, {weather_data['sys']['country']}"
            )

            # Update weather icon and description
            description = weather_data["weather"][0]["description"]
            self.weather_icon.config(text=get_weather_emoji(description))

            # Update temperature
            temp_unit = "C"  # or get it from a user preference setting
            temp, unit = kelvin_to_preferred_unit(
                weather_data["main"]["temp"], temp_unit
            )
            feels_like, _ = kelvin_to_preferred_unit(
                weather_data["main"]["feels_like"], temp_unit
            )

            self.temp_label.config(text=f"{temp:.1f}{unit}")
            self.feels_like_label.config(text=f"Feels like: {feels_like:.1f}{unit}")

            # Update details
            self.detail_labels["humidity"].config(
                text=f"{weather_data['main']['humidity']}%"
            )

            wind_direction = get_wind_direction(weather_data["wind"].get("deg", 0))
            self.detail_labels["wind"].config(
                text=f"{weather_data['wind']['speed']} m/s {wind_direction}"
            )

            self.detail_labels["pressure"].config(
                text=f"{weather_data['main']['pressure']} hPa"
            )

            visibility = format_visibility(weather_data.get("visibility", 0))
            self.detail_labels["visibility"].config(text=visibility)

            # Convert sunrise/sunset times
            timezone_str = weather_data.get("timezone", get_local_timezone())
            sunrise = format_local_time(weather_data["sys"]["sunrise"], timezone_str)
            sunset = format_local_time(weather_data["sys"]["sunset"], timezone_str)

            self.detail_labels["sunrise"].config(text=sunrise)
            self.detail_labels["sunset"].config(text=sunset)
        except Exception as e:
            logger.error(f"Error updating display: {str(e)}")
            self.show_error(f"Error updating display: {str(e)}")

    def show_error(self, message):
        logger.error(f"Error dialog shown: {message}")
        messagebox.showerror("Error", message)

    def setup_forecast_tab(self):
        """Setup the forecast tab with responsive canvas chart and details"""
        # Create main forecast frame without padding options
        forecast_frame = ttk.Frame(self.forecast_tab)
        forecast_frame.pack(fill=tk.BOTH, expand=True)

        # Create upper container for chart
        chart_container = ttk.Frame(forecast_frame)
        # Use pack configuration for padding instead of frame options
        chart_container.pack(fill=tk.BOTH, expand=True, pady=10)

        # Initialize chart_data dictionary
        self.chart_data = {
            "points": [],  # List of (x, y, temp, date, description) tuples
            "temp_range": (0, 0),  # (min_temp, max_temp)
        }

        # Create tooltip label for hover information
        self.tooltip = ttk.Label(chart_container, text="", style="tooltip.TLabel")

        # Create canvas with minimum size and weight
        self.chart_canvas = tk.Canvas(
            chart_container, background="#1e2d3e", height=300, cursor="crosshair"
        )
        self.chart_canvas.pack(fill=tk.BOTH, expand=True, padx=20)

        # Add resize handler
        self.chart_canvas.bind("<Configure>", self.on_canvas_resize)

        # Create legend below chart
        legend_frame = ttk.Frame(forecast_frame)
        legend_frame.pack(fill=tk.X, pady=5)

        ttk.Label(legend_frame, text="● Temperature trend", style="legend.TLabel").pack(
            side=tk.LEFT, padx=5
        )

        # Create separator
        ttk.Separator(forecast_frame, orient="horizontal").pack(fill=tk.X, pady=10)

        # Create frame for daily forecast summary
        self.daily_summary_frame = ttk.Frame(forecast_frame)
        self.daily_summary_frame.pack(fill=tk.X, pady=10)

        # Configure grid columns for daily summary
        for i in range(7):
            self.daily_summary_frame.columnconfigure(i, weight=1)

    def on_canvas_resize(self, event):
        """Handle canvas resize event"""
        if hasattr(self, "last_forecast_data"):
            # Redraw chart with new dimensions
            self.draw_temperature_chart(
                self.last_forecast_data["dates"],
                self.last_forecast_data["temps"],
                self.last_forecast_data["descriptions"],
            )

    def update_forecast_display(self, forecast_data):
        """Update the forecast display with new data"""
        try:
            logger.info("Updating forecast display")

            dates = []
            temps = []
            descriptions = []

            for item in forecast_data["list"]:
                dt = datetime.fromtimestamp(item["dt"])
                temp = item["main"]["temp"] - 273.15
                desc = item["weather"][0]["description"]

                dates.append(dt)
                temps.append(temp)
                descriptions.append(desc)

            # Store the data for resize events
            self.last_forecast_data = {
                "dates": dates,
                "temps": temps,
                "descriptions": descriptions,
            }

            # Draw enhanced temperature chart
            self.draw_temperature_chart(dates, temps, descriptions)

            # Update daily forecast details
            daily_forecasts = self.process_daily_forecasts(forecast_data["list"])
            self.update_daily_forecast_display(daily_forecasts)

        except Exception as e:
            logger.error(f"Error updating forecast display: {str(e)}")
            self.show_error(f"Error updating forecast display: {str(e)}")

    def process_daily_forecasts(self, forecast_list):
        """Process forecast list into daily summaries"""
        daily_forecasts = {}

        for item in forecast_list:
            dt = datetime.fromtimestamp(item["dt"])
            date = dt.date()

            if date not in daily_forecasts:
                daily_forecasts[date] = {
                    "temp_min": float("inf"),
                    "temp_max": float("-inf"),
                    "description": item["weather"][0]["description"],
                }

            temp = item["main"]["temp"] - 273.15
            daily_forecasts[date]["temp_min"] = min(
                daily_forecasts[date]["temp_min"], temp
            )
            daily_forecasts[date]["temp_max"] = max(
                daily_forecasts[date]["temp_max"], temp
            )

        return dict(sorted(daily_forecasts.items())[:7])

    def update_daily_forecast_display(self, daily_forecasts):
        """Update the daily forecast summary"""
        try:
            # Create a frame for daily summaries if it doesn't exist
            if not hasattr(self, "daily_summary_frame"):
                self.daily_summary_frame = ttk.Frame(self.forecast_tab)
                self.daily_summary_frame.pack(fill=tk.X, pady=10, padx=10)

            # Clear existing widgets
            for widget in self.daily_summary_frame.winfo_children():
                widget.destroy()

            # Create summary for each day
            for i, (date, forecast) in enumerate(daily_forecasts.items()):
                day_frame = ttk.Frame(self.daily_summary_frame)
                day_frame.grid(row=0, column=i, padx=5, pady=5, sticky="nsew")
                self.daily_summary_frame.columnconfigure(i, weight=1)

                ttk.Label(
                    day_frame, text=date.strftime("%a"), font=("Helvetica", 9, "bold")
                ).pack()

                ttk.Label(
                    day_frame,
                    text=get_weather_emoji(forecast["description"].lower()),
                    font=("Segoe UI Emoji", 20),
                ).pack()

                ttk.Label(
                    day_frame,
                    text=f"{forecast['temp_max']:.1f}°/{forecast['temp_min']:.1f}°",
                    font=("Helvetica", 9),
                ).pack()

        except Exception as e:
            logger.error(f"Error updating daily forecast display: {str(e)}")

    def draw_temperature_chart(self, dates, temps, descriptions):
        """Draw enhanced temperature chart using Tkinter canvas"""
        self.chart_canvas.delete("all")  # Clear previous drawing
        self.chart_data["points"] = []  # Clear previous points data

        # Get actual canvas size
        width = self.chart_canvas.winfo_width()
        height = self.chart_canvas.winfo_height()

        # Adjust padding based on canvas size
        padding = min(40, width * 0.1)  # Dynamic padding, max 40px

        # Calculate chart dimensions
        chart_width = width - 2 * padding
        chart_height = height - 2 * padding

        # Minimum size check
        if width < 100 or height < 100:
            return  # Canvas too small to draw meaningfully

        # Calculate scale
        min_temp = min(temps)
        max_temp = max(temps)
        temp_range = max(max_temp - min_temp, 1)

        # Draw gradient background (without alpha)
        gradient_steps = 20
        for i in range(gradient_steps):
            y1 = padding + (chart_height * i / gradient_steps)
            y2 = padding + (chart_height * (i + 1) / gradient_steps)
            temp = max_temp - (temp_range * i / gradient_steps)
            color = self.get_temperature_color(temp)
            # Remove alpha parameter
            self.chart_canvas.create_rectangle(
                padding, y1, padding + chart_width, y2, fill=color, outline=color
            )

        # Draw axes and labels
        self.draw_axes(padding, width, height, chart_height, min_temp, max_temp)

        # Draw time labels
        time_interval = max(len(dates) // 6, 1)
        for i in range(0, len(dates), time_interval):
            x = padding + (chart_width * i / (len(dates) - 1))
            self.chart_canvas.create_text(
                x,
                height - padding + 15,
                text=dates[i].strftime("%H:%M"),
                fill="white",
                anchor="n",
            )

        # Draw temperature line and points
        points = []
        for i in range(len(dates)):
            x = padding + (chart_width * i / (len(dates) - 1))
            y = (
                padding
                + chart_height
                - (chart_height * (temps[i] - min_temp) / temp_range)
            )
            points.extend([x, y])

            # Store point data for interaction
            self.chart_data["points"].append(
                (x, y, temps[i], dates[i], descriptions[i])
            )

            # Draw weather emoji
            emoji = get_weather_emoji(descriptions[i])
            self.chart_canvas.create_text(
                x, y - 15, text=emoji, font=("Segoe UI Emoji", 12), fill="white"
            )

            # Draw temperature point with color based on temperature
            color = self.get_temperature_color(temps[i])
            self.chart_canvas.create_oval(
                x - 4, y - 4, x + 4, y + 4, fill=color, outline="white"
            )

        # Draw smooth temperature line
        if len(points) >= 4:
            self.chart_canvas.create_line(points, fill="white", width=2, smooth=True)

    def draw_axes(self, padding, width, height, chart_height, min_temp, max_temp):
        """Draw chart axes with grid and labels"""
        # Draw main axes
        self.chart_canvas.create_line(
            padding, padding, padding, height - padding, fill="white", width=1
        )
        self.chart_canvas.create_line(
            padding,
            height - padding,
            width - padding,
            height - padding,
            fill="white",
            width=1,
        )

        # Draw temperature grid and labels
        for i in range(5):
            y = padding + (chart_height * i / 4)
            temp = max_temp - ((max_temp - min_temp) * i / 4)

            # Draw horizontal grid line
            self.chart_canvas.create_line(
                padding, y, width - padding, y, fill="gray", dash=(2, 4)
            )

            # Draw temperature label
            self.chart_canvas.create_text(
                padding - 20, y, text=f"{temp:.1f}°", fill="white", anchor="e"
            )

    def get_temperature_color(self, temp):
        """Return color based on temperature"""
        if temp <= 0:
            return "#4575b4"  # Cold blue
        elif temp <= 10:
            return "#74add1"  # Cool blue
        elif temp <= 20:
            return "#fee090"  # Warm yellow
        elif temp <= 30:
            return "#f46d43"  # Warm orange
        else:
            return "#d73027"  # Hot red

    def setup_menu(self):
        """Setup application menu"""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)

        # Settings menu
        settings_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Settings", menu=settings_menu)
        settings_menu.add_command(label="Preferences", command=self.show_preferences)
        settings_menu.add_separator()
        settings_menu.add_command(
            label="Manage Favorites", command=self.manage_favorites
        )

    def setup_favorites_dropdown(self):
        """Setup favorites dropdown in header"""
        favorites_frame = ttk.Frame(self.header_frame)
        favorites_frame.pack(side="left", padx=10)

        self.favorites_var = tk.StringVar()
        self.favorites_dropdown = ttk.Combobox(
            favorites_frame, textvariable=self.favorites_var, width=30, state="readonly"
        )
        self.favorites_dropdown.pack(side="left")

        # Bind selection event
        self.favorites_dropdown.bind("<<ComboboxSelected>>", self.on_favorite_selected)

        # Update favorites list
        self.update_favorites_list()

    def update_favorites_list(self):
        """Update the favorites dropdown list"""
        favorites = self.preferences.get_favorites()
        self.favorites_dropdown["values"] = [
            f"{city}, {country}" for city, country in favorites
        ]

    def on_favorite_selected(self, event):
        """Handle favorite location selection"""
        if self.favorites_var.get():
            self.city_var.set(self.favorites_var.get())
            self.refresh_weather()

    def show_preferences(self):
        """Show preferences dialog"""
        prefs_window = tk.Toplevel(self.root)
        prefs_window.title("Preferences")
        prefs_window.geometry("400x300")

        # Units frame
        units_frame = ttk.LabelFrame(prefs_window, text="Units")
        units_frame.pack(fill="x", padx=10, pady=5)

        unit_var = tk.StringVar(value=self.preferences.preferences["units"])
        ttk.Radiobutton(
            units_frame, text="Metric (°C, m/s)", value="metric", variable=unit_var
        ).pack(side="left", padx=5)
        ttk.Radiobutton(
            units_frame, text="Imperial (°F, mph)", value="imperial", variable=unit_var
        ).pack(side="left", padx=5)

        # Auto-detect location
        auto_detect_var = tk.BooleanVar(
            value=self.preferences.preferences["auto_detect_location"] == "true"
        )
        ttk.Checkbutton(
            prefs_window,
            text="Auto-detect location on startup",
            variable=auto_detect_var,
        ).pack(fill="x", padx=10, pady=5)

        # Refresh interval
        refresh_frame = ttk.LabelFrame(prefs_window, text="Refresh Interval")
        refresh_frame.pack(fill="x", padx=10, pady=5)

        refresh_var = tk.StringVar(
            value=self.preferences.preferences["refresh_interval"]
        )
        ttk.Entry(refresh_frame, textvariable=refresh_var).pack(side="left", padx=5)
        ttk.Label(refresh_frame, text="minutes").pack(side="left")

        # Save button
        def save_preferences():
            self.preferences.save_preference("units", unit_var.get())
            self.preferences.save_preference(
                "auto_detect_location", str(auto_detect_var.get()).lower()
            )
            self.preferences.save_preference("refresh_interval", refresh_var.get())
            prefs_window.destroy()
            self.refresh_weather()  # Refresh with new settings

        ttk.Button(prefs_window, text="Save", command=save_preferences).pack(pady=10)

    def manage_favorites(self):
        """Show favorites management dialog"""
        favorites_window = tk.Toplevel(self.root)
        favorites_window.title("Manage Favorites")
        favorites_window.geometry("400x400")

        # List of current favorites
        favorites_frame = ttk.Frame(favorites_window)
        favorites_frame.pack(fill="both", expand=True, padx=10, pady=5)

        favorites = self.preferences.get_favorites()
        for city, country in favorites:
            location_frame = ttk.Frame(favorites_frame)
            location_frame.pack(fill="x", pady=2)

            ttk.Label(location_frame, text=f"{city}, {country}").pack(side="left")

            ttk.Button(
                location_frame,
                text="Remove",
                command=lambda c=city: self.remove_favorite(c),
            ).pack(side="right")

        # Add new favorite
        add_frame = ttk.Frame(favorites_window)
        add_frame.pack(fill="x", padx=10, pady=5)

        new_city_var = tk.StringVar()
        ttk.Entry(add_frame, textvariable=new_city_var).pack(
            side="left", expand=True, fill="x", padx=(0, 5)
        )

        def add_new_favorite():
            city = new_city_var.get().strip()
            if city:
                try:
                    # Get coordinates using geocoding
                    geolocator = Nominatim(user_agent="weather_dashboard")
                    location = geolocator.geocode(city)
                    if location:
                        self.preferences.add_favorite(
                            location.address.split(",")[0],
                            location.address.split(",")[-1].strip(),
                            location.latitude,
                            location.longitude,
                        )
                        self.update_favorites_list()
                        favorites_window.destroy()
                except Exception as e:
                    messagebox.showerror("Error", f"Could not add location: {str(e)}")

        ttk.Button(add_frame, text="Add", command=add_new_favorite).pack(side="right")


def fetch_forecast_data(location):
    """Fetch 5-day forecast data from API"""
    try:
        logger.info(f"Fetching forecast data for location: {location}")
        params = {"appid": Api_Key, "q": location}
        response = session.get(FORECAST_URL, params=params)
        response.raise_for_status()

        forecast_data = response.json()
        logger.info("Forecast data successfully retrieved")
        return forecast_data
    except Exception as e:
        logger.error(f"Error fetching forecast: {str(e)}")
        raise


def main():
    try:
        logger.info("Starting Weather Dashboard application")
        root = tk.Tk()  # Use Tk instead of CTk
        app = WeatherDashboardGUI(root)
        root.mainloop()
    except Exception as e:
        logger.critical(f"Critical error in main loop: {str(e)}")
        raise


if __name__ == "__main__":
    try:
        logger.info("Reading API key")
        Api_Key = open("api_key.txt", "rt").read().strip()
        main()
    except FileNotFoundError:
        logger.critical("API key file not found")
        messagebox.showerror(
            "Error",
            "API key file (api_key.txt) not found.\n\n"
            "Create a file named 'api_key.txt' with your OpenWeatherMap API key",
        )
    except Exception as e:
        logger.critical(f"Failed to start application: {str(e)}")
        messagebox.showerror("Error", f"Failed to start application: {str(e)}")
    finally:
        logger.info("Application shutdown")
