#!/bin/bash
# ============================================================
# YouTube自動化パイプライン — EC2 初期セットアップスクリプト
# ============================================================
# Usage: bash ec2-setup.sh
#
# 前提: Ubuntu 22.04 LTS on EC2 t3.medium (or better)
# 実行権限: 初期ユーザー (ec2-user or ubuntu)
# 実行後: .env ファイルを編集して API KEY を設定

set -e

# Color output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# ============================================================
# 1. 基本パッケージ更新
# ============================================================
log_info "システムアップデート中..."
sudo apt update
sudo apt upgrade -y

# ============================================================
# 2. 必須ツールインストール
# ============================================================
log_info "必須ツールをインストール中..."
sudo apt install -y \
  python3.10 \
  python3-pip \
  python3-venv \
  ffmpeg \
  git \
  curl \
  wget \
  docker.io \
  awscli

# Python3.10 をデフォルトにする
sudo update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.10 1

log_info "Python: $(python3 --version)"
log_info "ffmpeg: $(ffmpeg -version | head -1)"
log_info "Docker: $(docker --version)"

# ============================================================
# 3. Python 仮想環境構築
# ============================================================
log_info "Python 仮想環境を作成中..."
cd /home/ubuntu
if [ ! -d "venv" ]; then
    python3 -m venv venv
    log_info "仮想環境作成完了: /home/ubuntu/venv"
else
    log_warn "仮想環境は既に存在します"
fi

# 仮想環境を有効化
source /home/ubuntu/venv/bin/activate

# ============================================================
# 4. リポジトリクローン（初回のみ）
# ============================================================
log_info "リポジトリをクローン中..."
if [ ! -d "/home/ubuntu/task" ]; then
    cd /home/ubuntu
    git clone https://github.com/plsr-alt/strategy-to-execution-partner.git task
    log_info "リポジトリクローン完了: /home/ubuntu/task"
else
    log_warn "リポジトリは既に存在します。git pull を実行..."
    cd /home/ubuntu/task
    git pull origin main
fi

# ============================================================
# 5. Python 依存パッケージインストール
# ============================================================
log_info "Python パッケージをインストール中..."
cd /home/ubuntu/task/03_PROJECTS/youtube_automation
pip install --upgrade pip
pip install -r requirements.txt
log_info "パッケージインストール完了"

# ============================================================
# 6. VOICEVOX Docker イメージ起動
# ============================================================
log_info "VOICEVOX Docker イメージをセットアップ中..."
sudo docker pull voicevox/voicevox:latest

# 既存のコンテナがあれば削除
sudo docker stop voicevox 2>/dev/null || true
sudo docker rm voicevox 2>/dev/null || true

# 新しいコンテナを起動
sudo docker run -d \
  --name voicevox \
  -p 50021:50021 \
  voicevox/voicevox:latest

log_info "VOICEVOX が localhost:50021 で起動しました"
sleep 5

# ============================================================
# 7. .env ファイルの準備
# ============================================================
log_info ".env ファイルを準備中..."
if [ ! -f ".env" ]; then
    cp .env.example .env
    log_warn "⚠️  .env ファイルを作成しました。以下のコマンドで編集してください:"
    log_warn "nano /home/ubuntu/task/03_PROJECTS/youtube_automation/.env"
    log_warn ""
    log_warn "以下の値を設定してください:"
    log_warn "  - GROQ_API_KEY"
    log_warn "  - YOUTUBE_API_KEY"
    log_warn "  - YOUTUBE_CLIENT_ID"
    log_warn "  - YOUTUBE_CLIENT_SECRET"
    log_warn "  - PEXELS_API_KEY"
else
    log_info ".env ファイルは既に存在します"
fi

# ============================================================
# 8. 出力・一時ディレクトリの作成
# ============================================================
log_info "出力ディレクトリを作成中..."
mkdir -p /home/ubuntu/task/out
mkdir -p /home/ubuntu/task/tmp
mkdir -p /home/ubuntu/task/03_PROJECTS/youtube_automation/out
mkdir -p /home/ubuntu/task/03_PROJECTS/youtube_automation/tmp

# ============================================================
# 9. Cron スケジューリング設定（オプション）
# ============================================================
log_info "Cron スケジュールを設定中..."
CRON_JOB="0 6 * * * /home/ubuntu/task/03_PROJECTS/youtube_automation/run_pipeline.sh >> /home/ubuntu/task/youtube_pipeline_cron.log 2>&1"

# 既存の Cron がなければ追加
if ! crontab -l 2>/dev/null | grep -q "run_pipeline.sh"; then
    (crontab -l 2>/dev/null; echo "$CRON_JOB") | crontab -
    log_info "✅ Cron 設定完了: 毎日 6:00 に youtube_pipeline.sh を実行"
else
    log_warn "Cron ジョブは既に存在します"
fi

# ============================================================
# 10. テスト実行（オプション）
# ============================================================
read -p "テスト実行しますか？ (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    log_info "テスト実行を開始します..."
    cd /home/ubuntu/task/03_PROJECTS/youtube_automation
    python -m pytest tests/ -v 2>/dev/null || log_warn "テストスイートが見つかりません"
else
    log_info "テスト実行をスキップしました"
fi

# ============================================================
# 11. セットアップ完了
# ============================================================
log_info ""
log_info "============================================================"
log_info "✅ EC2 セットアップが完了しました！！"
log_info "============================================================"
log_info ""
log_info "次のステップ:"
log_info "  1. .env ファイルを編集: nano /home/ubuntu/task/03_PROJECTS/youtube_automation/.env"
log_info "  2. API KEY を設定（GROQ, YouTube, Pexels）"
log_info "  3. パイプラインをテスト: python youtube_pipeline.py"
log_info "  4. 出力を確認: ls -lh out/"
log_info ""
log_info "自動実行設定:"
log_info "  - Cron: 毎日 6:00 に youtube_pipeline.sh を実行"
log_info "  - ログ: /home/ubuntu/task/youtube_pipeline_cron.log"
log_info ""
log_info "Docker 管理:"
log_info "  - VOICEVOX ログ確認: sudo docker logs voicevox"
log_info "  - VOICEVOX 停止: sudo docker stop voicevox"
log_info "  - VOICEVOX 再起動: sudo docker start voicevox"
log_info ""
log_info "AWS S3 バックアップ設定（オプション）:"
log_info "  - aws configure で AWS credentials を設定"
log_info "  - .env の AWS_* を入力"
log_info ""
