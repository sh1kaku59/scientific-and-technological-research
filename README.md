# Dự Án: Nghiên Cứu Tách Giọng, Nhận Diện Âm Thanh và Chuyển Đổi Âm Thanh Sang Văn Bản

## Mô tả dự án
Dự án này tập trung vào nghiên cứu và phát triển các giải pháp công nghệ cho việc tách giọng nói, nhận diện âm thanh và chuyển đổi âm thanh sang văn bản. Ứng dụng hướng tới hỗ trợ các bài toán xử lý tiếng nói, phân tích hội thoại, và trích xuất thông tin từ dữ liệu âm thanh.

## Các chức năng chính
- **Tách giọng nói**: Phân tách các nguồn giọng nói khác nhau từ một file âm thanh tổng hợp.
- **Nhận diện âm thanh**: Phân tích và nhận diện các loại âm thanh hoặc sự kiện âm thanh trong file audio.
- **Chuyển đổi âm thanh sang văn bản (Speech-to-Text)**: Chuyển đổi nội dung lời nói trong file âm thanh thành văn bản, hỗ trợ cho việc lưu trữ, tìm kiếm và phân tích dữ liệu.
- **Giao diện người dùng**: Cung cấp giao diện trực quan để tải lên file âm thanh, xem kết quả chuyển đổi, và quản lý nhật ký hệ thống.

## Cấu trúc thư mục
- `Audio Mind.py`: Tập tin chính khởi chạy ứng dụng.
- `search_window.py`, `transcript_result_window.py`, `upload_file_window.py`, `ui_kit.py`: Các module giao diện người dùng.
- `system_log.py`: Quản lý nhật ký hệ thống.
- `requirements.txt`: Danh sách các thư viện cần thiết.
- `__pycache__/`: Thư mục chứa các file biên dịch tạm thời của Python.

## Yêu cầu hệ thống
- Python 3.10 trở lên
- Các thư viện trong `requirements.txt`

## Hướng dẫn cài đặt
1. Cài đặt Python 3.10 hoặc mới hơn.
2. Cài đặt các thư viện cần thiết:
   ```bash
   pip install -r requirements.txt
   ```
3. Chạy ứng dụng:
   ```bash
   python "Audio Mind.py"
   ```

## Đóng góp
Mọi đóng góp, ý kiến hoặc báo lỗi xin gửi về trang GitHub của dự án.

---
**Tác giả:** [sh1kaku59]
**Liên hệ:** [wanbitido090@gmail.com]
