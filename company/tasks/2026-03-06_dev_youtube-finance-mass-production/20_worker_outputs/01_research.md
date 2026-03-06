# YouTube自動化パイプライン — 既存コード調査結果

## (1) run_pipeline.sh の呼び出し引数・ログ出力先・set -e の影響

### 呼び出し引数
```bash
# 基本形式（引数なし）
./run_pipeline.sh

# または crontab で
0 6 * * * /path/to/run_pipeline.sh
```

**youtube_pipeline.py への引数**:
```bash
python3 youtube_pipeline.py \
    --output "$LOG_DIR" \
    --log-file "$LOG_FILE"
```

### ログ出力先
```
$LOG_DIR = "$PROJECT_DIR/out"  # プロジェクトディレクトリ内の out フォルダ
$LOG_FILE = "$LOG_DIR/pipeline_$(date +%Y%m%d_%H%M%S).log"
# 例: ./out/pipeline_20260305_120000.log
```

**ログ出力方式**:
- stdout/stderr を `>> "$LOG_FILE" 2>&1` でファイルにリダイレクト
- 同時に画面にも色付き出力（log_info/log_error 関数）

### set -e の影響と注意点
```bash
set -e  # 行21: スクリプト全体で有効
```

**動作**:
- **any command で exit code != 0 になったらスクリプト終了**
- 途中でエラーが発生した場合、即座に exit 1 で終了
- バッチから呼ぶ場合、exit code を必ず確認する必要あり

**注意点**:
- 環境変数チェック（行64-68）で失敗 → スクリプト終了
- ffmpeg/python3 チェック（行83-90）で失敗 → スクリプト終了
- python3 実行で fail → 最後の exit 1 に到達（行145）

**バッチから呼ぶ際の推奨**:
```bash
# set +e で エラー継続を許可
set +e
./run_pipeline.sh
result=$?
set -e

if [ $result -ne 0 ]; then
    echo "Pipeline failed with code $result"
    # エラー対応
fi
```

---

## (2) ec2-setup.sh が前提とするディレクトリ構造・venvパス

### ホームディレクトリ自動検出
```bash
# 行44-51: 自動検出
if [ -d "/home/ec2-user" ]; then
    HOME_DIR="/home/ec2-user"  # Amazon Linux 2
elif [ -d "/home/ubuntu" ]; then
    HOME_DIR="/home/ubuntu"    # Ubuntu
fi
```

### 前提ディレクトリ構造（セットアップ後）
```
$HOME_DIR/
├── venv/                           # 行119-121: Python仮想環境
│   ├── bin/activate
│   └── lib/python3.x/site-packages/
├── task/                           # 行133-135: Git リポジトリ
│   ├── 03_PROJECTS/
│   │   └── youtube_automation/
│   │       ├── .env
│   │       ├── requirements.txt
│   │       ├── youtube_pipeline.py
│   │       ├── run_pipeline.sh
│   │       ├── out/               # 行196-197: ログ出力先
│   │       └── tmp/               # 同上: 一時ファイル
│   └── out/                        # 行194: トップレベルログ
└── youtube_pipeline_cron.log       # 行204: Cron実行ログ

```

### venvパス（確定）
```
$HOME_DIR/venv/bin/activate

# run_pipeline.sh での検出（行53-59）:
if [ -f "$HOME_DIR/venv/bin/activate" ]; then
    source "$HOME_DIR/venv/bin/activate"
fi
```

**パッケージインストール先**:
```bash
# 行147-149
cd "$HOME_DIR/task/03_PROJECTS/youtube_automation"
pip install -r requirements.txt
# → $HOME_DIR/venv/lib/python3.x/site-packages/ へインストール
```

---

## (3) EC2上の最終的なファイル配置パス（~/youtube_automation/ に統一予定）

