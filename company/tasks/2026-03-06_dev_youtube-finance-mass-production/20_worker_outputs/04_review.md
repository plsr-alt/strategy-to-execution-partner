# シェルスクリプト統合レビュー

## 総合評価
**NG（修正必須）**

---

## 指摘事項

| # | 問題点 | 重要度 | 該当箇所 | 改善提案 |
|---|--------|--------|---------|---------|
| 1 | **set -e / set +e の混在 — エラーハンドリング不完全** | 高 | batch_produce.sh L110-113 | `set +e` の直後に `bash "$PIPELINE_SCRIPT"` を実行すると、run_pipeline.sh の `set -e` で異常終了してもbatch_produce.sh が続行。正しくは：`bash "$PIPELINE_SCRIPT"` の後、その直後のみ `set -e` を戻す。現在は同じ `set +e` が2行ある（L110, L113）。L113を削除し、`RESULT=$?` 後すぐ `set -e` に戻すべき。 |
| 2 | **redeploy_ec2.sh の sshpass 文法エラー** | 高 | redeploy_ec2.sh L218-220 | heredoc 内の `EOF` がシングルクォートで保護されているため、`$(cat "$LOCAL_DIR/.env")` が展開されない。結果：空の .env が転送される。修正：`'EOF'` → `EOF` に変更。または別手段で内容を展開。 |
| 3 | **WSL vs Linux パス混在** | 高 | redeploy_ec2.sh L53 | LOCAL_DIR が WSL パス（`/mnt/c/...`）で定義されているが、TRANSFER_FILES 処理で `"$LOCAL_DIR/$file"` を参照する際、Bash の相対パス解決がぶれる可能性あり。テスト必須。また、run_pipeline.sh から呼ばれた際の PROJECT_DIR が batch_produce.sh と異なる可能性（別途指摘参照）。 |
| 4 | **Cron UTC/JST 変換の根拠が曖昧** | 中 | setup_cron.sh L39-40 | コメントに「UTC 0:00 = JST 9:00」と記載。ただし、実際の EC2 インスタンスの TZ 設定確認が redeploy_ec2.sh に無い。`timedatectl show` で確認すべき。現在 setup_cron.sh は TZ 設定を行わない → **インスタンスの TZ がデフォルト UTC でない場合、実行時刻が狂う**。 |
| 5 | **転送ファイル漏れ検出** | 中 | redeploy_ec2.sh L59-67 | TRANSFER_FILES に `.env` が含まれていないが、後段 L198 以降で特別処理。ただし、`groq_executor.py` がファイル一覧にあるのに、実際に youtube_automation/ ディレクトリに存在しているかローカルチェック時に見つからない場合、ログだけで続行。テスト環境では実在を確認済みか不明。 |
| 6 | **VOICEVOX 確認コマンド の信頼度** | 中 | redeploy_ec2.sh L305 | `docker ps --filter 'name=voicevox' --format '{{.State}}'` で `"running"` を検出。ただし、docker ps の `{{.State}}` フィールドは正確には `State.Running` 等の構造体。正しくは `--format '{{.State.Running}}'` or `docker inspect` で確認すべき。 |
| 7 | **ログディレクトリ事前作成の漏れ** | 中 | redeploy_ec2.sh + run_pipeline.sh | redeploy_ec2.sh L243 で `/logs` `/out` `/tmp` を作成するが、その後の個別スクリプト実行時に mkdir -p が再度実行される。冪等性は満たすが、setup_cron.sh L20 で `mkdir -p "$LOG_DIR"` が実行済み状態を想定。問題なし。ただし、batch_produce.sh L67 で `mkdir -p "$LOG_DIR"` を**スクリプト開始時**に実行すべき（現在はログ出力前）。 |
| 8 | **Cron 冪等性検証** | 高 | setup_cron.sh L28-50 | L30-31 で既存エントリを grep で除外した後、L46-50 で新規エントリを追加。ただし、**複数回実行すると重複する**。正しい流れ：(a) 既存 crontab 読込 → (b) 該当行削除 → **(c) 新規行追加 → (d) 重複排除** が必要。現在は (a)-(b) のみ実行し、直後に新規行を追加 → 次回実行時に重複。修正：`echo "$EXISTING" | sort | uniq` or `grep -F` での文字列比較を厳密に。 |
| 9 | **batch_produce.sh の成功/失敗カウント の正確性** | 中 | batch_produce.sh L116-122 | `if [ $RESULT -eq 0 ]` の判定は正しいが、run_pipeline.sh が `exit 0` / `exit 1` で確実に終了するか確認が必要。run_pipeline.sh L136, L145 で明示的に exit を呼ぶため問題なし。ただし、「失敗数ゼロ = 成功」の判定に `$FAIL_COUNT -eq 0` （L172）を使っているので、部分成功時（5本中2本失敗）の exit 1 が正しく働く。問題なし。 |
| 10 | **スポット消失対応の冪等性** | 高 | redeploy_ec2.sh | 新 IP を引数で受け取る仕様（L47）は OK。ただし、**既にファイルが転送済みの状態で再実行した場合**、L151 で `rm -f` で古いファイルを削除 → 再転送となる。冪等性は満たす。**ただし、crontab は再登録されない**。`setup_cron.sh` を再実行する必要がある。説明文 L381-385 で言及あり（手動実行）。自動化が不十分。 |
| 11 | **run_pipeline.sh の SCRIPT_DIR 解決と batch_produce.sh の呼び出し整合** | 高 | batch_produce.sh L111 vs run_pipeline.sh L29 | batch_produce.sh で `SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"` （L44）を解決 → `PIPELINE_SCRIPT="$SCRIPT_DIR/run_pipeline.sh"` （L47）。run_pipeline.sh では `SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"` （L29）で同じように解決。**ただし、batch_produce.sh から bash "$PIPELINE_SCRIPT" で実行した場合、run_pipeline.sh 内の `$BASH_SOURCE[0]` は `run_pipeline.sh` を指すため、PROJECT_DIR は正しく解決される**。問題なし。ただし、**symlink の場合は異なる可能性あり**。テスト必須。 |
| 11b | **確認コマンド実行時の所有権・パス** | 中 | batch_produce.sh L111 | `bash "$PIPELINE_SCRIPT" >> "$LOG_FILE" 2>&1` で実行。ただし、EC2 では cron が ec2-user で実行されるため、`$SCRIPT_DIR` が `~ec2-user/youtube_automation` を指す。Windows から redeploy_ec2.sh で転送した際、ファイルの所有権が root になる可能性。redeploy_ec2.sh L259 で `chmod +x` を実行済みだが、所有権は確認していない。冪等性・セキュリティ観点から問題。 |
| 12 | **.env 転送の複雑性と例外処理** | 高 | redeploy_ec2.sh L196-229 | `.env` が見つからない場合の処理が甘い。L228 で警告を出すのみ。ただし、run_pipeline.sh L64-68 で `.env` 未検出時に明示的に exit 1 を呼ぶため、パイプラインは起動しない。**問題：redeploy_ec2.sh が完了した直後、手動で `.env` を転送する手順が明確でない**。説明文 L381-382 に記載あるが、自動化が不十分。L198 の条件を `[ ! -f "$LOCAL_DIR/.env" ] && { log_error "..."; exit 1; }` に変更し、デプロイ失敗とすべき。 |

