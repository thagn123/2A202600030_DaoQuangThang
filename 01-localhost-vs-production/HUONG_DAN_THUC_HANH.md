# Hướng Dẫn Thực Hành: Từ Localhost Đến Production

Tài liệu này hướng dẫn bạn cách nhận diện các lỗi phổ biến khi phát triển ứng dụng (Anti-patterns) và cách áp dụng nguyên lý **12-Factor App** để xây dựng một AI Agent chuyên nghiệp.

---

## 🎯 Mục Tiêu
1. Nhận diện 5 lỗi "chết người" trong phát triển phần mềm.
2. Hiểu cấu trúc quản lý cấu hình bằng biến môi trường (.env).
3. Cách thêm Health Check và Graceful Shutdown.

---

## 🛠 Bước 1: Khám Nghiệm "Lỗi" (Thư mục `develop`)

Mở file `develop/app.py` và tìm các vấn đề sau:

1. **Hardcoded Secrets**: Lưu trực tiếp API Key trong mã nguồn.
    *   *Tại sao sai?*: Nếu bạn đẩy code lên GitHub, toàn bộ thế giới sẽ biết mật khẩu của bạn.
2. **Fixed Port/Host**: Ghi cứng `port=8000` và `host="localhost"`.
    *   *Tại sao sai?*: Khi mang lên Cloud (Railway, Render), họ sẽ yêu cầu app chạy trên một Port ngẫu nhiên được cấp phát qua biến môi trường.
3. **Debug Mode = True**: Luôn bật chế độ sửa lỗi.
    *   *Tại sao sai?*: Làm chậm ứng dụng và vô tình lộ thông tin hệ thống khi có lỗi xảy ra.
4. **Không có Health Check**: Không có đường dẫn nào để kiểm tra app còn sống hay không.
    *   *Tại sao sai?*: Hệ thống tự động (Kubernetes, Docker) không thể biết khi nào app bị treo để khởi động lại.
5. **Dùng `print()` thay vì `logging`**: 
    *   *Tại sao sai?*: `print()` không thể phân cấp độ (INFO, ERROR) và khó tìm kiếm khi có hàng triệu dòng log.

---

## 🚀 Bước 2: Triển Khai Chuẩn Production (Thư mục `production`)

### 1. Tách biệt cấu hình (.env)
*   **Hành động**: Copy `.env.example` thành `.env`.
*   **Tại sao?**: File `.env` sẽ nằm trong máy bạn, không bao giờ được đẩy lên Git. Code sẽ đọc giá trị từ máy thay vì ghi chết trong file.

### 2. Quản lý tập trung (config.py)
*   Sử dụng một Class (như `Settings` trong code) để đọc toàn bộ cấu hình một lần duy nhất.
*   **Fail Fast**: Nếu thiếu cấu hình quan trọng, app sẽ báo lỗi ngay khi khởi động thay vì chạy nửa chừng mới hỏng.

### 3. Thêm Liveness/Readiness Probe
*   Endpoint `/health`: Trả về trạng thái "Tôi vẫn sống".
*   Endpoint `/ready`: Trả về trạng thái "Tôi đã sẵn sàng nhận khách" (Đã kết nối DB, Redis xong).

---

## 🧪 Bước 3: Kiểm Tra Thực Tế

Mở Terminal và thực hiện các lệnh sau để thấy sự khác biệt:

1. **Chạy App:**
   ```powershell
   cd 01-localhost-vs-production/production
   py app.py
   ```

2. **Kiểm tra Health (Mở Terminal mới):**
   ```powershell
   curl http://localhost:8000/health
   ```

3. **Gửi câu hỏi (Test Mock LLM):**
   ```powershell
   curl http://localhost:8000/ask -X POST `
     -H "Content-Type: application/json" `
     -d '{"question": "Xin chào Agent!"}'
   ```

---

## 💡 Ghi chú quan trọng
*   Luôn luôn thêm `.env` vào file `.gitignore`.
*   Sử dụng **Structured Logging (JSON)** để dễ dàng tích hợp với các công cụ theo dõi lỗi như Datadog hoặc Sentry.
*   **Graceful Shutdown**: Luôn xử lý tín hiệu `SIGTERM` để đảm bảo app hoàn thành các yêu cầu dở dang trước khi tắt hẳn.
