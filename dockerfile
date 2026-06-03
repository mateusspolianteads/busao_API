FROM python:3.12-slim

WORKDIR /app

# Dependências do sistema pro Chromium funcionar
RUN apt-get update && apt-get install -y \
    wget \
    curl \
    ca-certificates \
    fonts-liberation \
    libnss3 \
    libatk-bridge2.0-0 \
    libgtk-3-0 \
    libx11-xcb1 \
    libasound2 \
    libxcomposite1 \
    libxdamage1 \
    libxrandr2 \
    libgbm1 \
    libxshmfence1 \
    && rm -rf /var/lib/apt/lists/*

# Copia dependências Python
COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

# Instala Playwright + Chromium
RUN pip install playwright
RUN playwright install chromium

# Copia o projeto inteiro
COPY . .

# Evita problemas de cache do playwright no render
ENV PLAYWRIGHT_BROWSERS_PATH=0

# Porta do Render
EXPOSE 10000

# Start do FastAPI
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "10000"]