# シェルスクリプト3本の設計図 — 構造化文書

## 全体構成

YouTube自動化パイプラインのEC2運用を支える3本のシェルスクリプト。スポットインスタンス消失を前提に、1コマンドで完全復旧できる冪等性と、毎日複数本の動画量産を止めない堅牢性を実装する。

---

## セクション構成

### 1. redeploy_ec2.sh — EC2再デプロイ（1コマンド復旧）

#### 役割
ローカル（WSL）からEC2への全ファイル転送・環境復旧・動作確認を一括実行。スポット消失後、このスクリプト1つで本番環境を再構築可能にする。

#### 変数定義セクション
```bash
# =========== 環境変数（修正必須）===========
EC2_IP="18.183.153.86"              # EC2公開IP
EC2_USER="ec2-user"                 # EC2ユーザー名
EC2_PASS="Welcome1234!"             # パスワード（sshpass用）
EC2_KEY_PATH="~/.ssh/ec2_key.pem"   # [推奨] キーペアパス

# ローカルディレクトリ（ホストマシン側）
LOCAL_DIR="/mnt/c/Users/tshibasaki/Desktop/etc/work/task/03_PROJECTS/youtube_automation"
REMOTE_DIR="/home/ec2-user/youtube_automation"
REMOTE_HOME="/home/ec2-user"

# 転送対象ファイル一覧
TRANSFER_FILES=(
    "youtube_pipeline.py"
    "requirements.txt"
    "run_pipeline.sh"
    ".env"
    "token.json"  # [オプション] OAuth token
    ".env.example"
)

# 動作確認コマンド
TEST_PYTHON_VERSION="python3 --version"
TEST_FFMPEG="ffmpeg -version | head -1"
TEST_VENV="source $REMOTE_HOME/venv/bin/activate && python3 -c 'import sys; print(sys.prefix)'"
```

#### 処理フロー（Pseudocode）
```
┌─ STEP 1: 前提チェック
│  ├─ sshpass がインストール済みか確認（`sshpass -V`）
│  ├─ EC2_IP, EC2_USER が設定されているか確認
│  └─ LOCAL_DIR が存在するか確認
│
├─ STEP 2: EC2への接続確認
│  ├─ sshpass -p "$EC2_PASS" ssh ec2-user@EC2_IP "echo OK"
│  └─ 接続失敗 → exit 1
│
├─ STEP 3: 転送前のクリーンアップ（冪等性確保）
│  └─ sshpass ssh ... "mkdir -p $REMOTE_DIR && rm -f $REMOTE_DIR/{youtube_pipeline.py,requirements.txt,...}"
│
├─ STEP 4: ファイル転送（scp or sshpass + echo）
│  ├─ For Each FILE in TRANSFER_FILES:
│  │  ├─ sshpass -p "$EC2_PASS" scp \
│  │  │    -o StrictHostKeyChecking=no \
│  │  │    -o UserKnownHostsFile=/dev/null \
│  │  │    "$LOCAL_DIR/$FILE" \
│  │  │    ec2-user@"$EC2_IP":"$REMOTE_DIR"/
│  │  └─ If scp failed → log error, continue (非ブロッキング)
│  │
│  └─ After all transfers: confirm all files arrived
│
├─ STEP 5: EC2上での初期化スクリプト実行
│  ├─ sshpass ssh ... "chmod +x $REMOTE_DIR/run_pipeline.sh"
│  └─ sshpass ssh ... "chmod +x $REMOTE_DIR/youtube_pipeline.py"
│
├─ STEP 6: Python仮想環境の構築（初回のみ）
│  ├─ ssh ... "if [ ! -d ~/venv ]; then python3 -m venv ~/venv; fi"
│  └─ ssh ... "source ~/venv/bin/activate && pip install -r $REMOTE_DIR/requirements.txt"
│
├─ STEP 7: VOICEVOX Docker確認
│  ├─ ssh ... "docker ps | grep voicevox"
│  └─ If not running:
│  │  └─ ssh ... "docker start voicevox" (or docker run ...)
│  └─ If docker not installed:
│     └─ log warning, 続行（スクリプト実行時に検出される）
│
├─ STEP 8: 動作確認コマンド実行
│  ├─ Test: Python version check
│  ├─ Test: ffmpeg availability
│  ├─ Test: venv activate & import test
│  └─ All tests passed → success log
│
└─ STEP 9: 完了ログ出力
   └─ echo "[SUCCESS] Redeploy completed at $(date)"
```

