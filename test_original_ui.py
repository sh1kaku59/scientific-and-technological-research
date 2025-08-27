import tkinter as tk
from tkinter import ttk, messagebox
import threading
import time
from transcript_result_window import TranscriptResultWindow
from supabase import create_client
import json

# Supabase config
SUPABASE_URL = "https://vvhrhsctmmrmzjztfzcg.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InZ2aHJoc2N0bW1ybXpqenRmemNnIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTUxMTE4NzQsImV4cCI6MjA3MDY4Nzg3NH0.TAyoqYZBwAM7qjDG2zqIkAbvq4gqTMe1sm2sbAk2CpY"

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

def test_with_real_data():
    """Test TranscriptResultWindow với dữ liệu thực từ Supabase"""
    
    print("🚀 Đang test TranscriptResultWindow với dữ liệu thực từ Supabase...")
    print("="*70)
    
    # Lấy dữ liệu thực từ Supabase
    try:
        print("📊 Đang lấy dữ liệu sessions từ Supabase...")
        result = supabase.table("transcripts").select("*").execute()
        
        if not result.data:
            print("❌ Không có transcript nào trong database!")
            messagebox.showerror("Lỗi", "Không có dữ liệu transcript trong Supabase!")
            return
        
        print(f"✅ Tìm thấy {len(result.data)} transcripts:")
        
        # Hiển thị tất cả sessions có sẵn
        available_sessions = []
        for i, transcript in enumerate(result.data):
            session_id = transcript.get('session_id')
            session_folder = session_id.split("_config_audio_")[0] if "_config_audio_" in session_id else session_id
            created_at = transcript.get('created_at')
            total_segments = transcript.get('total_segments', 0)
            
            # Kiểm tra số segments thực tế
            segments_result = supabase.table("transcript_segments").select("*").eq("session_id", session_id).execute()
            actual_segments = len(segments_result.data)
            
            # Nếu không tìm thấy với session_id chính xác, thử pattern
            if actual_segments == 0:
                segments_result = supabase.table("transcript_segments").select("*").ilike("session_id", f"{session_folder}%").execute()
                actual_segments = len(segments_result.data)
            
            available_sessions.append({
                'index': i + 1,
                'session_folder': session_folder,
                'session_id': session_id,
                'created_at': created_at,
                'total_segments': total_segments,
                'actual_segments': actual_segments
            })
            
            print(f"   [{i+1}] {session_folder}")
            print(f"       ID: {session_id}")
            print(f"       Created: {created_at}")
            print(f"       Segments: {actual_segments}/{total_segments}")
            print()
        
        # Tạo root window ẩn
        root = tk.Tk()
        root.withdraw()
        
        # Nếu chỉ có 1 session, sử dụng luôn
        if len(available_sessions) == 1:
            selected_session = available_sessions[0]
            print(f"🎯 Sử dụng session duy nhất: {selected_session['session_folder']}")
        else:
            # Chọn session trong terminal
            print("📋 Chọn session để test:")
            while True:
                try:
                    choice = input("Nhập số session (1 hoặc 2): ").strip()
                    if choice in ['1', '2']:
                        index = int(choice) - 1
                        if 0 <= index < len(available_sessions):
                            selected_session = available_sessions[index]
                            print(f"🎯 Đã chọn session: {selected_session['session_folder']}")
                            break
                    print("❌ Vui lòng nhập 1 hoặc 2")
                except KeyboardInterrupt:
                    print("\n❌ Đã hủy")
                    return
                except:
                    print("❌ Lỗi input, thử lại")
        
        print(f"🚀 Đang khởi tạo TranscriptResultWindow cho session: {selected_session['session_folder']}")
        print(f"   Session ID: {selected_session['session_id']}")
        print(f"   Segments: {selected_session['actual_segments']}")
        print()
        
        # Tạo TranscriptResultWindow với dữ liệu thực
        transcript_window = TranscriptResultWindow(
            master=root,
            session_folder=selected_session['session_folder'],
            config_filename=f"{selected_session['session_folder']}_config.json"
        )
        
        print("✅ TranscriptResultWindow đã được tạo!")
        print()
        print("🎮 HƯỚNG DẪN SỬ DỤNG:")
        print("   • Chờ window load dữ liệu từ Supabase")
        print("   • Click chọn một segment trong danh sách")
        print("   • Double-click segment hoặc click nút 'Phát' để nghe audio")
        print("   • Click 'Dừng' để dừng phát audio")
        print("   • Sử dụng nút 'Xuất TXT' hoặc 'Xuất JSON' để export")
        print("   • Click 'Làm mới' để reload dữ liệu")
        print()
        
        # Hiển thị root window
        root.deiconify()
        root.title("🧪 Test TranscriptResultWindow")
        root.geometry("400x200")
        
        # Thêm instructions vào root window
        instruction_frame = tk.Frame(root, bg="#f0f0f0")
        instruction_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        title_label = tk.Label(instruction_frame, 
                              text="🧪 TranscriptResultWindow Test",
                              font=("Segoe UI", 14, "bold"),
                              bg="#f0f0f0")
        title_label.pack(pady=(0, 10))
        
        info_label = tk.Label(instruction_frame, 
                             text=f"Session: {selected_session['session_folder'][:50]}...\n"
                                  f"Segments: {selected_session['actual_segments']}\n"
                                  f"Status: Đang load dữ liệu...",
                             font=("Segoe UI", 10),
                             bg="#f0f0f0", justify="left")
        info_label.pack(pady=10)
        
        def check_loading_status():
            """Kiểm tra trạng thái loading"""
            def update_status():
                try:
                    if hasattr(transcript_window, 'transcript_data') and transcript_window.transcript_data:
                        # Kiểm tra UI đã load segments chưa
                        if hasattr(transcript_window, 'tree'):
                            segments_count = len(transcript_window.tree.get_children())
                            if segments_count > 0:
                                info_label.config(
                                    text=f"Session: {selected_session['session_folder'][:50]}...\n"
                                         f"Segments: {segments_count} loaded\n"
                                         f"Status: ✅ Sẵn sàng! Hãy test các chức năng"
                                )
                                return
                    
                    # Nếu chưa load xong, tiếp tục check
                    root.after(1000, update_status)
                    
                except Exception:
                    # Window có thể đã bị đóng
                    pass
            
            root.after(2000, update_status)  # Check sau 2 giây
        
        check_loading_status()
        
        def close_all():
            """Đóng tất cả windows"""
            try:
                transcript_window.destroy()
            except:
                pass
            root.destroy()
        
        close_button = tk.Button(instruction_frame, 
                                text="❌ Đóng tất cả",
                                command=close_all,
                                bg="#f44336", fg="white",
                                font=("Segoe UI", 10))
        close_button.pack(pady=10)
        
        root.protocol("WM_DELETE_WINDOW", close_all)
        
        # Start event loop
        print("🖥️ Bắt đầu GUI event loop...")
        root.mainloop()
        
    except Exception as e:
        print(f"❌ Lỗi: {e}")
        import traceback
        traceback.print_exc()
        messagebox.showerror("Lỗi", f"Có lỗi xảy ra: {e}")

