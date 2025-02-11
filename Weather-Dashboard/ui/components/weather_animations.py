import tkinter as tk
from random import randint, choice
import time


class WeatherAnimator:
    def __init__(self, canvas):
        self.canvas = canvas
        self.animation_running = False
        self.particles = []
        self.animation_speed = 50  # ms between frames

    def start_animation(self, weather_type):
        """Start weather animation based on condition"""
        self.stop_animation()
        self.animation_running = True

        if "rain" in weather_type:
            self.animate_rain()
        elif "snow" in weather_type:
            self.animate_snow()
        elif "thunder" in weather_type:
            self.animate_thunder()
        else:
            self.animate_clear_sky()

    def stop_animation(self):
        """Stop current animation"""
        self.animation_running = False
        self.canvas.delete("weather_effect")
        self.particles.clear()

    def animate_rain(self):
        """Animate rainfall"""
        if not self.animation_running:
            return

        width = self.canvas.winfo_width()
        height = self.canvas.winfo_height()

        # Create new raindrops
        while len(self.particles) < 100:
            x = randint(0, width)
            y = randint(-height // 2, 0)
            speed = randint(10, 15)
            self.particles.append(
                {
                    "x": x,
                    "y": y,
                    "speed": speed,
                    "id": self.canvas.create_line(
                        x, y, x, y + 10, fill="#89CFF0", width=1, tags="weather_effect"
                    ),
                }
            )

        # Update raindrop positions
        for drop in self.particles[:]:
            drop["y"] += drop["speed"]
            self.canvas.coords(
                drop["id"], drop["x"], drop["y"], drop["x"], drop["y"] + 10
            )

            # Remove drops that are off screen
            if drop["y"] > height:
                self.canvas.delete(drop["id"])
                self.particles.remove(drop)

        self.canvas.after(self.animation_speed, self.animate_rain)

    def animate_snow(self):
        """Animate snowfall"""
        if not self.animation_running:
            return

        width = self.canvas.winfo_width()
        height = self.canvas.winfo_height()

        # Create new snowflakes
        while len(self.particles) < 50:
            x = randint(0, width)
            y = randint(-height // 2, 0)
            size = randint(3, 6)
            drift = choice([-1, 1])
            speed = randint(2, 4)
            self.particles.append(
                {
                    "x": x,
                    "y": y,
                    "size": size,
                    "drift": drift,
                    "speed": speed,
                    "id": self.canvas.create_text(
                        x,
                        y,
                        text="❄",
                        fill="white",
                        font=("Segoe UI Emoji", size),
                        tags="weather_effect",
                    ),
                }
            )

        # Update snowflake positions
        for flake in self.particles[:]:
            flake["y"] += flake["speed"]
            flake["x"] += flake["drift"] * 0.5
            self.canvas.coords(flake["id"], flake["x"], flake["y"])

            # Remove flakes that are off screen
            if flake["y"] > height or flake["x"] < 0 or flake["x"] > width:
                self.canvas.delete(flake["id"])
                self.particles.remove(flake)

        self.canvas.after(self.animation_speed, self.animate_snow)

    def animate_thunder(self):
        """Animate thunderstorm"""
        if not self.animation_running:
            return

        # Start with rain animation
        self.animate_rain()

        # Add occasional lightning flash
        if randint(1, 50) == 1:  # 2% chance per frame
            self.flash_lightning()

    def flash_lightning(self):
        """Create lightning flash effect"""
        if not self.animation_running:
            return

        # Create flash overlay
        flash = self.canvas.create_rectangle(
            0,
            0,
            self.canvas.winfo_width(),
            self.canvas.winfo_height(),
            fill="white",
            stipple="gray50",
            tags=("weather_effect", "lightning"),
        )

        # Fade out flash
        def fade_flash(opacity):
            if opacity > 0 and self.animation_running:
                self.canvas.itemconfig(flash, stipple=f"gray{opacity}")
                self.canvas.after(50, lambda: fade_flash(opacity - 25))
            else:
                self.canvas.delete(flash)

        fade_flash(75)

    def animate_clear_sky(self):
        """Animate clear sky with subtle sun rays"""
        if not self.animation_running:
            return

        width = self.canvas.winfo_width()
        height = self.canvas.winfo_height()

        # Create subtle gradient background
        self.canvas.delete("sky_gradient")
        colors = ["#87CEEB", "#B0E2FF", "#87CEEB"]  # Sky blue shades
        segments = len(colors) - 1

        for i in range(segments):
            y1 = height * i / segments
            y2 = height * (i + 1) / segments
            self.canvas.create_rectangle(
                0,
                y1,
                width,
                y2,
                fill=colors[i],
                outline=colors[i + 1],
                tags=("weather_effect", "sky_gradient"),
            )

        # Animate subtle sun rays
        def animate_rays():
            if not self.animation_running:
                return

            angle = time.time() * 30  # Rotate 30 degrees per second
            ray_length = min(width, height) * 0.4

            self.canvas.delete("sun_rays")

            # Draw rotating rays
            for i in range(8):
                ray_angle = angle + (i * 45)
                end_x = width / 2 + ray_length * cos(ray_angle)
                end_y = height / 3 + ray_length * sin(ray_angle)

                self.canvas.create_line(
                    width / 2,
                    height / 3,
                    end_x,
                    end_y,
                    fill="#FFD700",
                    width=2,
                    stipple="gray75",
                    tags=("weather_effect", "sun_rays"),
                )

            self.canvas.after(50, animate_rays)

        animate_rays()