#### エラーハンドリング
- 各scp失敗時：エラーメッセージ出力 → 次のファイルへ（set +e 動作）
- 接続失敗：即座に exit 1
- venv作成失敗：exit 1（以後のpip installが実行されない）
- docker not found：warning log → continue（youtube_pipeline.py実行時に検出）

#### 冪等性確保戦略
- 転送前に `rm -f` で既存ファイルを削除
- venv は `if [ ! -d ~/venv ]` で存在確認 → 既存なら スキップ
- docker start は idempotent（既に起動していたらno-op）
- requirements.txt は毎回 pip install（新パッケージ追加時に自動反映）

---

### 2. batch_produce.sh — 量産バッチ実行

#### 役割
EC2上で毎日複数本（3本）の動画を順番に生成・アップロード。1本失敗しても他の動画は継続実行。スポット消失を念頭に、ログ記録で復旧時の再実行判断をサポート。

#### 変数定義セクション
```bash
# =========== バッチ実行設定 ===========
PROJECT_DIR="$HOME/youtube_automation"
LOG_DIR="$PROJECT_DIR/logs"
PIPELINE_SCRIPT="$PROJECT_DIR/run_pipeline.sh"

# ログ出力先（日付ごとのバッチログ）
BATCH_LOG_FILE="$LOG_DIR/batch_$(date +\%Y\%m\%d).log"

# 動画生成間隔（秒）
WAIT_INTERVAL=300  # 5分

# 成功・失敗カウンタ
SUCCESS_COUNT=0
FAIL_COUNT=0
TOTAL_COUNT=0

# 処理対象動画数（推奨3本/日）
VIDEOS_TO_PRODUCE=3
```

#### 処理フロー（Pseudocode）
```
┌─ STEP 1: 前提チェック
│  ├─ $PROJECT_DIR が存在するか確認
│  ├─ $PIPELINE_SCRIPT が実行可能か確認（-x）
│  └─ $LOG_DIR が存在しなければ mkdir -p
│
├─ STEP 2: バッチログ開始
│  ├─ echo "[$(date)] ===== Batch Produce Start =====" >> "$BATCH_LOG_FILE"
│  └─ echo "[INFO] Producing $VIDEOS_TO_PRODUCE videos today"
│
├─ STEP 3: ループ開始（N本の動画を順番に処理）
│  ├─ For i in {1..$VIDEOS_TO_PRODUCE}:
│  │
│  │  A. 個別パイプライン実行
│  │     ├─ set +e  # エラー継続許可
│  │     ├─ $PIPELINE_SCRIPT >> "$BATCH_LOG_FILE" 2>&1
│  │     ├─ result=$?
│  │     └─ set -e  # 本スクリプト全体では厳密に
│  │
│  │  B. 終了コード判定
│  │     ├─ If [ $result -eq 0 ]:
│  │     │  ├─ SUCCESS_COUNT++
│  │     │  └─ echo "[✅ SUCCESS] Video $i completed" >> "$BATCH_LOG_FILE"
│  │     └─ Else:
│  │        ├─ FAIL_COUNT++
│  │        └─ echo "[❌ FAIL] Video $i failed (code=$result)" >> "$BATCH_LOG_FILE"
│  │
│  │  C. TOTAL_COUNT++
│  │
│  │  D. 待機（最後の動画は除く）
│  │     └─ If [ $i -lt $VIDEOS_TO_PRODUCE ]:
│  │        ├─ echo "[WAIT] Sleeping ${WAIT_INTERVAL}s before next video..."
│  │        └─ sleep $WAIT_INTERVAL
│  │
│  └─ End For
│
├─ STEP 4: バッチ完了サマリー
│  ├─ echo ""
│  ├─ echo "[SUMMARY] ====="
│  ├─ echo "  Total:   $TOTAL_COUNT"
│  ├─ echo "  Success: $SUCCESS_COUNT"
│  ├─ echo "  Failed:  $FAIL_COUNT"
│  ├─ echo "[$(date)] Batch Produce End"
│  └─ echo "================================"
│
└─ STEP 5: 終了コード設定
   ├─ If [ $FAIL_COUNT -eq 0 ]:
   │  └─ exit 0  # 全成功
   └─ Else:
      └─ exit 1  # 1つ以上失敗（ただしバッチは全実行完了）
```

