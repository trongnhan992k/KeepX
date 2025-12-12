# KeepX - Ứng Dụng Ghi Chú Hiện Đại & Bảo Mật

**KeepX** là một ứng dụng quản lý ghi chú mạnh mẽ, được xây dựng trên nền tảng **Django** kết hợp với sức mạnh đám mây của **Firebase**. Ứng dụng tập trung vào trải nghiệm người dùng tối giản, tốc độ phản hồi nhanh và khả năng đồng bộ hóa dữ liệu thời gian thực.

![KeepX Screenshot](https://via.placeholder.com/1200x600?text=KeepX+Dashboard+Preview)
*(Thay thế link trên bằng ảnh chụp màn hình thực tế của dự án)*

## 🚀 Tính Năng Nổi Bật

### 🔐 Xác Thực & Người Dùng
* **Đăng ký/Đăng nhập:** Hỗ trợ xác thực qua Email/Password sử dụng Firebase Authentication.
* **Bảo mật:** Cơ chế xác thực bảo mật khi thực hiện các hành động nhạy cảm (đổi mật khẩu, đổi email).
* **Quên mật khẩu:** Quy trình khôi phục mật khẩu an toàn qua email.
* **Hồ sơ cá nhân:** Cập nhật thông tin, avatar (upload lên Firebase Storage) và quản lý tài khoản.

### 📝 Quản Lý Ghi Chú
* **Soạn thảo:** Hỗ trợ định dạng văn bản (in đậm, nghiêng), danh sách việc cần làm (checklist).
* **Tổ chức:** Ghim ghi chú quan trọng, gán nhãn (Labels) và tô màu nền cho ghi chú.
* **Đa phương tiện:** Đính kèm hình ảnh vào ghi chú.
* **Nhắc nhở:** Đặt lịch nhắc nhở cho từng ghi chú.
* **Thùng rác:** Cơ chế "xóa mềm" cho phép khôi phục ghi chú đã xóa hoặc xóa vĩnh viễn.
* **Chế độ xem:** Chuyển đổi linh hoạt giữa dạng Lưới (Grid) và Danh sách (List).

### 🤝 Chia Sẻ & Hợp Tác
* **Chia sẻ:** Chia sẻ ghi chú với người dùng khác thông qua email.
* **Đồng bộ:** Dữ liệu được đồng bộ hóa tức thì nhờ Firestore.

### 🎨 Giao Diện (UI/UX)
* **Dark Mode:** Hỗ trợ giao diện sáng/tối hoàn chỉnh, tự động theo hệ thống hoặc tùy chỉnh thủ công.
* **Responsive:** Thiết kế tương thích hoàn hảo trên Mobile, Tablet và Desktop nhờ TailwindCSS.

## 🛠️ Công Nghệ Sử Dụng

* **Backend:** Python 3.12, Django 5.2.8
* **Database:** Google Cloud Firestore (NoSQL)
* **Authentication:** Firebase Authentication
* **File Storage:** Firebase Cloud Storage
* **Frontend:**
    * HTML5 / CSS3
    * [TailwindCSS](https://tailwindcss.com/) (CDN) - Styling
    * [Alpine.js](https://alpinejs.dev/) - Tương tác UI nhẹ nhàng
* **Deployment:** Docker, Google Cloud Run (Gunicorn WSGI)

## ⚙️ Yêu Cầu Tiên Quyết

Trước khi cài đặt, đảm bảo máy tính của bạn đã có:
* [Python 3.10+](https://www.python.org/downloads/)
* [Git](https://git-scm.com/)
* Một dự án đã tạo trên [Firebase Console](https://console.firebase.google.com/)

---

## 📥 Hướng Dẫn Cài Đặt (Local)

### 1. Clone dự án
```bash
git clone [https://github.com/trongnhan992k/KeepX.git](https://github.com/trongnhan992k/KeepX.git)
cd KeepX
2. Thiết lập môi trường ảo
Bash

# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
3. Cài đặt thư viện
Bash
pip install -r requirements.txt
4. 🔑 Cấu Hình Firebase (QUAN TRỌNG)
Dự án cần 2 thành phần bảo mật để kết nối Firebase. Tuyệt đối không commit các file này lên Git.

Bước 4.1: File Service Account (Cho Admin SDK)

Truy cập Firebase Console -> Project Settings -> Service accounts.

Chọn Generate new private key.

Đổi tên file tải về thành serviceAccountKey.json.

Đặt file này vào thư mục gốc của dự án (ngang hàng với manage.py).

Bước 4.2: Biến môi trường (.env)

Tạo file .env tại thư mục gốc.

Sao chép nội dung mẫu dưới đây và điền thông tin từ Firebase Console:

Code snippet

# Lấy trong Project Settings -> General -> Web API Key
FIREBASE_WEB_API_KEY=AIzaSyD...

# Lấy trong Storage -> Copy link bucket (bỏ đoạn "gs://")
# Ví dụ: keepx-project.firebasestorage.app
FIREBASE_STORAGE_BUCKET=ten-project-cua-ban.firebasestorage.app

# Cấu hình Django (Đặt True khi chạy Local)
DEBUG=True
SECRET_KEY=django-insecure-random-key...
5. Chạy ứng dụng
Bash

python manage.py runserver
Truy cập ứng dụng tại: http://127.0.0.1:8000

🐳 Chạy với Docker
Dự án đã được cấu hình sẵn Dockerfile để đóng gói và triển khai.

1. Build Docker Image

Bash

docker build -t keepx-app .
2. Chạy Container Lưu ý: Cần đảm bảo file .env và serviceAccountKey.json đã có trong thư mục trước khi build.

Bash

docker run -p 8080:8080 --env-file .env keepx-app
Truy cập tại: http://localhost:8080

📂 Cấu Trúc Dự Án
KeepX/
├── config/                 # Cấu hình Django & Firebase Setup
│   ├── settings.py         # Cài đặt chính, đọc biến môi trường
│   ├── firebase_setup.py   # Khởi tạo Firebase Admin SDK
│   └── urls.py             # Định tuyến gốc
├── notes/                  # App quản lý ghi chú
│   ├── views.py            # Logic CRUD, xử lý ảnh, chia sẻ
│   ├── urls.py             # Định tuyến cho ghi chú
│   └── templates/notes/    # Giao diện danh sách, form, thùng rác
├── users/                  # App quản lý người dùng
│   ├── views.py            # Logic Auth, Profile, Bảo mật
│   ├── forms.py            # Form đăng ký, đăng nhập, đổi mật khẩu
│   └── templates/users/    # Giao diện Auth
├── static/                 # CSS, JS, Images, Favicon
├── templates/              # Base layout & components
├── serviceAccountKey.json  # (Ignored) Key kết nối Firebase Admin
├── .env                    # (Ignored) Biến môi trường
├── Dockerfile              # Cấu hình Docker
├── requirements.txt        # Các thư viện phụ thuộc
└── manage.py
🤝 Đóng Góp (Contributing)
Mọi đóng góp đều được hoan nghênh! Vui lòng thực hiện theo quy trình sau:

Fork dự án.

Tạo nhánh tính năng (git checkout -b feature/TinhNangMoi).

Commit thay đổi (git commit -m 'Thêm tính năng X').

Push lên nhánh (git push origin feature/TinhNangMoi).

Tạo Pull Request.

📄 License
Dự án này được phát hành dưới giấy phép MIT.

Developed with ❤️ by TrongNhan992k