---

## 良い点

- **redeploy_ec2.sh の冪等性確保**: L142-152 で既存ファイルをクリーンアップしてから再転送 → 複数回実行時の重複を回避。
- **エラーログ活用**: 4スクリプト共に色付けログ・タイムスタンプを出力 → 問題追跡が容易。
- **前提条件チェック**: redeploy_ec2.sh L83-116 で sshpass, EC2_IP, ローカルファイル を事前確認。デプロイ時の失敗を事前防止。
- **パイプライン分割の設計**: batch_produce.sh が run_pipeline.sh を個別呼び出し → 失敗時も次ループへ進む。API rate limit 対策（L53 の 300秒待機）も工夫。
- **VOICEVOX 再起動ロジック**: L314-318 で既存コンテナ起動 or 新規作成を分岐 → スポット再起動時の復旧が効率的。

---

## 改善必須事項（リリース前に対応必要）

### 1. **batch_produce.sh の set -e / set +e 修正** （高）
**現在:**
```bash
set +e
bash "$PIPELINE_SCRIPT" >> "$LOG_FILE" 2>&1
RESULT=$?
set +e  # ← 重複。2度目の set +e は不要
```

**修正案:**
```bash
set +e
bash "$PIPELINE_SCRIPT" >> "$LOG_FILE" 2>&1
RESULT=$?
set -e  # ← set -e に戻す
```