#### 300秒wait（5分）の根拠

| 項目 | 推定時間 |
|------|---------|
| Groq API コール（字幕生成） | 30〜60秒 |
| MoviePy編集（映像合成） | 60〜90秒 |
| VOICEVOX音声合成 | 20〜40秒 |
| YouTube API アップロード | 60〜120秒 |
| ネットワーク遅延・API throttling | 20〜30秒 |
| **合計（最大）** | **約300〜400秒** |

→ **300秒（5分）**を採用：次の動画開始時にAPI rate limit回復を確保。Groq/YouTube API の rate limit に余裕を持たせる。

#### ログ出力フォーマット
```
[2026-03-06 09:00:15] ===== Batch Produce Start =====
[INFO] Producing 3 videos today
[2026-03-06 09:00:15] Starting Video 1/3...
[✅ SUCCESS] Video 1 completed (elapsed: 280s)
[WAIT] Sleeping 300s before next video...
[2026-03-06 09:05:20] Starting Video 2/3...
[❌ FAIL] Video 2 failed (code=1)
  └─ Error detail: Groq API down (from pipeline log)
[WAIT] Sleeping 300s before next video...
[2026-03-06 09:10:25] Starting Video 3/3...
[✅ SUCCESS] Video 3 completed (elapsed: 320s)

[SUMMARY] =====
  Total:   3
  Success: 2
  Failed:  1
[2026-03-06 09:15:30] Batch Produce End
================================
Exit Code: 1 (1 failure detected)
```

#### エラーハンドリング
- `set +e`: 個別動画失敗時も他の動画を中断しない
- `result=$?`: 各実行の終了コード を記録
- ログ内に失敗理由を記録（run_pipeline.sh の stderr が自動付与）
- 最終的に失敗が1つでもあれば exit 1 で報告

#### スポット消失時の対応
- 日付ごとのログ（batch_YYYYMMDD.log）で前日の実行状況を確認可能
- 再デプロイ後、前日ログをチェックして「どの動画まで成功したか」を把握
- 必要に応じて失敗分だけ再実行

---

### 3. setup_cron.sh — Cron設定と自動起動

#### 役割
毎日JST 9:00にbatch_produce.shを自動実行。システムタイムゾーン確認→crontab登録→@rebootでVOICEVOX自動起動を実装。再デプロイ後も冪等性を保つため既存エントリを削除してから再追加。

#### 変数定義セクション
```bash
# =========== Cron設定 ===========
HOME_DIR="/home/ec2-user"
PROJECT_DIR="$HOME_DIR/youtube_automation"
BATCH_SCRIPT="$PROJECT_DIR/batch_produce.sh"
LOG_DIR="$PROJECT_DIR/logs"

# システムタイムゾーン設定
TARGET_TZ="Asia/Tokyo"

# Cron設定内容
CRON_SCHEDULE="0 9 * * *"  # JST 9:00（シスレムがJST前提）
CRON_COMMENT="YouTube Automation - Batch Produce"

# VOICEVOX Docker 自動起動
DOCKER_IMAGE="voicevox/voicevox:latest"
VOICEVOX_CONTAINER="voicevox"
VOICEVOX_PORT="50021"
```

