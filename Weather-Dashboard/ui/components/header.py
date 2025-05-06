import tkinter as tk
from tkinter import ttk


class Header(ttk.Frame):
    def __init__(self, parent, on_refresh, on_theme_change):
        super().__init__(parent)
        self.pack(fill=tk.X, pady=(0, 20))

        # Create control frame for buttons
        self.control_frame = ttk.Frame(self)
        self.control_frame.pack(side=tk.RIGHT)

        # Refresh button
        self.refresh_btn = ttk.Button(
            self.control_frame, text="🔄", width=3, command=on_refresh
        )
        self.refresh_btn.pack(side=tk.LEFT, padx=5)

        # Theme toggle button
        self.theme_btn = ttk.Button(
            self.control_frame, text="🌓", width=3, command=on_theme_change
        )
        self.theme_btn.pack(side=tk.LEFT, padx=5)