理由: run_pipeline.sh が `set -e` で定義されているため、途中で異常終了しても batch_produce.sh が `set +e` のままだと、次ループで不正な状態で実行される可能性。正しくはループ後に `set -e` を戻して、スクリプト全体のエラーハンドリングを統一。

---

### 2. **redeploy_ec2.sh の .env 転送（heredoc）修正** （高）
**現在:**
```bash
sshpass -p "$EC2_PASS" ssh ... \
    "cat > $REMOTE_DIR/.env << 'EOF'
$(cat "$LOCAL_DIR/.env")
EOF"
```

**問題:** `'EOF'` でシングルクォート保護されているため、`$(cat ...)` が展開されない → 空ファイルが生成。

**修正案:**
```bash
sshpass -p "$EC2_PASS" ssh \
    -o StrictHostKeyChecking=no \
    -o UserKnownHostsFile=/dev/null \
    "$EC2_USER@$EC2_IP" \
    "cat > $REMOTE_DIR/.env << 'EOF'
$(cat "$LOCAL_DIR/.env")
EOF"
```

または、別案：
```bash
# ローカルファイルの内容を cat → ssh経由でリダイレクト
cat "$LOCAL_DIR/.env" | sshpass -p "$EC2_PASS" ssh ... "cat > $REMOTE_DIR/.env"
```

理由: scp が失敗した場合の フォールバック処理が機能していない可能性 → 手動で .env を再転送する手間が増える。

---

### 3. **setup_cron.sh の冪等性強化** （高）
**現在:**
```bash
EXISTING=$(crontab -l 2>/dev/null || echo "")
echo "$EXISTING" | grep -v "batch_produce.sh" | grep -v "docker start voicevox" | crontab - 2>/dev/null || true

# ... 後で新規エントリ追加
{
    echo "$EXISTING"  # ← EXISTING は既に grep で処理済みのはず。順序がおかしい
    echo "$BATCH_ENTRY"
    echo "$VOICEVOX_ENTRY"
} | crontab -
```

**問題:**
- L30-31 で `EXISTING` を grep で処理してから crontab - で書き込み
- L37 で `EXISTING` を再度取得（新しいcrontab内容を読み直す必要がある）
- L47 で古い `EXISTING`（grep処理前）を使用 → 重複の可能性

**修正案:**
```bash
# 既存 crontab から対象行を除外
EXISTING=$(crontab -l 2>/dev/null | grep -v "batch_produce.sh" | grep -v "docker start voicevox" || echo "")

# 新規エントリを追加
BATCH_ENTRY="0 0 * * * /bin/bash ${BATCH_SCRIPT} >> ${LOG_DIR}/batch_\$(date +\%Y-\%m-\%d).log 2>&1"
VOICEVOX_ENTRY="@reboot sudo docker start voicevox >> ${LOG_DIR}/voicevox_boot.log 2>&1"

# 重複排除を含めて crontab に書き込み
{
    echo "$EXISTING"
    echo "$BATCH_ENTRY"
    echo "$VOICEVOX_ENTRY"
} | sort | uniq | crontab -
```

理由: 複数回実行時に同じエントリが重複して登録される → cron 実行数が増加 → サーバー負荷・ログ肥大化。

---

### 4. **setup_cron.sh での TZ（タイムゾーン）設定追加** （中→高）
**現在:** setup_cron.sh で TZ 設定が無い。EC2 の デフォルト TZ が UTC でない場合、Cron 実行時刻がずれる。