### 現在の構造（ec2-setup.sh により）
```
/home/{ec2-user|ubuntu}/task/03_PROJECTS/youtube_automation/
├── .env                      # 必須（APIキー等）
├── .env.example              # テンプレート
├── requirements.txt          # Python依存
├── youtube_pipeline.py       # メインスクリプト
├── run_pipeline.sh           # 実行スクリプト
├── ec2-setup.sh              # セットアップ用（EC2内では不要後）
├── out/                      # ログ・出力ファイル
│   ├── pipeline_YYYYMMDD_HHMMSS.log
│   ├── final_YYYYMMDD_HHMMSS.mp4
│   ├── metadata_YYYYMMDD_HHMMSS.json
│   └── thumbnail_YYYYMMDD_HHMMSS.png
└── tmp/                      # 一時ファイル
    └── (moviepy等の中間ファイル)
```

### 統一パス案（推奨）
```
~/youtube_automation/
├── .env
├── requirements.txt
├── youtube_pipeline.py
├── run_pipeline.sh
├── ec2-setup.sh              # 初回セットアップのみ（後で削除可）
├── groq_executor.py          # [将来] Groq処理の独立モジュール
├── token.json                # [将来] YouTube OAuth token
├── config.yaml               # [将来] video_auto_edit との連携用
├── out/
├── tmp/
└── logs/                      # [推奨] ログを別フォルダに集約
    └── pipeline_YYYYMMDD_HHMMSS.log
```

**パス確定の理由**:
- ec2-setup.sh で `$HOME_DIR/task/03_PROJECTS/youtube_automation` にクローン
- run_pipeline.sh で `SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"` により相対パスで動作
- EC2内では絶対パス `/home/{user}/task/03_PROJECTS/youtube_automation/` で固定

---

## (4) batch_produce.sh で set +e が必要な技術的根拠

### set +e が必要なシーン

```bash
# ❌ 現在の run_pipeline.sh: set -e のまま
set -e
...
if python3 youtube_pipeline.py ...; then
    # 成功時処理
else
    # 失敗時処理 ← ここに到達しない（行136の exit 0 or 行145の exit 1）
fi
```

### batch_produce.sh での運用シナリオ
```bash
#!/bin/bash
# 複数案件の youtube_pipeline.sh を連続実行

set +e  # ← エラーで全体停止しない

for channel_id in "$@"; do
    echo "Processing $channel_id..."

    # run_pipeline.sh 実行
    /home/ubuntu/task/03_PROJECTS/youtube_automation/run_pipeline.sh
    result=$?

    if [ $result -ne 0 ]; then
        echo "⚠️ $channel_id failed (code=$result), continuing..."
        # ログ記録 → 次へ進む
    else
        echo "✅ $channel_id success"
    fi
done

# 全体の終了コード（いずれか1つ失敗でも exit 1）
```

### 技術的根拠
1. **スポットインスタンス環境**: 強制終了時の復旧を考慮
   - 1つのチャンネルで失敗 → 他チャンネルは続行すべき
   - 全失敗ログで再実行判断可能にする

2. **部分失敗許容**: 例）Pexels API down でも動画生成スキップ → 次へ
   - youtube_pipeline.py 側で try-except 実装
   - batch_produce.sh は個々の終了コードを監視

3. **監視ログ必須**: 失敗時の詳細は $LOG_FILE に記録
   ```bash
   tail -n 100 /home/ubuntu/task/out/pipeline_*.log
   ```

---

## (5) cron でJST 9:00を指定する場合のUTC変換

### 現在の cron 設定（ec2-setup.sh 行204）
```bash
CRON_JOB="0 6 * * * $HOME_DIR/task/03_PROJECTS/youtube_automation/run_pipeline.sh"
# → 毎日 06:00 UTC に実行
```

### JST 9:00 への変更（推奨）

**Step 1: EC2 インスタンスのタイムゾーン確認**
```bash
$ date +%Z  # UTC なら出力は "UTC"
$ timedatectl status  # systemd が管理している場合
```

**Step 2: JST への変更方法**

**方式A: EC2 のシステムタイムゾーンを JST に変更**
```bash
# Amazon Linux 2
sudo timedatectl set-timezone Asia/Tokyo

# または
sudo ln -sf /usr/share/zoneinfo/Asia/Tokyo /etc/localtime
```
この場合、crontab は「シスレム時刻基準」で動作:
```bash
0 9 * * * /home/ubuntu/task/03_PROJECTS/youtube_automation/run_pipeline.sh
# → 毎日 09:00 JST に実行
```

