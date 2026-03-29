FROM python:3.14-slim

# Установка зависимостей
RUN apt-get update -y \
    && apt-get install -y --no-install-recommends \
        wget \
        curl \
        unzip \
        gnupg \
        ca-certificates \
        fonts-liberation \
        libnss3 \
        libxss1 \
        libatk-bridge2.0-0 \
        libgtk-3-0 \
        libgbm-dev \
        libasound2 \
        xvfb \
    && rm -rf /var/lib/apt/lists/*

# Установка Google Chrome
RUN wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | gpg --dearmor -o /usr/share/keyrings/google.gpg \
    && echo "deb [arch=amd64 signed-by=/usr/share/keyrings/google.gpg] http://dl.google.com/linux/chrome/deb/ stable main" \
    > /etc/apt/sources.list.d/google.list \
    && apt-get update \
    && apt-get install -y google-chrome-stable

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
CMD ["python", "main.py"]