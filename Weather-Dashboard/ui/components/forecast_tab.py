from tkinter import ttk
from .forecast_chart import ForecastChart
from datetime import datetime


class ForecastTab(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.setup_ui()

    def setup_ui(self):
        """Setup forecast tab UI"""
        # Create chart
        self.chart = ForecastChart(self)
        self.chart.pack(fill="both", expand=True, padx=10, pady=10)

        # Create daily summary section
        self.summary_frame = ttk.Frame(self)
        self.summary_frame.pack(fill="x", padx=10, pady=5)

    def update_forecast(self, forecast_data):
        """Update forecast display with new data"""
        try:
            # Process forecast data into daily format
            processed_data = []
            for item in forecast_data["list"]:
                processed_data.append(
                    {
                        "temp": item["main"]["temp"] - 273.15,  # Convert to Celsius
                        "date": datetime.fromtimestamp(item["dt"]),
                        "description": item["weather"][0]["description"],
                        "humidity": item["main"]["humidity"],
                        "wind_speed": item["wind"]["speed"],
                        "icon": WEATHER_EMOJIS.get(
                            item["weather"][0]["description"].lower(), "❓"
                        ),
                    }
                )

            # Update chart with animation
            self.chart.update_chart(processed_data)

            # Update daily summaries
            self.update_summaries(processed_data)
        except Exception as e:
            logger.error(f"Error updating forecast display: {str(e)}")
            raise

    def update_summaries(self, forecast_data):
        """Update daily forecast summaries"""
        # Clear existing summaries
        for widget in self.summary_frame.winfo_children():
            widget.destroy()

        # Group by day and show daily summaries
        daily_data = {}
        for item in forecast_data:
            day = item["date"].date()
            if day not in daily_data:
                daily_data[day] = {
                    "temps": [],
                    "icon": item["icon"],
                    "description": item["description"],
                }
            daily_data[day]["temps"].append(item["temp"])

        # Create summary for each day
        for i, (day, data) in enumerate(list(daily_data.items())[:7]):
            day_frame = ttk.Frame(self.summary_frame)
            day_frame.grid(row=0, column=i, padx=5, pady=5, sticky="nsew")
            self.summary_frame.columnconfigure(i, weight=1)

            ttk.Label(
                day_frame, text=day.strftime("%a"), font=("Helvetica", 9, "bold")
            ).pack()

            ttk.Label(day_frame, text=data["icon"], font=("Segoe UI Emoji", 20)).pack()

            ttk.Label(
                day_frame,
                text=f"{max(data['temps']):.1f}°/{min(data['temps']):.1f}°",
                font=("Helvetica", 9),
            ).pack()