#### 処理フロー（Pseudocode）
```
┌─ STEP 1: システムタイムゾーン確認
│  ├─ current_tz=$(timedatectl show --property=Timezone --value)
│  └─ If [ "$current_tz" != "Asia/Tokyo" ]:
│     └─ sudo timedatectl set-timezone Asia/Tokyo
│        ├─ OR sudo ln -sf /usr/share/zoneinfo/Asia/Tokyo /etc/localtime
│        └─ echo "[INFO] Timezone changed to Asia/Tokyo"
│
├─ STEP 2: ログディレクトリ作成（冪等性）
│  ├─ mkdir -p "$LOG_DIR"
│  ├─ chmod 755 "$LOG_DIR"
│  └─ echo "[INFO] Log directory ready: $LOG_DIR"
│
├─ STEP 3: スクリプト実行権限設定
│  ├─ chmod +x "$BATCH_SCRIPT"
│  └─ echo "[INFO] batch_produce.sh is executable"
│
├─ STEP 4: Crontab エントリ削除（既存を削除して冪等性確保）
│  ├─ # 既存の同じコメント付きエントリを削除
│  ├─ crontab -l 2>/dev/null | grep -v "$CRON_COMMENT" | crontab -
│  ├─ OR crontab -e で手動削除（GUI環境の場合）
│  └─ echo "[INFO] Removed old cron entries"
│
├─ STEP 5: Crontab 新規登録
│  ├─ new_cron_entry="0 9 * * * $BATCH_SCRIPT >> $LOG_DIR/cron_execution.log 2>&1"
│  ├─ (crontab -l 2>/dev/null; echo "$new_cron_entry") | crontab -
│  └─ echo "[INFO] Registered new cron: 0 9 * * * (JST 9:00)"
│
├─ STEP 6: @reboot エントリ追加（VOICEVOX自動起動）
│  ├─ voicevox_reboot_entry="@reboot sleep 30 && docker start $VOICEVOX_CONTAINER || docker run -d --name $VOICEVOX_CONTAINER -p $VOICEVOX_PORT:50021 $DOCKER_IMAGE"
│  ├─ (crontab -l 2>/dev/null; echo "$voicevox_reboot_entry") | crontab -
│  └─ echo "[INFO] Registered @reboot entry for VOICEVOX"
│
├─ STEP 7: Crontab確認
│  ├─ echo "[INFO] Current crontab:"
│  ├─ crontab -l
│  └─ Verify both entries are present
│
├─ STEP 8: Docker確認（VOICEVOX が既に起動しているか）
│  ├─ If docker ps | grep -q "$VOICEVOX_CONTAINER":
│  │  └─ echo "[✅] VOICEVOX is already running"
│  └─ Else:
│     ├─ docker start "$VOICEVOX_CONTAINER" 2>/dev/null
│     └─ If [ $? -ne 0 ]:
│        └─ docker run -d --name "$VOICEVOX_CONTAINER" -p "$VOICEVOX_PORT:50021" "$DOCKER_IMAGE"
│           └─ echo "[INFO] VOICEVOX started"
│
└─ STEP 9: 完了ログ
   ├─ echo "[SUCCESS] Cron setup completed"
   ├─ echo "[SUMMARY]"
   ├─ echo "  - Timezone: Asia/Tokyo"
   ├─ echo "  - Batch schedule: 0 9 * * * (JST 9:00)"
   ├─ echo "  - VOICEVOX: $(docker ps --filter name=voicevox --format '{{.Status}}')"
   └─ echo "  - Next batch execution: Tomorrow 09:00"
```

#### Crontab冪等性確保戦略

```bash
# ❌ 非冪等（毎回重複登録される）
(crontab -l 2>/dev/null; echo "0 9 * * * /path/to/batch_produce.sh") | crontab -

# ✅ 冪等（既存エントリを削除してから追加）
crontab -l 2>/dev/null | grep -v "YouTube Automation" | crontab -
(crontab -l 2>/dev/null; echo "0 9 * * * /path/to/batch_produce.sh # YouTube Automation") | crontab -
```

