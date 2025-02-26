# Sử dụng hình ảnh Python 3.12.3 làm cơ sở
FROM python:3.12.3-slim

# Thiết lập thư mục làm việc
WORKDIR /app

# Sao chép tệp yêu cầu vào thư mục làm việc
COPY requirements.txt .

# Cài đặt các thư viện yêu cầu
# RUN pip install -r requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Sao chép mã nguồn vào thư mục làm việc
COPY . .


# Chạy lệnh để khởi chạy ứng án
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]