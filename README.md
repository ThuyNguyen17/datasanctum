# DataSanctum - File Analyzer

Ứng dụng phân tích tập tin đa năng sử dụng trí tuệ nhân tạo (NLP) để phân loại và trích xuất thông tin.

## 🚀 Tính năng chính

- **Hỗ trợ đa định dạng**: Phân tích các loại tập tin phổ biến như `.txt`, `.csv`, `.pdf`, `.docx`, `.json`.
- **Phân loại bằng AI**: Tự động nhận diện chủ đề dựa trên nội dung văn bản sử dụng mô hình Sentence Transformers và KeyBERT.
- **Trích xuất thông tin (Extraction)**: Đọc nội dung văn bản từ các tệp PDF scan hoặc ảnh (OCR) sử dụng Tesseract.
- **Giao diện hiện đại**: Xây dựng bằng `customtkinter` với hỗ trợ Chế độ tối/sáng (Dark/Light Mode).
- **Lịch sử truy cập**: Ghi nhớ các tập tin đã mở gần đây giúp truy cập nhanh chóng.

## 🛠 Cài đặt

Trước khi bắt đầu, hãy đảm bảo máy tính đã cài đặt Python 3.9+.

### 1. Cài đặt các thư viện Python
Sử dụng pip để cài đặt các thư viện cần thiết:
```bash
pip install -r requirements.txt
```

### 2. Cấu hình bên ngoài (Tùy chọn cho OCR)
Để sử dụng tính năng đọc PDF scan và ảnh, bạn cần cài đặt:
- **Tesseract OCR**: [Tải về tại đây](https://github.com/UB-Mannheim/tesseract/wiki). Lưu ý đường dẫn mặc định trong `UI/core/extractors.py` là `C:\Program Files\Tesseract-OCR\tesseract.exe`.
- **Poppler**: Cần thiết cho `pdf2image` để chuyển đổi PDF sang ảnh.

## 🏁 Cách khởi chạy

Mở terminal tại thư mục gốc của dự án và chạy lệnh sau:
```bash
python UI/main.py
```

## 📂 Cấu trúc thư mục

- `UI/main.py`: Điểm khởi đầu của ứng dụng.
- `UI/core/`: Chứa logic xử lý chính bao gồm giao diện, trình xử lý tệp, và quản lý ngôn ngữ/giao diện.
- `UI/core/assets/`: Chứa các bộ dữ liệu mô hình và biểu tượng.
- `classified_files/`: Thư mục chứa các tệp sau khi đã được phân loại theo chủ đề.

![Screenshot 2026-03-23 182822](https://github.com/user-attachments/assets/3b46fa66-bfb9-49e4-be76-29cb392b3ac0)
