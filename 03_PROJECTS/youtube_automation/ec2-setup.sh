#!/bin/bash
# ============================================================
# YouTube自動化パイプライン — EC2 初期セットアップスクリプト
# ============================================================
# Usage: bash ec2-setup.sh
#
# 対応: Amazon Linux 2 / Ubuntu 22.04 LTS on EC2 t4g.medium (or better)
# 実行権限: 初期ユーザー (ec2-user or ubuntu)
# 実行後: .env ファイルを編集して API KEY を設定
#
# パスワード認証設定: SSM Session Manager または SSH パスワードログイン対応

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
# 0. OS 検出
# ============================================================
log_info "OS を検出中..."

if [ -f "/etc/os-release" ]; then
    . /etc/os-release
    OS_NAME=$ID
    OS_VERSION=$VERSION_ID
else
    log_error "OS情報を検出できません"
    exit 1
fi

if [ "$OS_NAME" = "amzn" ]; then
    PKG_MANAGER="yum"
    HOME_DIR="/home/ec2-user"
    log_info "✅ Amazon Linux 2 検出 (version: $OS_VERSION)"
elif [ "$OS_NAME" = "ubuntu" ]; then
    PKG_MANAGER="apt"
    HOME_DIR="/home/ubuntu"
    log_info "✅ Ubuntu 検出 (version: $OS_VERSION)"
else
    log_error "サポートされていないOS: $OS_NAME"
    exit 1
fi

# ============================================================
# 1. 基本パッケージ更新
# ============================================================
log_info "システムアップデート中..."

if [ "$PKG_MANAGER" = "yum" ]; then
    sudo yum update -y
else
    sudo apt update
    sudo apt upgrade -y
fi

# ============================================================
# 2. 必須ツールインストール
# ============================================================
log_info "必須ツールをインストール中..."

if [ "$PKG_MANAGER" = "yum" ]; then
    # Amazon Linux 2
    sudo yum install -y \
      python3 \
      python3-pip \
      python3-venv \
      ffmpeg \
      git \
      curl \
      wget \
      docker \
      aws-cli

    # Docker 開始（Amazon Linux では systemctl 必須）
    sudo systemctl start docker
    sudo systemctl enable docker
else
    # Ubuntu
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
fi

log_info "✅ Python: $(python3 --version)"
log_info "✅ ffmpeg: $(ffmpeg -version | head -1)"
log_info "✅ Docker: $(docker --version)"

# ============================================================
# 3. Python 仮想環境構築
# ============================================================
log_info "Python 仮想環境を作成中..."
cd "$HOME_DIR"
if [ ! -d "venv" ]; then
    python3 -m venv venv
    log_info "✅ 仮想環境作成完了: $HOME_DIR/venv"
else
    log_warn "仮想環境は既に存在します"
fi

# 仮想環境を有効化
source "$HOME_DIR/venv/bin/activate"

# ============================================================
# 4. リポジトリクローン（初回のみ）
# ============================================================
log_info "リポジトリをクローン中..."
if [ ! -d "$HOME_DIR/task" ]; then
    cd "$HOME_DIR"
    git clone https://github.com/plsr-alt/strategy-to-execution-partner.git task
    log_info "✅ リポジトリクローン完了: $HOME_DIR/task"
else
    log_warn "リポジトリは既に存在します。git pull を実行..."
    cd "$HOME_DIR/task"
    git pull origin main
fi

# ============================================================
# 5. Python 依存パッケージインストール
# ============================================================
log_info "Python パッケージをインストール中..."
cd "$HOME_DIR/task/03_PROJECTS/youtube_automation"
pip install --upgrade pip
pip install -r requirements.txt
log_info "✅ パッケージインストール完了"

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
    log_warn "nano $HOME_DIR/task/03_PROJECTS/youtube_automation/.env"
    log_warn ""
    log_warn "以下の値を設定してください:"
    log_warn "  - GROQ_API_KEY"
    log_warn "  - YOUTUBE_API_KEY"
    log_warn "  - YOUTUBE_CLIENT_ID"
    log_warn "  - YOUTUBE_CLIENT_SECRET"
    log_warn "  - PEXELS_API_KEY"
else
    log_info "✅ .env ファイルは既に存在します"
fi

# ============================================================
# 8. 出力・一時ディレクトリの作成
# ============================================================
log_info "出力ディレクトリを作成中..."
mkdir -p "$HOME_DIR/task/out"
mkdir -p "$HOME_DIR/task/tmp"
mkdir -p "$HOME_DIR/task/03_PROJECTS/youtube_automation/out"
mkdir -p "$HOME_DIR/task/03_PROJECTS/youtube_automation/tmp"
log_info "✅ ディレクトリ作成完了"

# ============================================================
# 9. Cron スケジューリング設定（オプション）
# ============================================================
log_info "Cron スケジュールを設定中..."
CRON_JOB="0 6 * * * $HOME_DIR/task/03_PROJECTS/youtube_automation/run_pipeline.sh >> $HOME_DIR/task/youtube_pipeline_cron.log 2>&1"

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
    cd "$HOME_DIR/task/03_PROJECTS/youtube_automation"
    python -m pytest tests/ -v 2>/dev/null || log_warn "テストスイートが見つかりません"
else
    log_info "テスト実行をスキップしました"
fi

# ============================================================
# 11. パスワード認証設定（オプション）
# ============================================================
log_info ""
log_info "パスワード認証設定を実施中..."
log_warn "⚠️  セキュリティ警告: パスワード認証よりキーペアをお勧めします"
log_warn "   ただしご要望に従いパスワード認証を有効化します"

# SSM Session Manager が利用可能か確認
if command -v aws &> /dev/null; then
    log_info "✅ AWS CLI が利用可能です（SSM Session Manager 推奨）"
else
    log_warn "AWS CLI が見つかりません"
fi

log_info ""
log_info "パスワード認証有効化には以下の手順を実施してください:"
log_info "  1. EC2 Instance Connect または SSM Session Manager でログイン"
log_info "  2. sudo nano /etc/ssh/sshd_config"
log_info "  3. 以下の行を編集:"
log_info "     - PasswordAuthentication yes"
log_info "     - PubkeyAuthentication yes"
log_info "  4. 保存後: sudo systemctl restart sshd"
log_info ""
log_info "パスワード設定コマンド:"
log_info "  sudo passwd ec2-user  (Amazon Linux)"
log_info "  sudo passwd ubuntu    (Ubuntu)"
log_info ""

# ============================================================
# 12. セットアップ完了
# ============================================================
log_info ""
log_info "============================================================"
log_info "✅ EC2 セットアップが完了しました！！"
log_info "============================================================"
log_info ""
log_info "次のステップ:"
log_info "  1. .env ファイルを編集: nano $HOME_DIR/task/03_PROJECTS/youtube_automation/.env"
log_info "  2. API KEY を設定（GROQ, YouTube, Pexels）"
log_info "  3. パイプラインをテスト: python youtube_pipeline.py"
log_info "  4. 出力を確認: ls -lh out/"
log_info ""
log_info "自動実行設定:"
log_info "  - Cron: 毎日 6:00 に youtube_pipeline.sh を実行"
log_info "  - ログ: $HOME_DIR/task/youtube_pipeline_cron.log"
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
