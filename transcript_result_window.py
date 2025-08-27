import tkinter as tk
from tkinter import ttk, messagebox
import threading
import time
import webbrowser
from supabase import create_client
import json
import os
from datetime import datetime
import requests
from io import BytesIO
import pygame
import tempfile

# Supabase config
SUPABASE_URL = "https://vvhrhsctmmrmzjztfzcg.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InZ2aHJoc2N0bW1ybXpqenRmemNnIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTUxMTE4NzQsImV4cCI6MjA3MDY4Nzg3NH0.TAyoqYZBwAM7qjDG2zqIkAbvq4gqTMe1sm2sbAk2CpY"
BUCKET_NAME = "audio-transcripts"

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

class TranscriptResultWindow(tk.Toplevel):
    def __init__(self, master=None, session_folder=None, config_filename=None):
        super().__init__(master)
        self.session_folder = session_folder
        self.config_filename = config_filename
        self.polling = False
        self.transcript_data = None
        
        # Dictionary để lưu audio URLs cho mỗi item
        self.item_audio_urls = {}
        
        # Initialize pygame mixer for audio playback
        try:
            pygame.mixer.init()
        except Exception as e:
            print(f"Không thể khởi tạo pygame mixer: {e}")
        
        self.setup_ui()
        self.start_polling()
    
    def setup_ui(self):
        self.title(f"Kết quả Transcript - {self.session_folder}")
        self.geometry("900x600")
        self.protocol("WM_DELETE_WINDOW", self._on_close)
        
        # Header
        header_frame = ttk.Frame(self)
        header_frame.pack(fill="x", padx=10, pady=5)
        
        ttk.Label(header_frame, text="🎯 Kết quả Transcript", font=("Segoe UI", 16, "bold")).pack(side="left")
        
        self.status_label = ttk.Label(header_frame, text="⏳ Đang chờ Colab xử lý...", font=("Segoe UI", 10), foreground="orange")
        self.status_label.pack(side="right")
        
        # Progress frame
        progress_frame = ttk.Frame(self)
        progress_frame.pack(fill="x", padx=10, pady=5)
        
        self.progress = ttk.Progressbar(progress_frame, mode='indeterminate')
        self.progress.pack(fill="x")
        self.progress.start()
        
        # Main content frame
        content_frame = ttk.Frame(self)
        content_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        # Left side - transcript list
        left_frame = ttk.LabelFrame(content_frame, text="📝 Danh sách Transcript")
        left_frame.pack(side="left", fill="both", expand=True, padx=(0, 5))
        
        # Treeview for transcript segments
        columns = ("speaker", "time", "text")
        self.tree = ttk.Treeview(left_frame, columns=columns, show="headings", height=20)
        self.tree.heading("speaker", text="Người nói")
        self.tree.heading("time", text="Thời gian")
        self.tree.heading("text", text="Nội dung")
        
        self.tree.column("speaker", width=100)
        self.tree.column("time", width=100)
        self.tree.column("text", width=400)
        
        # Scrollbar cho treeview
        tree_scroll = ttk.Scrollbar(left_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=tree_scroll.set)
        
        self.tree.pack(side="left", fill="both", expand=True)
        tree_scroll.pack(side="right", fill="y")
        
        # Bind double click to play audio
        self.tree.bind("<Double-1>", self.on_segment_double_click)
        
        # Right side - controls and info
        right_frame = ttk.LabelFrame(content_frame, text="🎮 Điều khiển")
        right_frame.pack(side="right", fill="y", padx=(5, 0))
        
        # Session info
        info_frame = ttk.LabelFrame(right_frame, text="ℹ️ Thông tin Session")
        info_frame.pack(fill="x", padx=5, pady=5)
        
        ttk.Label(info_frame, text=f"Session: {self.session_folder}").pack(anchor="w", padx=5, pady=2)
        
        self.total_segments_label = ttk.Label(info_frame, text="Tổng segments: -")
        self.total_segments_label.pack(anchor="w", padx=5, pady=2)
        
        self.duration_label = ttk.Label(info_frame, text="Thời lượng: -")
        self.duration_label.pack(anchor="w", padx=5, pady=2)
        
        # Audio controls
        audio_frame = ttk.LabelFrame(right_frame, text="🔊 Audio")
        audio_frame.pack(fill="x", padx=5, pady=5)
        
        self.play_button = ttk.Button(audio_frame, text="▶️ Phát", command=self.play_selected_audio, state="disabled")
        self.play_button.pack(fill="x", padx=5, pady=2)
        
        self.stop_button = ttk.Button(audio_frame, text="⏹️ Dừng", command=self.stop_audio, state="disabled")
        self.stop_button.pack(fill="x", padx=5, pady=2)
        
        # Export controls
        export_frame = ttk.LabelFrame(right_frame, text="📤 Xuất dữ liệu")
        export_frame.pack(fill="x", padx=5, pady=5)
        
        self.export_txt_button = ttk.Button(export_frame, text="💾 Xuất TXT", command=self.export_to_txt, state="disabled")
        self.export_txt_button.pack(fill="x", padx=5, pady=2)
        
        self.export_json_button = ttk.Button(export_frame, text="📋 Xuất JSON", command=self.export_to_json, state="disabled")
        self.export_json_button.pack(fill="x", padx=5, pady=2)
        
        # Refresh button
        ttk.Button(right_frame, text="🔄 Làm mới", command=self.manual_refresh).pack(fill="x", padx=5, pady=10)
    
    def start_polling(self):
        """Bắt đầu polling kiểm tra kết quả"""
        self.polling = True
        thread = threading.Thread(target=self.poll_for_results, daemon=True)
        thread.start()
    
    def poll_for_results(self):
        """Polling kiểm tra transcript từ Supabase"""
        while self.polling:
            try:
                print(f"🔍 Polling for session: {self.session_folder}")
                
                # Tìm transcript với session_id khớp với session_folder 
                # Session_id trong DB có format: session_folder_config_audio_timestamp
                result = supabase.table("transcripts").select("*").ilike("session_id", f"{self.session_folder}%").execute()
                
                print(f"📊 Found {len(result.data)} transcripts")
                
                if result.data:
                    # Lấy transcript mới nhất
                    transcript = max(result.data, key=lambda x: x.get("created_at", ""))
                    print(f"✅ Processing transcript: {transcript.get('session_id')}")
                    self.process_transcript_result(transcript)
                    break
                else:
                    print(f"⏳ No transcripts found yet, waiting...")
                    
                time.sleep(10)  # Check mỗi 10 giây
                
            except Exception as e:
                print(f"Polling error: {e}")
                time.sleep(10)
    
    def process_transcript_result(self, transcript_data):
        """Xử lý kết quả transcript"""
        self.transcript_data = transcript_data
        
        # Update UI trên main thread
        self.after(0, self.update_ui_with_results)
    
    def update_ui_with_results(self):
        """Cập nhật UI với kết quả"""
        self.progress.stop()
        self.progress.destroy()
        
        self.status_label.config(text="✅ Hoàn thành!", foreground="green")
        
        # Update info
        metadata = self.transcript_data.get("metadata", {})
        total_segments = self.transcript_data.get("total_segments", 0)
        duration = metadata.get("total_duration", 0)
        
        self.total_segments_label.config(text=f"Tổng segments: {total_segments}")
        self.duration_label.config(text=f"Thời lượng: {duration:.1f}s")
        
        # Load segments
        self.load_transcript_segments()
        
        # Enable buttons
        self.export_txt_button.config(state="normal")
        self.export_json_button.config(state="normal")
        self.play_button.config(state="normal")
        self.stop_button.config(state="normal")
    
    def load_transcript_segments(self):
        """Load các segment transcript vào treeview"""
        try:
            session_id = self.transcript_data["session_id"]
            
            # Lấy segments từ database
            segments_result = supabase.table("transcript_segments").select("*").eq("session_id", session_id).order("start_time").execute()
            
            # Nếu không tìm thấy segments với session_id chính xác, thử tìm với pattern
            if not segments_result.data:
                print(f"⚠️ Không tìm thấy segments cho session_id: {session_id}")
                print("🔍 Thử tìm với pattern...")
                
                # Tìm tất cả segments có session_id bắt đầu với session_folder
                segments_result = supabase.table("transcript_segments").select("*").ilike("session_id", f"{self.session_folder}%").order("start_time").execute()
                
                if segments_result.data:
                    print(f"✅ Tìm thấy {len(segments_result.data)} segments với pattern matching")
                else:
                    print("❌ Vẫn không tìm thấy segments nào")
            
            # Clear existing items
            for item in self.tree.get_children():
                self.tree.delete(item)
            
            # Clear audio URLs dictionary
            self.item_audio_urls.clear()
            
            # Add segments to treeview
            for segment in segments_result.data:
                speaker_name = segment.get("speaker_name", "Unknown")
                start_time = segment.get("start_time", 0)
                end_time = segment.get("end_time", 0)
                text = segment.get("text", "")
                audio_url = segment.get("audio_url", "")
                
                time_str = f"{start_time:.1f}s-{end_time:.1f}s"
                
                item = self.tree.insert("", "end", values=(speaker_name, time_str, text))
                # Store audio URL in dictionary với item ID làm key
                self.item_audio_urls[item] = audio_url
                
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể load segments: {e}")
    
    def on_segment_double_click(self, event):
        """Xử lý double click trên segment"""
        self.play_selected_audio()
    
    def play_selected_audio(self):
        """Phát audio của segment được chọn"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("Chưa chọn", "Vui lòng chọn một segment để phát")
            return
        
        item = selection[0]
        
        # Lấy audio URL từ dictionary
        audio_url = self.item_audio_urls.get(item)
        
        if audio_url:
            print(f"🎵 Playing audio from stored URL: {audio_url[:80]}...")
            self.play_audio_from_url(audio_url)
        else:
            # Fallback: tìm audio URL từ database
            try:
                values = self.tree.item(item)["values"]
                speaker = values[0]
                time_range = values[1]  # "start-end"
                
                # Parse start time
                start_time = float(time_range.split("s-")[0])
                
                # Find segment in database
                session_id = self.transcript_data["session_id"]
                segments_result = supabase.table("transcript_segments").select("*").eq("session_id", session_id).eq("start_time", start_time).execute()
                
                # Nếu không tìm thấy với session_id chính xác, thử pattern matching
                if not segments_result.data:
                    segments_result = supabase.table("transcript_segments").select("*").ilike("session_id", f"{self.session_folder}%").eq("start_time", start_time).execute()
                
                if segments_result.data and segments_result.data[0].get("audio_url"):
                    audio_url = segments_result.data[0]["audio_url"]
                    print(f"🎵 Playing audio from database: {audio_url[:80]}...")
                    self.play_audio_from_url(audio_url)
                else:
                    messagebox.showinfo("Thông báo", "Segment này không có file audio")
                    
            except Exception as e:
                print(f"❌ Error playing audio: {e}")
                messagebox.showerror("Lỗi", f"Không thể phát audio: {e}")
    
    def play_audio_from_url(self, audio_url):
        """Phát audio từ URL"""
        try:
            # Download audio to temp file
            response = requests.get(audio_url)
            response.raise_for_status()
            
            # Save to temp file
            with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_file:
                temp_file.write(response.content)
                temp_path = temp_file.name
            
            # Play audio
            pygame.mixer.music.load(temp_path)
            pygame.mixer.music.play()
            
            # Clean up temp file after playing
            def cleanup():
                time.sleep(1)  # Wait a bit for audio to start
                try:
                    os.unlink(temp_path)
                except Exception:
                    pass
            
            threading.Thread(target=cleanup, daemon=True).start()
            
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể phát audio: {e}")
    
    def stop_audio(self):
        """Dừng phát audio"""
        try:
            pygame.mixer.music.stop()
        except Exception as e:
            print(f"Error stopping audio: {e}")
    
    def export_to_txt(self):
        """Xuất transcript ra file TXT"""
        if not self.transcript_data:
            return
        
        from tkinter import filedialog
        
        filename = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
            initialfile=f"{self.session_folder}_transcript.txt"
        )
        
        if filename:
            try:
                session_id = self.transcript_data["session_id"]
                segments_result = supabase.table("transcript_segments").select("*").eq("session_id", session_id).order("start_time").execute()
                
                # Nếu không tìm thấy với session_id chính xác, thử pattern matching
                if not segments_result.data:
                    segments_result = supabase.table("transcript_segments").select("*").ilike("session_id", f"{self.session_folder}%").order("start_time").execute()
                
                with open(filename, "w", encoding="utf-8") as f:
                    f.write(f"Transcript Session: {session_id}\n")
                    f.write(f"Ngày tạo: {self.transcript_data.get('created_at', '')}\n")
                    f.write("=" * 60 + "\n\n")
                    
                    for segment in segments_result.data:
                        speaker_name = segment.get("speaker_name", "Unknown")
                        start_time = segment.get("start_time", 0)
                        end_time = segment.get("end_time", 0)
                        text = segment.get("text", "")
                        
                        f.write(f"{speaker_name} [{start_time:.1f}s-{end_time:.1f}s]: {text}\n")
                
                messagebox.showinfo("Thành công", f"Đã xuất transcript ra: {filename}")
                
            except Exception as e:
                messagebox.showerror("Lỗi", f"Không thể xuất file: {e}")
    
    def export_to_json(self):
        """Xuất transcript ra file JSON"""
        if not self.transcript_data:
            return
        
        from tkinter import filedialog
        
        filename = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
            initialfile=f"{self.session_folder}_transcript.json"
        )
        
        if filename:
            try:
                session_id = self.transcript_data["session_id"]
                segments_result = supabase.table("transcript_segments").select("*").eq("session_id", session_id).order("start_time").execute()
                
                # Nếu không tìm thấy với session_id chính xác, thử pattern matching
                if not segments_result.data:
                    segments_result = supabase.table("transcript_segments").select("*").ilike("session_id", f"{self.session_folder}%").order("start_time").execute()
                
                export_data = {
                    "session_info": self.transcript_data,
                    "segments": segments_result.data
                }
                
                with open(filename, "w", encoding="utf-8") as f:
                    json.dump(export_data, f, ensure_ascii=False, indent=2)
                
                messagebox.showinfo("Thành công", f"Đã xuất transcript ra: {filename}")
                
            except Exception as e:
                messagebox.showerror("Lỗi", f"Không thể xuất file: {e}")
    
    def manual_refresh(self):
        """Làm mới thủ công"""
        if self.transcript_data:
            self.load_transcript_segments()
        else:
            # Restart polling
            if not self.polling:
                self.start_polling()
    
    def _on_close(self):
        """Xử lý khi đóng cửa sổ"""
        self.polling = False
        self.stop_audio()
        
        # Về lại trang chính
        try:
            if tk._default_root is not None:
                tk._default_root.deiconify()
        except Exception as e:
            print(f"Error showing main window: {e}")
        
        self.destroy()