#### 時刻指定の最終決定

| 方式 | コマンド | メリット | デメリット |
|------|---------|---------|-----------|
| **A) システムTZ JST化（推奨）** | `sudo timedatectl set-timezone Asia/Tokyo` + `crontab: 0 9 * * *` | 直感的、ログ時刻も JST | sudo 権限必須 |
| B) CRON_TZ環境変数 | `CRON_TZ=Asia/Tokyo` + `0 9 * * *` | sudo 不要 | cron周辺ツールで非対応の場合あり |
| C) systemd timer | OnCalendar=\*-\*-\* 09:00:00 | モダン、柔軟 | 複雑化（不要） |

**採用**: **方式A**（システムTZ JST化）

---

### 4. 情報の流れ（再デプロイから自動実行までのシーケンス）

#### Phase 0: ローカル準備（手動）
```
WSL ローカル
├─ youtube_automation/ フォルダ確認
├─ redeploy_ec2.sh に EC2_IP, EC2_PASS 記入
└─ redeploy_ec2.sh 実行準備
```

#### Phase 1: EC2環境復旧（redeploy_ec2.sh 実行）
```
$ bash redeploy_ec2.sh

1. 接続確認 → sshpass -p "Welcome1234!" ssh ec2-user@18.183.153.86 "echo OK"
2. ファイル転送 → scp youtube_pipeline.py, requirements.txt, run_pipeline.sh, .env
3. venv構築 → python3 -m venv ~/venv && pip install -r requirements.txt
4. VOICEVOX起動確認 → docker ps | grep voicevox → docker start voicevox
5. 動作確認 → python3 --version, ffmpeg -version, venv activate test
6. 完了ログ → [SUCCESS] Redeploy completed
```

#### Phase 2: Cron設定（setup_cron.sh 実行）
```
$ bash setup_cron.sh

1. システムTZ確認 → Asia/Tokyo に設定
2. ログディレクトリ作成 → ~/youtube_automation/logs/
3. 既存cron削除 → grep -v "YouTube Automation" | crontab -
4. 新規cron登録 → 0 9 * * * /home/ec2-user/youtube_automation/batch_produce.sh
5. @reboot登録 → VOICEVOX自動起動
6. 確認 → crontab -l で両エントリを表示
```

#### Phase 3: 毎日自動実行（cronによる自動起動）
```
[毎日JST 09:00]
  ↓
cron が batch_produce.sh を起動
  ↓
batch_produce.sh (3本の動画)
  ├─ Loop i=1:
  │  ├─ run_pipeline.sh (Video 1)
  │  ├─ ログ記録 (logs/batch_YYYYMMDD.log)
  │  └─ sleep 300s
  ├─ Loop i=2:
  │  ├─ run_pipeline.sh (Video 2)
  │  ├─ ログ記録
  │  └─ sleep 300s
  └─ Loop i=3:
     ├─ run_pipeline.sh (Video 3)
     ├─ ログ記録
     └─ サマリー出力 (Success: 2, Failed: 1)
  ↓
完了ログ → logs/batch_YYYYMMDD.log
```

#### Phase 4: スポット消失後の復旧（自動）
```
[EC2 Spot が消失]
  ↓
[新しい Spot インスタンスが起動]
  ↓
$ bash redeploy_ec2.sh
  (同じコマンド、冪等）
  ↓
$ bash setup_cron.sh
  (同じコマンド、冪等）
  ↓
[翌日 JST 09:00 に自動実行再開]
  ↓
ログをチェック:
  $ tail -f logs/batch_*.log
  前日失敗分の詳細を確認 → 必要に応じて手動実行
```

---

## スクリプト間の依存関係

