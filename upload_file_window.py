import json
from supabase import create_client
import os
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from transcript_result_window import TranscriptResultWindow

def normalize_filename(name):
    import re, unicodedata
    nfkd = unicodedata.normalize('NFKD', name)
    name = ''.join([c for c in nfkd if not unicodedata.combining(c)])
    name = name.replace(' ', '_')
    name = re.sub(r'[^a-zA-Z0-9._-]', '_', name)
    name = re.sub(r'_+', '_', name)
    name = name.strip('_')
    return name

SUPABASE_URL = "https://vvhrhsctmmrmzjztfzcg.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InZ2aHJoc2N0bW1ybXpqenRmemNnIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTUxMTE4NzQsImV4cCI6MjA3MDY4Nzg3NH0.TAyoqYZBwAM7qjDG2zqIkAbvq4gqTMe1sm2sbAk2CpY"
BUCKET_NAME = "audio-transcripts"

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

def upload_to_supabase(file_path, folder=None):
    import mimetypes
    file_name = os.path.basename(file_path)
    safe_file_name = normalize_filename(file_name)
    
    # Upload file ở root level - KHÔNG thêm prefix folder cho file audio mẫu
    # if folder:
    #     name_part = os.path.splitext(safe_file_name)[0]
    #     ext_part = os.path.splitext(safe_file_name)[1]
    #     safe_file_name = f"{folder}_{name_part}{ext_part}"
    
    print(f"📤 Uploading to Supabase: {safe_file_name}")
    
    with open(file_path, "rb") as f:
        file_data = f.read()
    
    # Detect content type
    content_type, _ = mimetypes.guess_type(file_path)
    if not content_type:
        content_type = "application/octet-stream"
    
    file_options = {
        "content_type": content_type,
        "cache_control": "3600",
        "upsert": True
    }
    
    try:
        print(f"🔄 Attempting upload: {safe_file_name}")
        result = supabase.storage.from_(BUCKET_NAME).upload(safe_file_name, file_data, file_options=file_options)
        print(f"✅ Upload successful: {result}")
    except Exception as upload_error:
        print(f"⚠️ Upload failed, trying update: {upload_error}")
        try:
            result = supabase.storage.from_(BUCKET_NAME).update(safe_file_name, file_data, file_options={"content_type": content_type})
            print(f"✅ Update successful: {result}")
        except Exception as update_error:
            print(f"❌ Update failed: {update_error}")
            raise update_error
    
    public_url = f"{SUPABASE_URL}/storage/v1/object/public/{BUCKET_NAME}/{safe_file_name}"
    print(f"✅ Public URL: {public_url}")
    return public_url, safe_file_name