**方式B: crontab の環境変数で CRON_TZ を指定**
```bash
# .crontab ファイル（または crontab -e）
CRON_TZ=Asia/Tokyo
0 9 * * * /home/ubuntu/task/03_PROJECTS/youtube_automation/run_pipeline.sh
```

**方式C: systemd timer を使用（推奨、モダン）**
```ini
# /etc/systemd/system/youtube-pipeline.timer
[Unit]
Description=YouTube Pipeline Timer (JST 9:00)

[Timer]
OnCalendar=*-*-* 09:00:00 Asia/Tokyo
Unit=youtube-pipeline.service

[Install]
WantedBy=timers.target
```

### 変換ルール（UTC → JST）
```
JST = UTC + 9 時間
∴ JST 9:00 = UTC 0:00
  JST 12:00 = UTC 3:00
  JST 18:00 = UTC 9:00

cron フォーマット: "分 時 日 月 曜日"
∴ JST 9:00 → cron "0 9 * * *"  （ただしシステムが JST の場合）
  または cron "0 0 * * *"       （ UTC 基準で 0:00 = JST 9:00 を実現）
```

**推奨**: **方式A（シスレムタイムゾーン JST 化）** で統一
- run_pipeline.sh 内の `date` コマンドもログが JST になり一貫性あり
- crontab 指定が直感的（"9:00" と書いたら JST 9:00 実行）

---

## (6) WSL上でsshpass + scpを使う際のコマンド書式

### sshpass のインストール（WSL）
```bash
# Ubuntu on WSL
sudo apt update
sudo apt install -y sshpass

# 確認
sshpass -V
```

### SSH 接続情報の前提
```bash
EC2_HOST="ec2-user@{EC2_PUBLIC_IP}"   # Amazon Linux 2
EC2_HOST="ubuntu@{EC2_PUBLIC_IP}"     # Ubuntu
EC2_KEY="/path/to/key.pem"            # プライベートキー
EC2_PASSWORD="xxxxxx"                 # ec2-user のパスワード
```

### sshpass + scp の基本形式

**パターン1: パスワード認証でファイル転送**
```bash
sshpass -p "$EC2_PASSWORD" \
  scp -o StrictHostKeyChecking=no \
      -o UserKnownHostsFile=/dev/null \
      -P 22 \
      local_file.txt \
      ec2-user@{EC2_IP}:~/youtube_automation/
```

**パターン2: キーペア + パスワード（鍵も保護されている場合）**
```bash
# キー認証優先（推奨、more secure）
scp -i "$EC2_KEY" \
    -o StrictHostKeyChecking=no \
    -o UserKnownHostsFile=/dev/null \
    local_file.txt \
    ec2-user@{EC2_IP}:~/youtube_automation/
```

### batch_produce.sh での実装例

```bash
#!/bin/bash

EC2_HOST="ec2-user"  # or "ubuntu"
EC2_IP="203.0.113.45"
EC2_DEST_DIR="~/youtube_automation"

# 転送ファイル一覧
FILES=(
    "youtube_pipeline.py"
    "requirements.txt"
    "run_pipeline.sh"
    ".env"
)

# キー認証で転送
for file in "${FILES[@]}"; do
    echo "Transferring $file..."
    scp -i ~/.ssh/ec2_key.pem \
        -o StrictHostKeyChecking=no \
        ./"$file" \
        "${EC2_HOST}@${EC2_IP}:${EC2_DEST_DIR}/"

    if [ $? -eq 0 ]; then
        echo "✅ $file transferred"
    else
        echo "❌ $file transfer failed"
    fi
done
```

### 推奨事項
```
❌ sshpass の使用は避けるべき（password in plaintext）
✅ SSH キーペア認証を推奨
   → ~/.ssh/config で ホスト登録
   → aws ec2-instance-connect OR SSM Session Manager 活用
```

**セキュア運用例**:
```bash
# ~/.ssh/config に登録
Host youtube-ec2
    HostName {EC2_PUBLIC_IP}
    User ec2-user
    IdentityFile ~/.ssh/ec2_key.pem
    StrictHostKeyChecking no

# 転送コマンド
scp youtube_pipeline.py youtube-ec2:~/youtube_automation/
```