**修正案:**
redeploy_ec2.sh の STEP 5（リモート初期化）に以下を追加:
```bash
sshpass -p "$EC2_PASS" ssh ... \
    "sudo timedatectl set-timezone Asia/Tokyo"
```

setup_cron.sh にも確認コマンドを追加:
```bash
echo "[INFO] Current timezone:"
timedatectl show-timesync
# 出力例: Timezone=Asia/Tokyo
```

理由: JST 9:00 の指定が UTC 0:00 に対応するには、EC2 インスタンスの TZ が Asia/Tokyo に設定されている必要。デフォルト UTC のまま放置すると、Cron は UTC 基準で動作 → 9時間の遅延。

---

### 5. **redeploy_ec2.sh の .env 転送を強制化** （中→高）
**現在:** L228 で `.env` が見つからない場合は警告のみ。run_pipeline.sh で実行時にエラー終了。

**修正案:**
```bash
if [ ! -f "$LOCAL_DIR/.env" ]; then
    log_error ".env ファイルが見つかりません: $LOCAL_DIR/.env"
    log_error "以下を実行してください: cp .env.example .env && 編集"
    exit 1  # ← デプロイを失敗させる
fi
```

理由: パイプライン起動時のエラーを事前に防止。デプロイ直後に手動で .env を転送する手間を削減。

---

### 6. **VOICEVOX 確認コマンドの正確性修正** （中）
**現在:**
```bash
VOICEVOX_STATUS=$(sshpass -p "$EC2_PASS" ssh ... \
    "docker ps --filter 'name=voicevox' --format '{{.State}}' 2>/dev/null || echo 'not_found'" \
    2>/dev/null)

if [ "$VOICEVOX_STATUS" = "running" ]; then
```

**問題:** `docker ps` の `{{.State}}` フォーマットプレースホルダーは正確には構造体。単純な "running" 文字列比較では失敗する可能性。

**修正案:**
```bash
VOICEVOX_STATUS=$(sshpass -p "$EC2_PASS" ssh ... \
    "docker ps --filter 'name=voicevox' --format 'table {{.State}}' 2>/dev/null | tail -1 || echo 'not_found'" \
    2>/dev/null)

if [ "$VOICEVOX_STATUS" = "running" ]; then
```

または、docker inspect を使用:
```bash
VOICEVOX_STATUS=$(sshpass -p "$EC2_PASS" ssh ... \
    "docker inspect voicevox --format '{{.State.Running}}' 2>/dev/null || echo 'false'" \
    2>/dev/null)

if [ "$VOICEVOX_STATUS" = "true" ]; then
```

理由: `docker ps` の出力フォーマットが環境・バージョンで異なる可能性あり。inspect を使うことで状態を確実に判定。

---

### 7. **batch_produce.sh のログ出力タイミング** （低→中）
**現在:** L67 で `mkdir -p "$LOG_DIR"` を実行。ただし、L26 の `log_info` 関数が `tee -a "$LOG_FILE"` で出力するため、L66 時点で $LOG_FILE が未定義。

**実装は正しい**（L46 で `LOG_FILE` を定義し、L67 で mkdir-p を実行してから L69 で log_info を呼ぶため問題なし）。

---

### 8. **redeploy_ec2.sh の所有権・パーミッション** （中）
**現在:** L259 で `chmod +x` を実行。ただし、**ファイル所有権が root になると ec2-user が編集・実行時に権限不足になる**可能性。

**修正案:**
```bash
sshpass -p "$EC2_PASS" ssh ... \
    "$EC2_USER@$EC2_IP" \
    "chmod +x $REMOTE_DIR/youtube_pipeline.py $REMOTE_DIR/run_pipeline.sh $REMOTE_DIR/batch_produce.sh $REMOTE_DIR/setup_cron.sh && \
     chown ec2-user:ec2-user $REMOTE_DIR/*"  # ← 所有権も ec2-user に変更
```

理由: scp で転送したファイルが root 所有になると、cron (ec2-user 実行) で実行権限エラーが発生する可能性。

---

