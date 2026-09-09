FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
# GPU不要（CPU推論で十分な速度が出ることを確認済み）なため、CPU版torchを使い
# イメージサイズを抑える
RUN pip install --no-cache-dir torch --index-url https://download.pytorch.org/whl/cpu \
    && pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8092"]
