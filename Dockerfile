FROM python:3.10-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    libnss3 \
    libatk-bridge2.0-0 \
    libdrm-dev \
    libxkbcommon-dev \
    libgbm-dev \
    libasound-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN playwright install chromium

COPY . .

# استفاده از پورت ثابت 8080 (بدون متغیر)
CMD ["gunicorn", "app:app", "--bind", "0.0.0.0:8080"]