---

## (7) 転送必須ファイル一覧（youtube_pipeline.py, requirements.txt, run_pipeline.sh, ec2-setup.sh, groq_executor.py, token.json, .env）

### 初回セットアップ時（ec2-setup.sh 実行前）
```
WSL ローカル側で準備:
✅ youtube_pipeline.py          → EC2 へ転送
✅ requirements.txt             → EC2 へ転送
✅ run_pipeline.sh              → EC2 へ転送
✅ ec2-setup.sh                 → EC2 へ転送（セットアップ用）
⚠️  .env                        → **手動で EC2 上で作成** (.env.example から)
❌ groq_executor.py             → 現在は youtube_pipeline.py に統合（将来独立予定）
❌ token.json                   → YouTube OAuth は初回実行時に対話で生成
❌ config.yaml                  → video_auto_edit との連携まだ（将来）
```

### セットアップ手順
```bash
# Step 1: 転送対象ファイルをWSLに準備
cd /mnt/c/Users/tshibasaki/Desktop/etc/work/task/03_PROJECTS/youtube_automation

# Step 2: EC2 へ転送
scp -i ~/.ssh/ec2_key.pem \
    youtube_pipeline.py requirements.txt run_pipeline.sh ec2-setup.sh \
    ec2-user@{EC2_IP}:/tmp/

# Step 3: EC2 ログイン＆セットアップ
ssh -i ~/.ssh/ec2_key.pem ec2-user@{EC2_IP}

# Step 4: EC2 上で実行
cd /tmp
bash ec2-setup.sh

# Step 5: .env 編集
nano ~/task/03_PROJECTS/youtube_automation/.env
  GROQ_API_KEY=xxx
  YOUTUBE_API_KEY=xxx
  YOUTUBE_CLIENT_ID=xxx
  YOUTUBE_CLIENT_SECRET=xxx
  PEXELS_API_KEY=xxx
```

### 定期更新時（コード変更がある場合）
```bash
# WSL から差分 scp で更新
scp -i ~/.ssh/ec2_key.pem \
    youtube_pipeline.py run_pipeline.sh \
    ec2-user@{EC2_IP}:~/task/03_PROJECTS/youtube_automation/

# .env は EC2 上で保持（更新対象外）
```

### ファイル一覧（詳細）

| ファイル名 | 必須性 | 保存先 | 説明 |
|-----------|--------|--------|------|
| youtube_pipeline.py | ✅ 必須 | ~/youtube_automation/ | メインパイプライン スクリプト |
| requirements.txt | ✅ 必須 | ~/youtube_automation/ | Python依存パッケージ |
| run_pipeline.sh | ✅ 必須 | ~/youtube_automation/ | Cron 実行スクリプト |
| ec2-setup.sh | ✅ 初回 | /tmp/ （セットアップ後削除可） | OS/依存関係セットアップ |
| .env | ✅ 必須 | ~/youtube_automation/ | APIキー設定（**手動作成**） |
| .env.example | ℹ️ 参考 | ~/youtube_automation/ | .env テンプレート |
| groq_executor.py | ❌ 将来 | 未決定 | Groq 処理の独立モジュール（計画） |
| token.json | ❌ 自動生成 | ~/youtube_automation/ | YouTube OAuth token（初回実行時生成） |
| config.yaml | ❌ 将来 | ~/youtube_automation/ | video_auto_edit 連携設定（計画） |

---

## (8) スポットインスタンス消失を前提とした設計考慮点（データ永続化、再デプロイ容易性）

### スポットインスタンスの課題
```
⚠️  Spot インスタンス = 2分通知で強制終了可能
    ∴ ローカルストレージは失われる（EBS ボリュームも除外時）
    ∴ S3 へのバックアップ必須
```

### データ永続化戦略

**1) ローカル保存（ephemeral storage）**
```
❌ 非推奨: ~/youtube_automation/out/ にのみ保存
   理由: インスタンス消失で全データロス

✅ 推奨: out/ + S3 バックアップの並行
```