class UploadFileWindow(tk.Toplevel):
    def upload_config_to_supabase(self, config_dict, folder):
        # Tạo config filename phù hợp với Colab (folder_config.json)
        config_filename = f"{folder}_config.json"
        config_path = config_filename
        
        print(f"🔍 Creating config file: {config_filename}")
        print(f"🔍 Config content: {json.dumps(config_dict, indent=2)}")
        
        # Tạo config file local
        with open(config_path, "w", encoding="utf-8") as f:
            json.dump(config_dict, f, ensure_ascii=False, indent=2)
        
        try:
            with open(config_path, "rb") as f:
                file_data = f.read()
                
            file_options = {
                "content_type": "application/json", 
                "cache_control": "3600",
                "upsert": True
            }
            
            print(f"📤 Uploading config to Supabase: {config_filename}")
            
            # Upload config ở root level (phù hợp với Colab polling)
            try:
                result = supabase.storage.from_(BUCKET_NAME).upload(config_filename, file_data, file_options=file_options)
                print(f"✅ Config upload successful: {result}")
            except Exception as upload_error:
                print(f"⚠️ Config upload failed, trying update: {upload_error}")
                result = supabase.storage.from_(BUCKET_NAME).update(config_filename, file_data, file_options={"content_type": "application/json"})
                print(f"✅ Config update successful: {result}")
                
            public_url = f"{SUPABASE_URL}/storage/v1/object/public/{BUCKET_NAME}/{config_filename}"
            print(f"✅ Config public URL: {public_url}")
            
            return public_url
            
        except Exception as e:
            print(f"❌ Config upload error: {e}")
            raise e
        finally:
            # Xóa file local sau khi upload
            try:
                if os.path.exists(config_path):
                    os.remove(config_path)
                    print(f"🧹 Cleaned up local config: {config_path}")
            except Exception:
                pass

    def _upload_total_file(self):
        file_path = filedialog.askopenfilename(
            title="Chọn file audio tổng",
            filetypes=[
                ("Audio Files", "*.mp3;*.aac;*.wav;*.flac;*.ogg;*.m4a;*.wma;*.aiff;*.alac;*.amr"),
                ("All Files", "*.*")
            ]
        )
        if file_path:
            audio_exts = ('.mp3', '.aac', '.wav', '.flac', '.ogg', '.m4a', '.wma', '.aiff', '.alac', '.amr')
            if not file_path.lower().endswith(audio_exts):
                self.total_label.config(text="Chỉ nhận file âm thanh. Không nhận file video hoặc định dạng khác.")
                return
            self.total_label.config(text="Đang upload file tổng lên Supabase...")
            try:
                base_name = os.path.splitext(os.path.basename(file_path))[0]
                normalized_name = normalize_filename(base_name)
                self.session_folder = normalized_name
                public_url, file_name = upload_to_supabase(file_path, self.session_folder)
                self.audio_file_name = file_name  # Lưu lại tên file thực tế
                self.audio_url = public_url
                print(f"✅ Main audio uploaded: {file_name} -> {public_url}")
                self.total_label.config(text=f"✅ File tổng đã upload: {file_name}")
            except Exception as e:
                error_msg = f"❌ Lỗi upload file tổng: {e}"
                print(error_msg)
                self.total_label.config(text=error_msg)
            except Exception as e:
                self.total_label.config(text=f"Lỗi upload file tổng: {e}")

    def _upload_sample_files(self):
        file_paths = filedialog.askopenfilenames(
            title="Chọn các file mẫu giọng",
            filetypes=[
                ("Audio Files", "*.mp3;*.aac;*.wav;*.flac;*.ogg;*.m4a;*.wma;*.aiff;*.alac;*.amr"),
                ("All Files", "*.*")
            ]
        )
        self.sample_links = []
        if file_paths:
            audio_exts = ('.mp3', '.aac', '.wav', '.flac', '.ogg', '.m4a', '.wma', '.aiff', '.alac', '.amr')
            msg = ""
            for file_path in file_paths:
                if not file_path.lower().endswith(audio_exts):
                    msg += f"Bỏ qua file không hợp lệ: {os.path.basename(file_path)}\n"
                    continue
                try:
                    public_url, file_name = upload_to_supabase(file_path, self.session_folder)
                    # Lưu với name và url phù hợp với Colab
                    self.sample_links.append({"name": file_name, "url": public_url})
                    print(f"✅ Sample uploaded: {file_name} -> {public_url}")
                    msg += f"✅ {file_name}\n"
                except Exception as e:
                    error_msg = f"❌ Lỗi upload {os.path.basename(file_path)}: {e}"
                    print(error_msg)
                    msg += f"❌ {os.path.basename(file_path)}: {e}\n"
            
            if self.sample_links:
                msg += f"\n✅ Đã upload {len(self.sample_links)} file mẫu giọng thành công."
            self.samples_label.config(text=msg)

    def try_send_config(self):
        # Đảm bảo đã upload file tổng và file mẫu thành công
        if not hasattr(self, 'audio_url') or not hasattr(self, 'sample_links') or not self.sample_links:
            self.samples_label.config(text="Bạn cần upload file tổng và ít nhất 1 file mẫu trước!")
            return
            
        # Tạo config đúng format Colab expects
        config = {
            "audio_url": self.audio_url,
            "sample_files": self.sample_links  # Giữ nguyên format name, url
        }
        
        print(f"DEBUG: Creating config with {len(config['sample_files'])} sample files")
        for i, sample in enumerate(config["sample_files"]):
            print(f"  Sample {i+1}: {sample['name']} -> {sample['url'][:50]}...")
            
        try:
            config_url = self.upload_config_to_supabase(config, self.session_folder)
            success_msg = self.samples_label.cget('text') + "\n\n✅ Config đã upload thành công!\nColab sẽ tự động phát hiện và xử lý file mới."
            self.samples_label.config(text=success_msg)
            
            # Tự động chuyển sang màn hình kết quả và đóng cửa sổ upload
            self.open_results_window()
            
        except Exception as e:
            error_msg = self.samples_label.cget('text') + f"\n❌ Lỗi upload config: {e}"
            print(f"❌ Config upload error: {e}")
            self.samples_label.config(text=error_msg)

    def open_results_window(self):
        """Mở cửa sổ xem kết quả transcript"""
        if not hasattr(self, 'session_folder') or not self.session_folder:
            messagebox.showerror("Lỗi", "Chưa có session để xem kết quả!")
            return
            
        config_filename = f"{self.session_folder}_config.json"
        
        # Mở cửa sổ kết quả với master là root thay vì self
        result_window = TranscriptResultWindow(
            master=tk._default_root, 
            session_folder=self.session_folder,
            config_filename=config_filename
        )
        result_window.focus()
        
        # Đóng cửa sổ upload ngay sau khi mở màn hình kết quả
        self.destroy()

    def _on_close(self):
        try:
            if tk._default_root is not None:
                tk._default_root.deiconify()
        except Exception:
            pass
        self.destroy()

    def __init__(self, master=None):
        super().__init__(master)
        self.title("V-Scribe – Upload File")
        self.minsize(420, 320)
        self.protocol("WM_DELETE_WINDOW", self._on_close)

        # Main container, center all widgets
        container = ttk.Frame(self)
        container.pack(expand=True)

        label = ttk.Label(container, text="Chọn file tổng và các file mẫu giọng", font=("Segoe UI", 12, "bold"))
        label.pack(pady=(16, 8))

        btn_total = ttk.Button(container, text="Chọn file audio tổng", command=self._upload_total_file)
        btn_total.pack(pady=4)
        self.total_label = ttk.Label(container, text="", font=("Segoe UI", 10))
        self.total_label.pack(pady=2)

        btn_samples = ttk.Button(container, text="Chọn các file mẫu giọng (nhiều)", command=self._upload_sample_files)
        btn_samples.pack(pady=4)
        self.samples_label = ttk.Label(container, text="", font=("Segoe UI", 10), justify="left")
        self.samples_label.pack(pady=2)

        self.sample_links = []
        self.session_folder = None

        btn_config = ttk.Button(container, text="Tạo & upload config.json", command=self.try_send_config)
        btn_config.pack(pady=10)