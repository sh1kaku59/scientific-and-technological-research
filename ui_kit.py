import tkinter as tk
from tkinter import ttk


# Color palette (light theme: green + white)
BG_DARK = "#ffffff"         # window background (light)
SURFACE = "#f5f5f5"         # cards / canvas surface
OUTLINE = "#c5c5c5"         # borders
TEXT_PRIMARY = "#111827"    # near-black text
TEXT_SECONDARY = "#374151"  # dark gray text
ACCENT = "#16a34a"          # green
ACCENT_HOVER = "#12873e"
ACCENT_ACTIVE = "#0e6f33"


def apply_dark_green_theme(root: tk.Misc) -> None:
    """Applies a cohesive dark + green theme to ttk widgets and root background."""
    try:
        root.configure(bg=BG_DARK)
    except Exception:
        pass

    style = ttk.Style(root)
    try:
        style.theme_use("clam")
    except Exception:
        pass

    # Base containers and labels
    style.configure("TFrame", background=BG_DARK)
    style.configure("Title.TLabel", background=BG_DARK, foreground=TEXT_PRIMARY, font=("Segoe UI", 20, "bold"))
    style.configure("Heading.TLabel", background=BG_DARK, foreground=TEXT_PRIMARY, font=("Segoe UI", 18, "bold"))
    style.configure("TLabel", background=BG_DARK, foreground=TEXT_SECONDARY)

    # Buttons (ttk) – used for smaller actions like Back; big actions use RoundedButton
    style.configure(
        "Primary.TButton",
        background=ACCENT,
        foreground=TEXT_PRIMARY,
        bordercolor=ACCENT,
        focusthickness=0,
        padding=(18, 12),
    )
    style.map(
        "Primary.TButton",
        background=[("active", ACCENT_HOVER), ("pressed", ACCENT_ACTIVE)],
        relief=[("pressed", "sunken"), ("!pressed", "raised")],
    )

    # Progressbar + other accents
    style.configure("Horizontal.TProgressbar", background=ACCENT, troughcolor=SURFACE, bordercolor=OUTLINE, lightcolor=ACCENT, darkcolor=ACCENT)


class RoundedButton(tk.Canvas):
    """A reusable rounded-corner button drawn on a Canvas.

    Provides hover/press states and a simple command callback.
    """

    def __init__(self, parent: tk.Misc, text: str, command=None, width: int = 320, height: int = 50, radius: int = 14):
        super().__init__(parent, width=width, height=height, highlightthickness=0, bg=BG_DARK, bd=0)
        self._text = text
        self._command = command
        self._radius = radius
        self._width = width
        self._height = height
        self._state_fill = ACCENT

        self._shape = self._draw_rounded_rect(2, 2, width - 2, height - 2, radius, fill=ACCENT)
        self._label = self.create_text(width // 2, height // 2, text=text, fill=TEXT_PRIMARY, font=("Segoe UI", 12, "bold"))

        self.bind("<Enter>", self._on_enter)
        self.bind("<Leave>", self._on_leave)
        self.bind("<ButtonPress-1>", self._on_press)
        self.bind("<ButtonRelease-1>", self._on_release)

    def _draw_rounded_rect(self, x1: int, y1: int, x2: int, y2: int, r: int, *, fill: str) -> int:
        # Approximate rounded rectangle using polygons with smoothing
        points = [
            x1 + r, y1,
            x2 - r, y1,
            x2, y1,
            x2, y1 + r,
            x2, y2 - r,
            x2, y2,
            x2 - r, y2,
            x1 + r, y2,
            x1, y2,
            x1, y2 - r,
            x1, y1 + r,
            x1, y1,
        ]
        return self.create_polygon(points, smooth=True, splinesteps=36, fill=fill, outline="")

    def _on_enter(self, _e=None) -> None:
        self._state_fill = ACCENT_HOVER
        self.itemconfigure(self._shape, fill=self._state_fill)

    def _on_leave(self, _e=None) -> None:
        self._state_fill = ACCENT
        self.itemconfigure(self._shape, fill=self._state_fill)

    def _on_press(self, _e=None) -> None:
        self.itemconfigure(self._shape, fill=ACCENT_ACTIVE)

    def _on_release(self, _e=None) -> None:
        # Restore hover or normal
        self.itemconfigure(self._shape, fill=self._state_fill)
        if callable(self._command):
            self._command()


def center_on_screen(win: tk.Misc) -> None:
    try:
        win.update_idletasks()
        try:
            width = int(win.winfo_width())
            height = int(win.winfo_height())
        except Exception:
            width, height = 420, 620
        if width < 50:
            width = 420
        if height < 50:
            height = 620
        screen_w = win.winfo_screenwidth()
        screen_h = win.winfo_screenheight()
        x = (screen_w - width) // 2
        y = (screen_h - height) // 2
        win.geometry(f"+{x}+{y}")
    except Exception:
        pass


