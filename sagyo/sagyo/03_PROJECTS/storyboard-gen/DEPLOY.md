# DEPLOY.md — EC2 デプロイ手順

## 目次
1. [EC2 準備](#1-ec2-準備)
2. [初回デプロイ](#2-初回デプロイ)
3. [アプリ起動・確認](#3-アプリ起動確認)
4. [更新手順](#4-更新手順)
5. [ログ確認](#5-ログ確認)
6. [停止・再起動](#6-停止再起動)
7. [よくあるエラーと対処](#7-よくあるエラーと対処)

---

## 1. EC2 準備

### インスタンス要件
| 項目 | 推奨 |
|------|------|
| AMI | Amazon Linux 2023 または Ubuntu 22.04 LTS |
| インスタンスタイプ | t3.medium 以上（メモリ 4GB+） |
| ストレージ | 20GB 以上（生成画像が増えると消費する） |
| セキュリティグループ | ポート 22（SSH）・3000（アプリ）を開放 |

### Docker + Docker Compose インストール（Amazon Linux 2023）

```bash
# Docker インストール
sudo dnf install -y docker
sudo systemctl enable --now docker
sudo usermod -aG docker ec2-user
# ← 一度ログアウト＆再ログインして docker グループを反映

# Docker Compose plugin（v2）
sudo mkdir -p /usr/local/lib/docker/cli-plugins
sudo curl -SL "https://github.com/docker/compose/releases/latest/download/docker-compose-linux-$(uname -m)" \
  -o /usr/local/lib/docker/cli-plugins/docker-compose
sudo chmod +x /usr/local/lib/docker/cli-plugins/docker-compose

# 確認
docker --version
docker compose version
```

### Docker インストール（Ubuntu 22.04）

```bash
sudo apt-get update
sudo apt-get install -y ca-certificates curl gnupg
sudo install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] \
  https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | \
  sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
sudo apt-get update
sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin
sudo usermod -aG docker ubuntu
# 再ログイン後に反映
```

---

## 2. 初回デプロイ

### 2-1. ZIP をEC2に配置・展開

```bash
# ローカルから SCP で転送する場合
scp -i your-key.pem storyboard-gen.zip ec2-user@<EC2_IP>:~

# EC2 上で展開
cd ~
unzip storyboard-gen.zip
cd storyboard-gen
```

### 2-2. `.env` ファイルを編集

```bash
cp .env.example .env
nano .env         # または vim .env
```

最低限これだけ設定すればOK:
```
OPENAI_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxxxxx
```

オプション（デフォルトで動く）:
```
DATA_DIR=/data        # コンテナ内パス（変更不要）
JOB_TTL_DAYS=7        # ジョブ自動削除日数
MAX_SCRIPT_LENGTH=5000
DEFAULT_MAX_CUTS=15
MAX_CUTS_LIMIT=30
APP_PORT=3000         # ホスト側ポート（デフォルト3000）
```

### 2-3. 起動

```bash
docker compose up -d --build
```

初回はイメージビルドに 3〜5 分かかります。

---

## 3. アプリ起動・確認

```bash
# コンテナ状態確認
docker compose ps

# ヘルスチェック確認（healthy になるまで待つ）
docker compose ps   # STATUS: healthy になればOK

# ブラウザでアクセス
# http://<EC2のパブリックIP>:3000
```

---

## 4. 更新手順

### ZIP 入れ替えによる更新（git 不要）

```bash
# 1. 新しい ZIP をアップロード
scp -i your-key.pem storyboard-gen-new.zip ec2-user@<EC2_IP>:~

# 2. EC2 上で展開・入れ替え
cd ~
unzip -o storyboard-gen-new.zip   # -o で上書き
cd storyboard-gen

# 3. .env は変更されないが念のため確認
cat .env

# 4. コンテナ停止 → ビルド → 起動
docker compose down
docker compose up -d --build

# 5. 確認
docker compose ps
docker compose logs -f --tail=50
```

> **注意**: `unzip -o` は `.env` ファイルも上書きします。
> `.env.example` だけ上書きされます（`.env` は `.dockerignore` 対象外）が、
> 念のため `cp .env.backup .env` でバックアップを事前に取ることを推奨。

バックアップを取る場合:
```bash
cp .env .env.backup
unzip -o storyboard-gen-new.zip
cp .env.backup .env   # バックアップから復元
```

---

## 5. ログ確認

```bash
# リアルタイムでログを追う
docker compose logs -f

# 最新 100 行
docker compose logs --tail=100

# タイムスタンプ付き
docker compose logs -t --tail=50

# エラーだけ抽出
docker compose logs 2>&1 | grep -i error
```

---

## 6. 停止・再起動

```bash
# 停止（データは保持）
docker compose down

# 再起動
docker compose restart

# 完全停止＋ボリューム削除（全データ消去）
docker compose down -v   # ← 画像データも消えるので注意

# コンテナだけ再作成（ビルドなし）
docker compose up -d --no-build
```

---

## 7. よくあるエラーと対処

### ❌ `OPENAI_API_KEY` が未設定

**症状**: ジョブが `failed` になる。ログに `AuthenticationError` や `401`。

```bash
# 確認
docker compose exec app env | grep OPENAI

# 修正
nano .env  # OPENAI_API_KEY を設定
docker compose down && docker compose up -d
```

---

### ❌ ポート 3000 がすでに使用中

**症状**: `docker compose up` でエラー `bind: address already in use`。

```bash
# 使用中のプロセス確認
sudo lsof -i :3000
# または
sudo ss -tlnp | grep 3000

# .env でポートを変更
APP_PORT=3001   # docker-compose.yml の ${APP_PORT:-3000} に反映

docker compose up -d
```

---

### ❌ `/data` への書き込み権限エラー

**症状**: ログに `EACCES: permission denied, mkdir '/data/...'`

```bash
# ボリュームのオーナー確認（uid=1001 が nextjs ユーザー）
docker compose exec app ls -la /
docker volume inspect storyboard-gen_storyboard_data

# 対処: コンテナを一度削除してボリューム再作成
docker compose down -v
docker compose up -d --build
```

---

### ❌ ディスク容量不足

**症状**: `ENOSPC: no space left on device`

```bash
# 使用量確認
df -h
docker system df

# 古いイメージ・コンテナを削除
docker system prune -af

# ジョブデータが多い場合: ボリュームのパスを確認して手動削除
docker volume inspect storyboard-gen_storyboard_data
# Mountpoint のパスにある古いディレクトリを削除
```

---

### ❌ 画像生成が `failed` になる（rate limit）

**症状**: ログに `429 Too Many Requests`

OpenAI の tier によってはレート制限がかかります。対処:
- `docker compose restart` で処理を再開（既存ジョブは recovery されません。ブラウザから新しいジョブを作成してください）
- OpenAI の利用上限を引き上げる（Tier 2 以上推奨）

---

### ❌ コンテナが `unhealthy` になる

```bash
# ヘルスチェックの詳細を確認
docker inspect storyboard-gen | grep -A 10 '"Health"'

# ログで原因確認
docker compose logs --tail=100

# 強制再起動
docker compose restart
```

---

### ❌ `docker compose: command not found`

Docker Compose v2 がインストールされていない場合。

```bash
# v2 の確認
docker compose version

# v1 系がある場合は v2 をインストール（上記の手順を参照）
```

---

## データの永続化について

生成された画像とジョブ情報は Docker Volume `storyboard_data` に保存されます。

```
/data/{jobId}/
  ├── job.json        # ジョブ状態・カット情報
  ├── cut-001.png     # 生成画像
  ├── cut-002.png
  └── ...
```

`docker compose down` ではデータは消えません（`-v` オプションを付けた場合のみ消えます）。

EC2 インスタンスを停止・再起動してもデータは保持されます（EBS ストレージ）。
