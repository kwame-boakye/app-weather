import tkinter as tk
from tkinter import ttk
import time
from utils.logger import logger
from config.constants import TEMP_COLORS
from .weather_animations import WeatherAnimator


class ForecastChart(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.setup_chart()
        self.animation_speed = 20  # ms per frame
        self.hover_point = None
        self.points_data = []
        self.weather_animator = WeatherAnimator(self.canvas)

    def setup_chart(self):
        """Setup the chart canvas and tooltip"""
        # Create canvas
        self.canvas = tk.Canvas(
            self, background="#1e2d3e", height=300, cursor="crosshair"
        )
        self.canvas.pack(fill=tk.BOTH, expand=True)

        # Create tooltip
        self.tooltip = ttk.Label(
            self,
            style="Tooltip.TLabel",
            background="#1a1a1a",
            foreground="white",
            padding=5,
        )

        # Bind mouse events
        self.canvas.bind("<Motion>", self.on_mouse_move)
        self.canvas.bind("<Leave>", self.on_mouse_leave)

    def animate_point(self, points, index=0):
        """Animate points appearing one by one"""
        if index >= len(points):
            return

        x, y, temp, date, desc, details = points[index]

        # Draw point with animation
        radius = 4
        color = self.get_temperature_color(temp)

        # Animate point appearing
        for r in range(radius + 1):
            self.canvas.delete(f"point_{index}")
            self.canvas.create_oval(
                x - r,
                y - r,
                x + r,
                y + r,
                fill=color,
                outline="white",
                tags=(f"point_{index}", "point"),
            )
            self.update()
            time.sleep(0.01)

        # Draw weather icon
        self.canvas.create_text(
            x,
            y - 15,
            text=details["icon"],
            font=("Segoe UI Emoji", 12),
            fill="white",
            tags=("icon",),
        )

        # Draw connecting line to previous point
        if index > 0:
            prev_x, prev_y = points[index - 1][:2]
            self.canvas.create_line(
                prev_x, prev_y, x, y, fill="white", width=2, smooth=True, tags=("line",)
            )

        # Schedule next point
        self.after(self.animation_speed, lambda: self.animate_point(points, index + 1))

    def update_chart(self, forecast_data):
        """Update chart with new forecast data"""
        self.canvas.delete("all")
        self.points_data = []

        # Start weather animation based on current weather
        current_weather = forecast_data[0]["description"].lower()
        self.weather_animator.start_animation(current_weather)

        # Calculate dimensions
        width = self.canvas.winfo_width()
        height = self.canvas.winfo_height()
        padding = min(40, width * 0.1)

        # Process data
        temps = [item["temp"] for item in forecast_data]
        min_temp = min(temps)
        max_temp = max(temps)
        temp_range = max(max_temp - min_temp, 1)

        # Draw axes and grid
        self.draw_axes(padding, width, height, min_temp, max_temp)

        # Prepare points for animation
        points = []
        for i, item in enumerate(forecast_data):
            x = padding + ((width - 2 * padding) * i / (len(forecast_data) - 1))
            y = (
                padding
                + (height - 2 * padding)
                - ((height - 2 * padding) * (item["temp"] - min_temp) / temp_range)
            )

            points.append(
                (
                    x,
                    y,
                    item["temp"],
                    item["date"],
                    item["description"],
                    {
                        "humidity": item["humidity"],
                        "wind_speed": item["wind_speed"],
                        "icon": item["icon"],
                    },
                )
            )
            self.points_data.append((x, y, item))

        # Start animation
        self.animate_point(points)

    def on_mouse_move(self, event):
        """Handle mouse movement over chart"""
        x, y = event.x, event.y

        # Find closest point
        closest_point = None
        min_distance = float("inf")

        for px, py, data in self.points_data:
            distance = ((x - px) ** 2 + (y - py) ** 2) ** 0.5
            if distance < min_distance and distance < 20:
                min_distance = distance
                closest_point = (px, py, data)

        if closest_point:
            self.show_tooltip(closest_point)
            self.highlight_point(closest_point)
        else:
            self.hide_tooltip()
            self.remove_highlight()

    def show_tooltip(self, point_data):
        """Show tooltip with point details"""
        x, y, data = point_data
        tooltip_text = (
            f"Date: {data['date'].strftime('%Y-%m-%d %H:%M')}\n"
            f"Temperature: {data['temp']:.1f}°C\n"
            f"Humidity: {data['humidity']}%\n"
            f"Wind: {data['wind_speed']} m/s\n"
            f"Condition: {data['description']}"
        )

        self.tooltip.configure(text=tooltip_text)
        self.tooltip.place(x=x + 10, y=y - 10)

    def hide_tooltip(self):
        """Hide the tooltip"""
        self.tooltip.place_forget()

    def highlight_point(self, point_data):
        """Highlight the hovered point"""
        if self.hover_point != point_data:
            self.remove_highlight()
            x, y, data = point_data
            self.canvas.create_oval(
                x - 6,
                y - 6,
                x + 6,
                y + 6,
                outline="white",
                width=2,
                tags=("highlight",),
            )
            self.hover_point = point_data

    def remove_highlight(self):
        """Remove point highlight"""
        self.canvas.delete("highlight")
        self.hover_point = None

    def get_temperature_color(self, temp):
        """Get color based on temperature"""
        if temp <= 0:
            return TEMP_COLORS["cold"]
        elif temp <= 10:
            return TEMP_COLORS["cool"]
        elif temp <= 20:
            return TEMP_COLORS["mild"]
        elif temp <= 30:
            return TEMP_COLORS["warm"]
        else:
            return TEMP_COLORS["hot"]

    def draw_axes(self, padding, width, height, min_temp, max_temp):
        """Draw chart axes with grid and labels"""
        # Draw main axes
        self.canvas.create_line(
            padding, padding, padding, height - padding, fill="white", width=1
        )
        self.canvas.create_line(
            padding,
            height - padding,
            width - padding,
            height - padding,
            fill="white",
            width=1,
        )

        # Draw temperature grid and labels
        temp_step = (max_temp - min_temp) / 4
        for i in range(5):
            y = padding + (height - 2 * padding) * i / 4
            temp = max_temp - temp_step * i

            # Draw horizontal grid line
            self.canvas.create_line(
                padding, y, width - padding, y, fill="gray", dash=(2, 4)
            )

            # Draw temperature label
            self.canvas.create_text(
                padding - 10, y, text=f"{temp:.1f}°", fill="white", anchor="e"
            )

        # Draw time labels
        time_step = (width - 2 * padding) / 6
        for i in range(7):
            x = padding + time_step * i
            self.canvas.create_text(
                x, height - padding + 15, text=f"Day {i+1}", fill="white", anchor="n"
            )
