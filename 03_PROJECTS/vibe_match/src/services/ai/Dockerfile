FROM python:3.11-slim

WORKDIR /app

# システム依存
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgl1-mesa-glx libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Python依存
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# CLIPモデルを事前ダウンロード（ビルド時にキャッシュ）
RUN python -c "import open_clip; open_clip.create_model_and_transforms('ViT-L-14', pretrained='openai')"

# アプリケーション
COPY app/ app/

EXPOSE 8080

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080"]
