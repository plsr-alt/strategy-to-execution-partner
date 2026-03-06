#!/bin/bash
# EC2 セットアップスクリプト
# 実行: bash ec2_setup.sh

set -e

echo "=========================================="
echo "EC2 セットアップ開始"
echo "=========================================="

# 1. システム更新
echo "[1/6] システム更新中..."
sudo yum update -y

# 2. 開発ツールインストール
echo "[2/6] pip3 と git インストール中..."
sudo yum install -y python3-pip git

# 3. task フォルダ作成
echo "[3/6] task フォルダ作成中..."
mkdir -p /home/ec2-user/task/03_PROJECTS/youtube_automation
mkdir -p /home/ec2-user/task/03_PROJECTS/video_auto_edit
mkdir -p /home/ec2-user/task/out

# 4. Python 依存パッケージインストール
echo "[4/6] 依存パッケージインストール中..."
pip3 install --upgrade pip
pip3 install \
  groq \
  pydantic \
  requests \
  pillow \
  moviepy \
  google-auth \
  google-auth-oauthlib \
  google-auth-httplib2 \
  google-api-python-client \
  python-dotenv \
  ffmpeg-python

# 5. ffmpeg インストール
echo "[5/6] ffmpeg インストール中..."
sudo yum install -y ffmpeg

# 6. 確認
echo "[6/6] インストール確認中..."
echo ""
echo "✅ Python version: $(python3 --version)"
echo "✅ pip3 version: $(pip3 --version)"
echo "✅ git version: $(git --version)"
echo "✅ ffmpeg version: $(ffmpeg -version | head -1)"
echo ""
echo "=========================================="
echo "EC2 セットアップ完了！！"
echo "=========================================="
