import sys
import tkinter as tk
from tkinter import ttk

from upload_file_window import UploadFileWindow
from system_log import SystemLogWindow
from ui_kit import apply_dark_green_theme, RoundedButton

WINDOW_MIN_WIDTH = 420
WINDOW_MIN_HEIGHT = 620


def on_settings_click(event=None) -> None:
    try:
        if tk._default_root is not None:
            tk._default_root.withdraw()
        SystemLogWindow(master=tk._default_root)
    except Exception as exc:
        print(f"[Settings] Open System Log failed: {exc}")





# Khi bấm nút sẽ mở cửa sổ upload file (từ file riêng)
def on_voice_and_text_click() -> None:
    try:
        if tk._default_root is not None:
            tk._default_root.withdraw()
        UploadFileWindow(master=tk._default_root)
    except Exception as exc:
        print(f"[Action] Upload file window (failed to open): {exc}")





def _enable_windows_high_dpi_if_possible() -> None:
    if sys.platform.startswith("win"):
        try:
            import ctypes  # type: ignore

            ctypes.windll.shcore.SetProcessDpiAwareness(1)
        except Exception:
            pass


class AudioMindApp(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title("V-Scribe")
        self.minsize(WINDOW_MIN_WIDTH, WINDOW_MIN_HEIGHT)

        self._configure_root_grid()
        self._init_styles()

        self._build_topbar()
        self._build_center_logo()
        self._build_action_buttons()

    def _configure_root_grid(self) -> None:
        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)

    def _init_styles(self) -> None:
        apply_dark_green_theme(self)

    def _build_topbar(self) -> None:
        topbar = ttk.Frame(self, padding=(16, 20, 16, 8))
        topbar.grid(row=0, column=0, sticky="ew")
        topbar.columnconfigure(0, weight=1)
        topbar.columnconfigure(1, weight=0)

        title = ttk.Label(topbar, text="V-Scribe", style="Title.TLabel")
        title.grid(row=0, column=0, sticky="n", padx=(0, 12))

        # Đơn giản hóa nút settings (ẩn icon, chỉ còn text nhỏ)
        settings_btn = ttk.Button(topbar, text="Log", style="Primary.TButton", command=on_settings_click)
        settings_btn.grid(row=0, column=1, sticky="e")

    def _build_center_logo(self) -> None:
        center = ttk.Frame(self, padding=(16, 8))
        center.grid(row=1, column=0, sticky="nsew")
        center.columnconfigure(0, weight=1)
        center.rowconfigure(0, weight=1)

        # Icon micro nhỏ phía trên slogan
        icon_label = ttk.Label(center, text="🎤", font=("Segoe UI Emoji", 38), anchor="center", background="#ffffff")
        icon_label.grid(row=0, column=0, sticky="n", pady=(48, 0))

        # Slogan căn giữa, font nhẹ nhàng
        slogan = ttk.Label(center, text="Voice to Text. Simple. Fast. Accurate.", style="TLabel", anchor="center", font=("Segoe UI", 13, "italic"))
        slogan.grid(row=1, column=0, sticky="n", pady=(10, 10))

    def _build_action_buttons(self) -> None:
        actions = ttk.Frame(self, padding=(16, 0, 16, 24))
        actions.grid(row=2, column=0, sticky="sew")
        actions.columnconfigure(0, weight=1)

        # Nút chính đơn giản, tên ngắn gọn
        btn = RoundedButton(actions, text="Chọn file âm thanh", command=on_voice_and_text_click, width=260, height=48)
        btn.grid(row=0, column=0, sticky="n", pady=(16, 0))


def main() -> None:
    _enable_windows_high_dpi_if_possible()
    app = AudioMindApp()
    app.mainloop()


if __name__ == "__main__":
    main()