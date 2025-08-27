import tkinter as tk
from tkinter import ttk
from ui_kit import apply_dark_green_theme, RoundedButton
from search_window import SearchWindow

class SystemLogWindow(tk.Toplevel):
    def __init__(self, master: tk.Misc | None = None) -> None:
        super().__init__(master)
        self.title("V-Scribe – System Log")
        self.minsize(420, 620)
        self.protocol("WM_DELETE_WINDOW", self._on_close)
        apply_dark_green_theme(self)

        style = ttk.Style(self)
        try:
            style.theme_use("clam")
        except Exception:
            pass
        style.configure("Heading.TLabel", font=("Segoe UI", 18, "bold"))
        style.configure("Primary.TButton", font=("Segoe UI", 13, "bold"), padding=(18, 13))

        container = ttk.Frame(self)
        container.pack(fill="both", expand=True)
        container.columnconfigure(0, weight=1)

        # Icon log nhỏ phía trên tiêu đề
        icon_label = ttk.Label(container, text="📝", font=("Segoe UI Emoji", 32), anchor="center", background="#ffffff")
        icon_label.grid(row=0, column=0, sticky="n", pady=(32, 0))

        # Tiêu đề nhỏ gọn, căn giữa
        ttk.Label(container, text="System Log", style="Heading.TLabel", anchor="center").grid(
            row=1, column=0, sticky="n", padx=16, pady=(8, 4)
        )

        # Mô tả ngắn
        ttk.Label(container, text="Xem lại nhật ký hệ thống và thực hiện phân tích.", style="TLabel", anchor="center", font=("Segoe UI", 11)).grid(
            row=2, column=0, sticky="n", padx=16, pady=(0, 18)
        )

        # Nút chính nổi bật, căn giữa
        actions = ttk.Frame(container, padding=(16, 0, 16, 16))
        actions.grid(row=3, column=0, sticky="n")
        actions.columnconfigure(0, weight=1)
        RoundedButton(actions, text="Analyze & Convert", command=self.analyze_and_convert, width=220, height=46).grid(row=0, column=0, sticky="n", pady=(10, 0))

    def analyze_and_convert(self) -> None:
        self.withdraw()  # Ẩn cửa sổ hiện tại
        search_window = SearchWindow(master=self)  # Mở cửa sổ tìm kiếm

    def _on_close(self) -> None:
        try:
            if tk._default_root is not None:
                tk._default_root.deiconify()
        except Exception:
            pass
        self.destroy()





