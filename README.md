# Mini App – Trợ lý dinh dưỡng học đường

Sản phẩm STEM của Nhóm A trong dự án “Dữ liệu vì sức khỏe học đường”.

## 1. Công nghệ
- Python: ngôn ngữ lập trình.
- Streamlit: xây dựng giao diện web.
- Pandas: đọc, làm sạch và thống kê bảng dữ liệu.
- Plotly: trực quan hóa biểu đồ.
- Openpyxl: hỗ trợ đọc tệp Excel.

## 2. Chạy trên máy tính
1. Cài Python 3.10 trở lên.
2. Giải nén thư mục dự án.
3. Mở Terminal/CMD tại thư mục chứa `app.py`.
4. Tạo môi trường ảo (khuyến nghị): `python -m venv .venv`
5. Kích hoạt:
   - Windows: `.venv\\Scripts\\activate`
   - macOS/Linux: `source .venv/bin/activate`
6. Cài thư viện: `pip install -r requirements.txt`
7. Chạy: `streamlit run app.py`
8. Trình duyệt mở địa chỉ nội bộ do Streamlit cung cấp (thường là http://localhost:8501).

## 3. Triển khai miễn phí bằng GitHub + Streamlit Community Cloud
1. Tạo tài khoản GitHub và đăng nhập.
2. Tạo repository mới, ví dụ `miniapp-dinh-duong-nhom-a`.
3. Tải toàn bộ tệp/thư mục trong dự án lên repository (không tải thư mục `.venv`).
4. Truy cập https://share.streamlit.io/ và đăng nhập bằng GitHub.
5. Chọn **Create app** → chọn repository → branch (thường `main`) → Main file path: `app.py`.
6. Chọn **Deploy**. Chờ hệ thống cài thư viện trong `requirements.txt`.
7. Mở đường dẫn ứng dụng do Streamlit cấp để trình diễn và chia sẻ.

## 4. Cấu trúc thư mục
- `app.py`: toàn bộ giao diện và xử lí dữ liệu; có chú thích theo từng nhóm lệnh.
- `requirements.txt`: danh sách thư viện cần cài.
- `README.md`: hướng dẫn nhanh.
- `data/mau_khao_sat_5_cot.csv`: tệp CSV mẫu, chưa có dữ liệu cá nhân.
- `.streamlit/config.toml`: cấu hình giao diện mặc định.

## 5. Cấu trúc dữ liệu đầu vào
Tệp Excel/CSV phải có đúng các cột:
1. Mã HS
2. Chiều cao (cm)
3. Cân nặng (kg)
4. Số ngày ăn rau xanh, rau quả (ngày/tuần)
5. Số lần sử dụng thức ăn nhanh và đồ uống có đường (lần/tuần)

Tên cột phải khớp mẫu. Không điền dữ liệu suy đoán vào ô trống.

## 6. Lưu ý khoa học và an toàn
- Điểm thói quen 0–2 là quy ước học tập, không phải thang đo y tế.
- BMI ở trẻ em/vị thành niên cần diễn giải theo tuổi và giới; app chỉ hiển thị tham khảo, không chẩn đoán.
- Nhóm BMI minh họa trong Excel chỉ là ví dụ kỹ thuật, không được dùng để xếp loại sức khỏe.
- Không thu thập họ tên hoặc thông tin nhận dạng cá nhân.
- AI chỉ hỗ trợ quá trình phát triển mã; ứng dụng không gọi API AI khi chạy.