### 9. **run_pipeline.sh の symlink 対応** （低）
**現在:** L29 で `SCRIPT_DIR="$(cd ... pwd)"` で解決。symlink の場合、`readlink -f` で実パスを取得すべき。

**修正案:**
```bash
# Symlink も含めて実パスを取得
SCRIPT_DIR="$(cd "$(dirname "$(readlink -f "${BASH_SOURCE[0]}")")" && pwd)"
```

理由: スポット再起動時に symlink で run_pipeline.sh を指す場合、PROJECT_DIR がずれる可能性回避。

---

### 10. **スポット消失時の自動復旧フロー** （中→高）
**現在:** redeploy_ec2.sh で新 IP を指定して再実行 → ファイル転送。ただし、**crontab の再登録は手動**（説明文 L385 参照）。

**改善案:**
```bash
# redeploy_ec2.sh 完了後、自動で setup_cron.sh を実行
sshpass -p "$EC2_PASS" ssh \
    -o StrictHostKeyChecking=no \
    -o UserKnownHostsFile=/dev/null \
    "$EC2_USER@$EC2_IP" \
    "bash $REMOTE_DIR/setup_cron.sh" \
    >> "$LOG_FILE" 2>&1 || log_warn "Cron setup failed - run manually"
```

理由: スポット消失から復旧まで完全自動化 → 運用負荷軽減。手動実行依存度を低減。

---

## 検査結果

### チェックリスト対応表

| # | チェック項目 | 結果 | 詳細 |
|---|-------------|------|------|
| 1 | run_pipeline.sh との set -e 整合 | NG | batch_produce.sh L113 が `set +e` で重複（訂正: L113を削除or L113を `set -e` に変更） |
| 2 | WSL/Linux パス混在 | OK | LOCAL_DIR は WSL パス、EC2上は Linux パスで分離。ただ SCRIPT_DIR解決は問題なし |
| 3 | sshpass -o StrictHostKeyChecking 位置 | OK | 正しく `-o` フラグの直後に指定 |
| 4 | Cron UTC/JST 変換 | NG | setup_cron.sh で TZ 設定がない。redeploy_ec2.sh で `timedatectl set-timezone Asia/Tokyo` を追加必須 |
| 5 | 転送ファイル漏れ | OK | 一覧は完全。ただし .env は特別処理で対応 |
| 6 | VOICEVOX 確認 | NG | `docker ps` のフォーマットプレースホルダー使い方が不正確。`docker inspect` で修正推奨 |
| 7 | ログディレクトリ事前作成 | OK | batch_produce.sh L67、run_pipeline.sh L35-36、setup_cron.sh L20 で mkdirを実行。冪等性OK |
| 8 | Cron 冪等性 | NG | 重複追加される。`sort \| uniq` を追加必須 |
| 9 | 成功/失敗カウント | OK | 終了コード判定は正確 |
| 10 | スポット消失対応 | NG | crontab 再登録が手動。自動化推奨 |
| 11 | run_pipeline.sh SCRIPT_DIR解決 | OK | batch_produce.sh から呼ばれても正しく解決。ただし symlink対応は微弱 |
| 12 | .env 転送 | NG | (1) heredoc の `'EOF'` が内容を展開せず、(2) 見つからない場合デプロイ続行 |

---

## 総合診断

**3つの Critical Bug:**
1. batch_produce.sh: `set -e` 復帰忘れ → エラー伝播失敗
2. redeploy_ec2.sh: heredoc 内の .env が空になる → パイプライン起動失敗
3. setup_cron.sh: Cron 重複登録 → 1日に複数実行

**2つの Medium Risk:**
4. TZ 未設定 → Cron 時刻ズレ
5. VOICEVOX 状態判定が不正確 → 起動スキップの誤検出

**推奨**: 上記 5点を修正してから本番デプロイ。テスト環境で cron 実行・ファイル転送・スポット再起動シミュレーションを実施。

---

## 次アクション

1. **04_review_fixes.md** を別途作成し、各修正コード スニペット を提供
2. **テストチェックリスト** を作成（cron重複判定、.env確認、スポット再起動シミュレーション）
3. **デプロイ手順書** を更新（TZ設定・manual手順→自動化）