**2) S3 バックアップ（run_pipeline.sh 行123-134）**
```bash
if [ ! -z "$AWS_S3_BUCKET" ]; then
    aws s3 sync "$LOG_DIR" "s3://$AWS_S3_BUCKET/youtube_automation/$(date +%Y%m%d)/" \
        --region "$AWS_REGION"
fi
```

**3) .env と token.json の永続化**
```bash
# オプション A: Systems Manager Parameter Store
aws ssm put-parameter --name "/youtube-automation/api-keys" \
    --value "$(cat .env)" --type SecureString

# オプション B: S3 (暗号化)
aws s3 cp .env s3://{bucket}/secrets/.env --sse AES256

# オプション C: Secrets Manager
aws secretsmanager create-secret --name youtube-api-keys \
    --secret-string "$(cat .env)"
```

### 再デプロイ容易性の実装

**1) インフラストラクチャのコード化（IaC）**

**CloudFormation テンプレート例**:
```yaml
# ec2-cloudformation.yaml
AWSTemplateFormatVersion: '2010-09-09'
Resources:
  YouTubeAutomationInstance:
    Type: AWS::EC2::Instance
    Properties:
      ImageId: ami-xxxxxxxx  # Amazon Linux 2 or Ubuntu 22.04
      InstanceType: t4g.medium
      SpotPrice: "0.04"
      UserData:
        Fn::Base64: |
          #!/bin/bash
          set -e

          # S3 から .env を復元
          aws s3 cp s3://youtube-backup/secrets/.env /tmp/.env

          # ec2-setup.sh 実行
          cd /tmp
          aws s3 cp s3://youtube-backup/scripts/ec2-setup.sh .
          bash ec2-setup.sh

          # .env を配置
          mv /tmp/.env ~/task/03_PROJECTS/youtube_automation/.env
```

**2) デプロイスクリプト（bootstrap.sh）**

```bash
#!/bin/bash
# bootstrap.sh: Spot インスタンス起動時の自動デプロイ

set -e

echo "[Bootstrap] Starting..."

# Step 1: S3 から .env と スクリプトを復元
echo "[Bootstrap] Restoring .env from S3..."
mkdir -p ~/youtube_automation
aws s3 cp s3://youtube-backup/secrets/.env ~/youtube_automation/.env
aws s3 cp s3://youtube-backup/scripts/ ~/youtube_automation/ --recursive

# Step 2: 権限設定
chmod +x ~/youtube_automation/ec2-setup.sh
chmod +x ~/youtube_automation/run_pipeline.sh

# Step 3: 初期セットアップ
echo "[Bootstrap] Running ec2-setup.sh..."
bash ~/youtube_automation/ec2-setup.sh

# Step 4: 初回実行テスト
echo "[Bootstrap] Running pipeline test..."
~/youtube_automation/run_pipeline.sh

echo "[Bootstrap] Complete!"
```

**3) ファイル版管理**

```bash
# S3 バックアップの構成
s3://youtube-backup/
├── scripts/
│   ├── youtube_pipeline.py          # 定期更新
│   ├── requirements.txt
│   ├── run_pipeline.sh
│   └── ec2-setup.sh
├── secrets/
│   └── .env                         # 最新版のみ保持（暗号化）
├── outputs/
│   ├── 2026-03-01/
│   │   ├── pipeline_*.log
│   │   ├── final_*.mp4
│   │   └── metadata_*.json
│   └── 2026-03-02/
│       └── ...
└── cache/
    └── venv-backup/                 # [将来] 仮想環境スナップショット
```

### スポットインスタンス消失への耐性チェックリスト

```
✅ コード: github リポジトリに全コード管理
   → git clone で即座に復元可能

✅ 設定: S3 に .env（暗号化）保存
   → Spot 起動時に aws s3 cp で復元

✅ 出力: run_pipeline.sh で S3 sync
   → 毎回実行時に バックアップ

✅ スケジューリング: CloudWatch Events → Lambda → Spot起動 + bootstrap
   → 全自動化で人手なし

✅ ログ: CloudWatch Logs へも転送
   → Spot 消失後もログ確認可能

✅ 再デプロイ: ec2-setup.sh 非冪等チェック
   → 既存ファイルは上書きせず スキップ
```

