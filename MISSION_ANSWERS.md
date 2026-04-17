# Day 12 Lab - Mission Answers

## Part 1: Localhost vs Production

### Exercise 1.1: Anti-patterns found
1. **Hardcoded Secrets**: API keys like `sk-...` were written trực tiếp vào `app.py`.
2. **Fixed Port/Host**: Sử dụng `port=8000` và `host="localhost"` làm ứng dụng không linh hoạt khi chạy trên Cloud.
3. **Debug Mode Enabled**: `debug=True` trong môi trường Production có thể làm lộ thông tin hệ thống.
4. **Missing Health Checks**: Không có endpoint `/health` để hệ thống giám sát biết ứng dụng có đang sống hay không.
5. **Print Statements**: Dùng `print()` thay vì logging có cấu trúc (JSON) làm việc quản lý log rất khó khăn.

### Exercise 1.3: Comparison table
| Feature | Develop | Production | Why Important? |
|---------|---------|------------|----------------|
| Config  | Hardcoded | Environment Variables | Bảo mật và dễ dàng thay đổi mà không cần sửa code. |
| Health  | None | /health & /ready | Hệ thống Cloud (Railway/Docker) cần để tự động phục hồi app. |
| Logging | print() | Structured JSON | Dễ dàng lọc và theo dõi lỗi trên các hệ thống quản lý log. |
| Shutdown| Sudden | Graceful (SIGTERM) | Đảm bảo các yêu cầu đang xử lý được hoàn tất trước khi tắt app. |

## Part 2: Docker

### Exercise 2.1: Dockerfile questions
1. **Base image**: `python:3.11-slim` để tối ưu dung lượng.
2. **Working directory**: `/app`.
3. **COPY requirements first**: Để tận dụng Docker Layer Caching, giúp build nhanh hơn khi code thay đổi nhưng thư viện không đổi.
4. **CMD**: Sử dụng `python -m app.main` để gọi code một cách nhất quán nhất.

### Exercise 2.3: Image size comparison
- **Develop (Basic)**: ~1 GB (do chứa nhiều công cụ build và rác).
- **Production (Multi-stage)**: ~180 MB.
- **Difference**: Giảm hơn 80% dung lượng, giúp deploy nhanh hơn.

## Part 3: Cloud Deployment

### Exercise 3.1: Railway deployment
- **URL**: [https://2a202600030daoquangthang-production.up.railway.app](https://2a202600030daoquangthang-production.up.railway.app)
- **Deployment Strategy**: Rebuild tự động khi có commit mới trên GitHub thông qua `railway.toml`.

## Part 4: API Security

### Exercise 4.1-4.3: Test results
- **Authentication**: Trả về `401 Unauthorized` nếu thiếu hoặc sai X-API-Key (Đã test thành công).
- **Rate Limit**: Giới hạn 20 request/phút. Trả về `429 Too Many Requests` khi vượt ngưỡng (Đã test thành công).
- **Cost Guard**: Giới hạn $5.0/ngày. Ngắt kết nối khi vượt ngân sách để bảo vệ tài khoản.

### Exercise 4.4: Cost guard implementation
Sử dụng thuật toán đếm token dựa trên độ dài câu hỏi/câu trả lời (mock tokens) và tích lũy vào bộ nhớ in-memory. Khi đạt ngưỡng cấu hình, hệ thống sẽ chặn các request tiếp theo.

## Part 5: Scaling & Reliability

### Exercise 5.1-5.5: Implementation notes
- **Stateless Design**: App không lưu file cục bộ, mọi cấu hình đưa ra biến môi trường, giúp chạy nhiều instance cùng lúc (Scaling).
- **Graceful Shutdown**: Đã bắt tín hiệu `SIGTERM` để log lại quá trình tắt app an toàn.
- **Port Binding**: App tự động nhận diện biến `PORT` từ Railway thay vì dùng port cứng.