```
redeploy_ec2.sh
    ↓
    └─→ youtube_pipeline.py
    └─→ run_pipeline.sh
    └─→ requirements.txt
    └─→ .env
    └─→ token.json (Option)
         ↓
         [EC2環境準備完了]
              ↓
setup_cron.sh
    ├─→ /etc/localtime (TZ設定)
    └─→ crontab
         ↓
         [自動実行スケジュール登録]
              ↓
batch_produce.sh (毎日 09:00 自動実行)
    ├─→ run_pipeline.sh (Video 1-N)
    └─→ logs/batch_YYYYMMDD.log
```

---

## チェックリスト（本番環境での実行順序）

### Cron実行前のローカル確認
- [ ] redeploy_ec2.sh に EC2_IP, EC2_USER, EC2_PASS が正しく設定されているか
- [ ] LOCAL_DIR が `C:/Users/tshibasaki/Desktop/etc/work/task/03_PROJECTS/youtube_automation` で正しいか
- [ ] youtube_pipeline.py, requirements.txt, run_pipeline.sh が LOCAL_DIR に存在するか
- [ ] .env が LOCAL_DIR に存在し、APIキーが全て埋まっているか

### redeploy_ec2.sh 実行後の確認
- [ ] SSH接続成功：`sshpass -p "Welcome1234!" ssh ec2-user@18.183.153.86 "echo OK"`
- [ ] ファイル転送成功：`sshpass ssh ec2-user@... "ls -la ~/youtube_automation/"`
- [ ] venv構築：`ssh ... "source ~/venv/bin/activate && python3 -c 'import sys; print(sys.prefix)'"`
- [ ] pip install成功：`ssh ... "pip list | grep groq"`
- [ ] VOICEVOX起動：`ssh ... "docker ps | grep voicevox"`

### setup_cron.sh 実行後の確認
- [ ] TZ設定：`ssh ... "date +%Z"` → Asia/Tokyo が表示されるか
- [ ] logs/ディレクトリ作成：`ssh ... "ls -la ~/youtube_automation/logs/"`
- [ ] Crontab登録：`ssh ... "crontab -l"` → 0 9 * * * が表示されるか
- [ ] @reboot登録：`ssh ... "crontab -l | grep @reboot"`

### 本番運用中の定期確認
- [ ] 日次ログ確認：`tail -n 50 logs/batch_$(date +%Y%m%d).log`
- [ ] パイプラインログ確認：`ls -lt logs/pipeline_*.log | head -5`
- [ ] YouTube動画確認：新規チャンネル上にアップロードされているか
- [ ] スポット消失時：redeploy_ec2.sh + setup_cron.sh を再実行

---

## 疑似コード全体（参考実装例）

### redeploy_ec2.sh
```bash
#!/bin/bash
set -e

# Variables
EC2_IP="18.183.153.86"
EC2_USER="ec2-user"
EC2_PASS="Welcome1234!"
LOCAL_DIR="/mnt/c/Users/tshibasaki/Desktop/etc/work/task/03_PROJECTS/youtube_automation"
REMOTE_DIR="/home/ec2-user/youtube_automation"

# Check sshpass
sshpass -V || { echo "sshpass not installed"; exit 1; }

# Check connection
sshpass -p "$EC2_PASS" ssh ec2-user@"$EC2_IP" "echo OK" || exit 1

# Transfer files
for file in youtube_pipeline.py requirements.txt run_pipeline.sh .env token.json; do
    sshpass -p "$EC2_PASS" scp \
        -o StrictHostKeyChecking=no \
        -o UserKnownHostsFile=/dev/null \
        "$LOCAL_DIR/$file" \
        ec2-user@"$EC2_IP":"$REMOTE_DIR"/ || echo "⚠️ $file transfer failed"
done

# Setup venv
sshpass -p "$EC2_PASS" ssh ec2-user@"$EC2_IP" \
    "python3 -m venv ~/venv && source ~/venv/bin/activate && pip install -r $REMOTE_DIR/requirements.txt"

# Check VOICEVOX
sshpass -p "$EC2_PASS" ssh ec2-user@"$EC2_IP" \
    "docker ps | grep voicevox || docker start voicevox"

# Tests
sshpass -p "$EC2_PASS" ssh ec2-user@"$EC2_IP" "python3 --version"
sshpass -p "$EC2_PASS" ssh ec2-user@"$EC2_IP" "ffmpeg -version | head -1"

echo "[SUCCESS] Redeploy completed at $(date)"
```