### 実装例（Lambda からの Spot 起動）

```python
# lambda_start_spot.py: CloudWatch Events で定期実行

import boto3
import json
from datetime import datetime

ec2 = boto3.client('ec2', region_name='ap-northeast-1')

def lambda_handler(event, context):
    # S3 から .env と bootstrap.sh を先読み
    s3_script = f"""
    #!/bin/bash
    set -e
    HOME_DIR="/home/ec2-user"

    # 依存関係インストール
    sudo yum install -y python3 git awscli

    # .env と スクリプト復元
    mkdir -p $HOME_DIR/youtube_automation
    aws s3 cp s3://youtube-backup/secrets/.env $HOME_DIR/youtube_automation/
    aws s3 cp s3://youtube-backup/scripts/ $HOME_DIR/youtube_automation/ --recursive

    # ec2-setup.sh 実行
    chmod +x $HOME_DIR/youtube_automation/ec2-setup.sh
    $HOME_DIR/youtube_automation/ec2-setup.sh
    """

    # Spot インスタンス起動
    response = ec2.run_instances(
        ImageId='ami-xxxxxxxx',  # Amazon Linux 2
        InstanceType='t4g.medium',
        MinCount=1,
        MaxCount=1,
        UserData=s3_script,
        InstanceMarketOptions={
            'MarketType': 'spot',
            'SpotOptions': {
                'MaxPrice': '0.04',
                'SpotInstanceType': 'one-time',
            }
        },
    )

    instance_id = response['Instances'][0]['InstanceId']
    print(f"Spot instance {instance_id} launched")

    return {
        'statusCode': 200,
        'body': json.dumps({'instance_id': instance_id})
    }
```

### まとめ（推奨構成）

```
┌─────────────────────────────────────────────────────────┐
│  WSL ローカル（管理拠点）                                  │
├─────────────────────────────────────────────────────────┤
│  • youtube_pipeline.py, run_pipeline.sh 編集・保存        │
│  • S3 へ週1回 push（git commit + S3 sync）               │
└────────┬────────────────────────────────────────────────┘
         │ git clone / aws s3 cp
         ▼
┌─────────────────────────────────────────────────────────┐
│  S3 バケット（永続化層）                                 │
├─────────────────────────────────────────────────────────┤
│  • scripts/ : github リポジトリと同期                    │
│  • secrets/ : .env 暗号化保存                           │
│  • outputs/ : 動画・ログ・メタデータ 日次保存           │
└────────┬────────────────────────────────────────────────┘
         │ CloudWatch Events（毎日 JST 9:00）
         ▼
┌─────────────────────────────────────────────────────────┐
│  Lambda / Spot EC2                                       │
├─────────────────────────────────────────────────────────┤
│  1. bootstrap.sh 実行                                   │
│  2. run_pipeline.sh 実行（自動実行）                    │
│  3. 出力を S3 sync                                      │
│  4. インスタンス自動シャットダウン（cost 削減）          │
└─────────────────────────────────────────────────────────┘
```

**実装タイムライン**:
- **Phase 1** ✅ 現在: ec2-setup.sh + run_pipeline.sh 動作確認
- **Phase 2** 🔄 : S3 バックアップ統合（run_pipeline.sh に aws s3 sync 追加）
- **Phase 3** 🚀 : CloudFormation + Lambda で全自動化

---

## 参考資料

- **run_pipeline.sh**: `03_PROJECTS/youtube_automation/run_pipeline.sh` L1-147
- **ec2-setup.sh**: `03_PROJECTS/youtube_automation/ec2-setup.sh` L1-283
- **youtube_pipeline.py**: `03_PROJECTS/youtube_automation/youtube_pipeline.py` L1-80
- **CLAUDE.md**: `03_PROJECTS/youtube_automation/CLAUDE.md` （詳細仕様書）
- **requirements.txt**: `03_PROJECTS/youtube_automation/requirements.txt` L1-44

---

## 調査完了日時
2026-03-06 10:15 JST
