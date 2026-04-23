FROM python:3.10-slim

WORKDIR /app

# 設置環境變數避免 Python 寫入 pyc 檔案，並確保直接輸出日誌
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# 複製並安裝相依套件
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 複製專案檔案
COPY . .

# 預設執行指令 (也可以透過 docker-compose 覆寫)
CMD ["python", "batch_attack.py"]