### batch_produce.sh
```bash
#!/bin/bash

PROJECT_DIR="$HOME/youtube_automation"
PIPELINE_SCRIPT="$PROJECT_DIR/run_pipeline.sh"
LOG_DIR="$PROJECT_DIR/logs"
BATCH_LOG_FILE="$LOG_DIR/batch_$(date +%Y%m%d).log"

mkdir -p "$LOG_DIR"

echo "[$(date)] ===== Batch Produce Start =====" >> "$BATCH_LOG_FILE"

SUCCESS_COUNT=0
FAIL_COUNT=0

for i in {1..3}; do
    echo "[INFO] Video $i/3..."

    set +e
    "$PIPELINE_SCRIPT" >> "$BATCH_LOG_FILE" 2>&1
    result=$?
    set -e

    if [ $result -eq 0 ]; then
        ((SUCCESS_COUNT++))
        echo "[✅] Video $i success" >> "$BATCH_LOG_FILE"
    else
        ((FAIL_COUNT++))
        echo "[❌] Video $i failed (code=$result)" >> "$BATCH_LOG_FILE"
    fi

    if [ $i -lt 3 ]; then
        sleep 300
    fi
done

echo "[SUMMARY] Success: $SUCCESS_COUNT, Failed: $FAIL_COUNT" >> "$BATCH_LOG_FILE"
echo "[$(date)] ===== Batch Produce End =====" >> "$BATCH_LOG_FILE"

[ $FAIL_COUNT -eq 0 ] && exit 0 || exit 1
```

### setup_cron.sh
```bash
#!/bin/bash

HOME_DIR="/home/ec2-user"
PROJECT_DIR="$HOME_DIR/youtube_automation"
BATCH_SCRIPT="$PROJECT_DIR/batch_produce.sh"
LOG_DIR="$PROJECT_DIR/logs"

# Set timezone
sudo timedatectl set-timezone Asia/Tokyo

# Create log directory
mkdir -p "$LOG_DIR"
chmod 755 "$LOG_DIR"

# Make scripts executable
chmod +x "$BATCH_SCRIPT"

# Remove old cron entries
crontab -l 2>/dev/null | grep -v "YouTube Automation" | crontab - || true

# Register new cron
(crontab -l 2>/dev/null; echo "0 9 * * * $BATCH_SCRIPT >> $LOG_DIR/cron_execution.log 2>&1 # YouTube Automation") | crontab -

# Register @reboot for VOICEVOX
(crontab -l 2>/dev/null; echo "@reboot sleep 30 && docker start voicevox || docker run -d --name voicevox -p 50021:50021 voicevox/voicevox:latest") | crontab -

# Start VOICEVOX
docker start voicevox || docker run -d --name voicevox -p 50021:50021 voicevox/voicevox:latest

echo "[SUCCESS] Cron setup completed"
crontab -l
```

---

## 注釈

[推測] スポット消失後の完全復旧が1コマンド（redeploy_ec2.sh）で実現可能な理由：
- EC2上のファイル全てが remote_dir に統一
- 仮想環境の再構築を含むため、古いパッケージキャッシュの影響なし
- token.json は S3 永続化を前提（別タスク）

300秒waitの根拠は調査結果の表に基づき、API rate limit 回復時間+マージン

---

## 構造化完了

3本のシェルスクリプトは以下の原則で設計：
1. **冪等性**: 再実行時に重複登録や上書きエラーが発生しない
2. **スポット耐性**: 1コマンド（redeploy_ec2.sh）で環境全復旧
3. **堅牢バッチ**: 1本失敗しても他の3本は継続（set +e）
4. **監視ログ**: 日付ごとのバッチログで障害追跡可能
5. **自動化完成**: redeploy_ec2.sh + setup_cron.sh で翌日から自動実行再開

