"""
Theme Manager for the Batch Renamer Application.
Provides modern, Apple-inspired aesthetics using ttk.Style.
"""
import tkinter as tk
from tkinter import ttk

# Apple-inspired Color Palette
COLOR_BG_MAIN = "#F5F5F7"      # Light Gray Background (Apple standard)
COLOR_BG_PANEL = "#FFFFFF"     # White Panels
COLOR_TEXT_PRIMARY = "#1D1D1F" # Nearly black
COLOR_TEXT_SECONDARY = "#86868B" # Gray text
COLOR_ACCENT = "#0071E3"       # Apple Blue
COLOR_ACCENT_HOVER = "#0077ED" # Lighter Blue
COLOR_BORDER = "#D2D2D7"       # Soft border
COLOR_SUCCESS = "#34C759"      # Apple Green
COLOR_WARNING = "#FF9F0A"      # Apple Orange
COLOR_ERROR = "#FF3B30"        # Apple Red

# Fonts
FONT_PRIMARY = ("Segoe UI", 10)
FONT_BOLD = ("Segoe UI", 10, "bold")
FONT_HEADER = ("Segoe UI", 12, "bold")
FONT_SMALL = ("Segoe UI", 9)

class ModernTheme:
    """Applies a modern, flat, Apple-like theme to the tkinter application."""
    
    def __init__(self, root):
        self.root = root
        self.style = ttk.Style()
        
    def apply(self):
        """Apply the modern theme configuration."""
        
        # 1. Base Configuration
        self.style.theme_use("clam") # Clam provides the best base for customization
        
        # Global Background
        self.root.configure(bg=COLOR_BG_MAIN)
        self.style.configure(".", 
                             background=COLOR_BG_MAIN, 
                             foreground=COLOR_TEXT_PRIMARY, 
                             font=FONT_PRIMARY)
        
        # 2. Frames and Labelframes
        self.style.configure("TFrame", background=COLOR_BG_MAIN)
        
        # Details Panel (White background)
        self.style.configure("Card.TFrame", background=COLOR_BG_PANEL, relief="flat")
        
        self.style.configure("TLabelframe", 
                             background=COLOR_BG_MAIN, 
                             foreground=COLOR_TEXT_SECONDARY,
                             bordercolor=COLOR_BORDER,
                             relief="flat")
        
        self.style.configure("TLabelframe.Label", 
                             foreground=COLOR_TEXT_SECONDARY,
                             background=COLOR_BG_MAIN,
                             font=FONT_BOLD)

        # 3. Notebook (Tabs)
        self.style.configure("TNotebook", background=COLOR_BG_MAIN, borderwidth=0)
        self.style.configure("TNotebook.Tab", 
                             padding=[15, 6], 
                             font=FONT_PRIMARY,
                             background=COLOR_BG_MAIN,
                             foreground=COLOR_TEXT_SECONDARY,
                             borderwidth=0)
        self.style.map("TNotebook.Tab",
                       background=[("selected", COLOR_BG_PANEL), ("active", COLOR_BG_MAIN)],
                       foreground=[("selected", COLOR_ACCENT), ("active", COLOR_TEXT_PRIMARY)],
                       font=[("selected", FONT_BOLD)])

        # 4. Buttons (Flat, Rounded-ish look via border padding)
        # Primary Action Button (Blue)
        self.style.configure("Accent.TButton", 
                             background=COLOR_ACCENT, 
                             foreground="white", 
                             borderwidth=0,
                             relief="flat",
                             font=("Segoe UI", 10, "bold"),
                             padding=[20, 10])
                             
        self.style.map("Accent.TButton",
                       background=[("active", COLOR_ACCENT_HOVER), ("disabled", COLOR_BORDER)])

        # Secondary Button (Gray/White)
        self.style.configure("TButton", 
                             background=COLOR_BG_PANEL, 
                             foreground=COLOR_TEXT_PRIMARY, 
                             borderwidth=1,
                             bordercolor=COLOR_BORDER,
                             relief="flat",
                             padding=[12, 6])
                             
        self.style.map("TButton",
                       background=[("active", "#E5E5EA")],
                       foreground=[("active", "black")])

        # 5. Treeview (Tables)
        self.style.configure("Treeview",
                             background=COLOR_BG_PANEL,
                             fieldbackground=COLOR_BG_PANEL,
                             foreground=COLOR_TEXT_PRIMARY,
                             borderwidth=0,
                             rowheight=28,
                             font=FONT_PRIMARY)
                             
        self.style.configure("Treeview.Heading",
                             background=COLOR_BG_MAIN,
                             foreground=COLOR_TEXT_SECONDARY,
                             font=FONT_BOLD,
                             borderwidth=0,
                             relief="flat")
                             
        self.style.map("Treeview.Heading",
                       background=[("active", COLOR_BG_MAIN)],
                       relief=[("pressed", "flat")])

        # Selection Color
        self.style.map("Treeview",
                       background=[("selected", "#E5F1FB")],
                       foreground=[("selected", COLOR_ACCENT)])

        # 6. Entry and Combobox
        self.style.configure("TEntry", 
                             fieldbackground=COLOR_BG_PANEL,
                             borderwidth=1,
                             relief="solid",
                             bordercolor=COLOR_BORDER,
                             padding=5)
                             
        self.style.configure("TCombobox", 
                             fieldbackground=COLOR_BG_PANEL,
                             background=COLOR_BG_PANEL,
                             borderwidth=1,
                             relief="solid",
                             bordercolor=COLOR_BORDER,
                             arrowcolor=COLOR_TEXT_SECONDARY,
                             padding=5)
        
        # 7. Progress Bar
        self.style.configure("TProgressbar", 
                             background=COLOR_SUCCESS, 
                             troughcolor=COLOR_BORDER,
                             borderwidth=0,
                             thickness=6)

        # 8. Custom Styles for specific elements
        self.style.configure("Header.TLabel", font=FONT_HEADER, foreground=COLOR_TEXT_PRIMARY)
        self.style.configure("Status.TLabel", font=FONT_SMALL, foreground=COLOR_TEXT_SECONDARY, background=COLOR_BG_MAIN)