def show_session_selection_dialog(parent, sessions):
    """Hiển thị dialog để chọn session"""
    
    dialog = tk.Toplevel(parent)
    dialog.title("Chọn Session để Test")
    dialog.geometry("700x400")
    dialog.transient(parent)
    dialog.grab_set()
    
    # Đưa dialog lên trên cùng
    dialog.lift()
    dialog.focus_force()
    dialog.attributes('-topmost', True)
    dialog.after(100, lambda: dialog.attributes('-topmost', False))
    
    # Center the dialog
    dialog.update_idletasks()
    x = (dialog.winfo_screenwidth() - 700) // 2
    y = (dialog.winfo_screenheight() - 400) // 2
    dialog.geometry(f"700x400+{x}+{y}")
    
    selected_session = None
    
    # Title
    title_label = tk.Label(dialog, 
                          text="📋 Chọn Session để Test",
                          font=("Segoe UI", 14, "bold"))
    title_label.pack(pady=10)
    
    # Sessions listbox
    listbox_frame = tk.Frame(dialog)
    listbox_frame.pack(fill="both", expand=True, padx=20, pady=10)
    
    listbox = tk.Listbox(listbox_frame, font=("Consolas", 9))
    scrollbar = ttk.Scrollbar(listbox_frame, orient="vertical", command=listbox.yview)
    listbox.configure(yscrollcommand=scrollbar.set)
    
    # Populate listbox
    for session in sessions:
        display_text = (f"[{session['index']}] {session['session_folder'][:60]}... "
                       f"({session['actual_segments']}/{session['total_segments']} segments)")
        listbox.insert("end", display_text)
    
    listbox.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")
    
    # Info label
    info_label = tk.Label(dialog, 
                         text="💡 Chọn session:\n• Click vào session rồi nhấn OK\n• Double-click để chọn nhanh\n• Nhấn phím số 1,2,3... rồi Enter",
                         font=("Segoe UI", 9), justify="center")
    info_label.pack(pady=5)
    
    def on_key_press(event):
        """Xử lý phím số để chọn session"""
        try:
            if event.char.isdigit():
                index = int(event.char) - 1
                if 0 <= index < len(sessions):
                    listbox.selection_clear(0, "end")
                    listbox.selection_set(index)
                    listbox.see(index)
            elif event.keysym == "Return":
                on_select()
        except:
            pass
    
    dialog.bind("<Key>", on_key_press)
    dialog.focus_set()
    
    def on_select():
        nonlocal selected_session
        selection = listbox.curselection()
        if selection:
            selected_session = sessions[selection[0]]
            dialog.destroy()
    
    def on_double_click(event):
        on_select()
    
    listbox.bind("<Double-Button-1>", on_double_click)
    
    # Buttons
    button_frame = tk.Frame(dialog)
    button_frame.pack(pady=10)
    
    ok_button = tk.Button(button_frame, text="✅ OK", command=on_select,
                         bg="#4CAF50", fg="white", font=("Segoe UI", 10))
    ok_button.pack(side="left", padx=5)
    
    cancel_button = tk.Button(button_frame, text="❌ Cancel", 
                             command=dialog.destroy,
                             bg="#f44336", fg="white", font=("Segoe UI", 10))
    cancel_button.pack(side="left", padx=5)
    
    # Select first item by default
    if sessions:
        listbox.selection_set(0)
        listbox.focus_set()
    
    # Wait for dialog to close
    dialog.wait_window()
    
    return selected_session

if __name__ == "__main__":
    print("🧪 Starting TranscriptResultWindow Test with Real Supabase Data")
    print("This test will use the original UI with real data from your database")
    print("="*70)
    
    test_with_real_data()
