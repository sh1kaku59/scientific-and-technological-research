import tkinter as tk
from tkinter import ttk
from supabase import create_client
from transcript_result_window import TranscriptResultWindow

SUPABASE_URL = "https://vvhrhsctmmrmzjztfzcg.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InZ2aHJoc2N0bW1ybXpqenRmemNnIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTUxMTE4NzQsImV4cCI6MjA3MDY4Nzg3NH0.TAyoqYZBwAM7qjDG2zqIkAbvq4gqTMe1sm2sbAk2CpY"
BUCKET_NAME = "audio-transcripts"

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

class SearchWindow(tk.Toplevel):
    def __init__(self, master=None):
        super().__init__(master)
        self.title("Tìm kiếm cuộc họp")
        self.geometry("900x540")
        self.configure(bg="#f5f5f5")

        # Đóng cửa sổ sẽ tắt luôn app
        self.protocol("WM_DELETE_WINDOW", self.on_close)

        # Khởi tạo transcript_rows trước
        self.transcript_rows = self.get_all_audio_files()

        # Frame tổng căn giữa
        main_frame = ttk.Frame(self, padding=(0, 16, 0, 16))
        main_frame.pack(fill=tk.BOTH, expand=True)
        main_frame.columnconfigure(0, weight=1)

        # Icon kính lúp lớn
        icon_label = ttk.Label(main_frame, text="🔎", font=("Segoe UI Emoji", 38), anchor="center", background="#f5f5f5")
        icon_label.grid(row=0, column=0, pady=(10, 0))

        # Tiêu đề lớn
        title_label = ttk.Label(main_frame, text="Tìm kiếm cuộc họp", font=("Segoe UI", 22, "bold"), anchor="center", background="#f5f5f5")
        title_label.grid(row=1, column=0, pady=(2, 0))

        # Mô tả ngắn
        desc_label = ttk.Label(main_frame, text="Nhập từ khóa để tìm kiếm file ghi âm, nội dung hoặc người nói.", font=("Segoe UI", 11), anchor="center", foreground="#555", background="#f5f5f5")
        desc_label.grid(row=2, column=0, pady=(0, 10))

        # Ô tìm kiếm đẹp
        self.search_var = tk.StringVar()
        self.search_var.trace('w', self.on_search_change)
        search_entry = ttk.Entry(main_frame, textvariable=self.search_var, font=("Segoe UI", 12))
        search_entry.grid(row=3, column=0, sticky="ew", padx=60, pady=(0, 8))
        search_entry.insert(0, "Nhập từ khóa...")
        def clear_placeholder(event):
            if search_entry.get() == "Nhập từ khóa...":
                search_entry.delete(0, tk.END)
        def restore_placeholder(event):
            if not search_entry.get():
                search_entry.insert(0, "Nhập từ khóa...")
        search_entry.bind("<FocusIn>", clear_placeholder)
        search_entry.bind("<FocusOut>", restore_placeholder)

        # Frame chứa thông báo và bảng
        self.content_frame = ttk.Frame(main_frame)
        self.content_frame.grid(row=4, column=0, sticky="nsew", padx=10, pady=(0, 0))
        self.content_frame.columnconfigure(0, weight=1)

        # Label thông báo
        self.message_label = ttk.Label(
            self.content_frame,
            text="Vui lòng nhập từ khóa để tìm kiếm cuộc họp...",
            font=("Segoe UI", 11),
            foreground='#888',
            anchor="center",
            background="#f5f5f5"
        )
        self.message_label.pack(expand=True)

        # Bảng kết quả hiện đại
        columns = ("session_id", "original_filename", "created_at")
        style = ttk.Style()
        style.configure("Treeview.Heading", font=("Segoe UI", 11, "bold"), background="#e5e5e5")
        style.configure("Treeview", font=("Segoe UI", 11), rowheight=28, borderwidth=0, relief="flat")
        self.file_tree = ttk.Treeview(self.content_frame, columns=columns, show="headings", style="Treeview")
        self.file_tree.heading("session_id", text="ID Cuộc Họp")
        self.file_tree.heading("original_filename", text="Tên File")
        self.file_tree.heading("created_at", text="Thời Gian")
        self.file_tree.column("session_id", width=340, anchor="center")
        self.file_tree.column("original_filename", width=300, anchor="center")
        self.file_tree.column("created_at", width=220, anchor="center")
        self.file_tree.pack_forget()
        self.file_tree.bind("<Double-1>", self.on_file_double_click)

    def display_files(self, rows):
        self.file_tree.delete(*self.file_tree.get_children())
        
        if not rows:
            # Ẩn bảng và hiện thông báo không tìm thấy
            self.file_tree.pack_forget()
            self.message_label.configure(text="Không tìm thấy kết quả phù hợp...")
            self.message_label.pack(expand=True)
            return
            
        # Ẩn thông báo và hiện bảng kết quả
        self.message_label.pack_forget()
        self.file_tree.pack(fill=tk.BOTH, expand=True)
        
        for item in rows:
            created_at = item.get("created_at", "")[:19]
            session_id = item.get("session_id", "")
            
            # Format ngày giờ đẹp hơn
            try:
                date_part = created_at[:10]
                time_part = created_at[11:19]
                created_at = f"{date_part}\n{time_part}"
            except:
                pass
                
            self.file_tree.insert(
                "", "end",
                values=(session_id, item['original_filename'], created_at)
            )

    def search_files(self):
        term = self.search_var.get().lower().strip()
        
        if not term:  # Nếu ô tìm kiếm trống
            # Ẩn bảng và hiện thông báo nhập
            self.file_tree.pack_forget()
            self.message_label.configure(text="Vui lòng nhập từ khóa để tìm kiếm cuộc họp...")
            self.message_label.pack(expand=True)
            return
            
        filtered = []
        for item in self.transcript_rows:
            try:
                # Chuẩn bị dữ liệu tìm kiếm
                created_date = item.get('created_at', '')[:10]
                transcript_text = str(item.get('transcript_text', '')).lower()
                speakers = [s.lower() for s in item.get('speakers', []) if s]
                session_id = item.get('session_id', '').lower()
                
                # Tìm kiếm trong tất cả các trường
                if (any(term in speaker for speaker in speakers) or
                    term in transcript_text or
                    term in created_date.lower() or
                    term in session_id):
                    filtered.append(item)
            except Exception as e:
                print(f"Lỗi khi xử lý item: {e}")
                
        self.display_files(filtered)

    def get_all_audio_files(self):
        # Lấy dữ liệu từ bảng transcripts
        transcripts_response = supabase.table("transcripts").select(
            "session_id, original_filename, audio_url, created_at, metadata"
        ).execute()
        
        # Lấy dữ liệu từ bảng transcript_segments
        segments_response = supabase.table("transcript_segments").select(
            "session_id, text, speaker_name"
        ).execute()
        
        # Tạo dictionary để map session_id với text và speaker_name
        session_data = {}
        for segment in (segments_response.data or []):
            session_id = segment.get('session_id', '')
            text = segment.get('text', '')
            speaker = segment.get('speaker_name', '')
            
            if session_id not in session_data:
                session_data[session_id] = {
                    'text': '',
                    'speakers': set()
                }
            
            # Gộp text và thêm speaker vào set
            session_data[session_id]['text'] += " " + text
            if speaker:
                session_data[session_id]['speakers'].add(speaker)
        
        # Kết hợp dữ liệu từ cả hai bảng
        combined_data = []
        for transcript in (transcripts_response.data or []):
            session_id = transcript['session_id']
            session_info = session_data.get(session_id, {'text': '', 'speakers': set()})
            
            # Thêm text và danh sách speaker vào transcript
            transcript['transcript_text'] = session_info['text']
            transcript['speakers'] = list(session_info['speakers'])
            combined_data.append(transcript)
            
        return combined_data

    def on_search_change(self, *args):
        """Xử lý khi nội dung ô tìm kiếm thay đổi"""
        # Tự động tìm kiếm khi người dùng gõ
        self.search_files()

    def on_file_double_click(self, event):
        selected = self.file_tree.selection()
        if selected:
            item = self.file_tree.item(selected[0])
            session_id = item['values'][0]  # Lấy session_id từ cột đầu tiên
            
            # Tách lấy session_folder từ session_id
            session_folder = session_id.split("_config_audio_")[0] if "_config_audio_" in session_id else session_id
            
            print(f"Session Folder truyền vào: {session_folder}")
            
            # Chỉ truyền session_folder vào TranscriptResultWindow
            TranscriptResultWindow(master=self.master, session_folder=session_folder)
            self.destroy()

    def on_close(self):
        # Đóng SearchWindow và hiện lại trang chính
        if self.master:
            self.master.deiconify()
        self.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    root.withdraw()
    SearchWindow(root)
    root.mainloop()