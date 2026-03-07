# 抽出データ — AI Shorts Factory

## 抽出元
- `03_PROJECTS/ai_shorts_factory/SPEC.md` (v1.1, 2026-03-07)
- `03_PROJECTS/ai_shorts_factory/TODO.md` (2026-03-07)
- `02_STRATEGY/2026-03-08_4PJ_integration_strategy.md`
- `04_RESEARCH/2026-03-07_ai_video_generation_free_tools.md`

---

## 抽出結果

### (A) ブランド定義

| # | 項目 | 値 | 抽出元 |
|---|------|---|--------|
| 1 | コンセプト | AIアート×自動量産×3プラットフォーム同時展開（YouTube Shorts / Instagram Reels / TikTok） | SPEC.md §1 |
| 2 | 目的 | 既存YouTubeパイプライン資産を活用し、ショート動画（15-60秒）を自動量産し、リーチ最大化と収入源多角化を実現 | SPEC.md §1 |
| 3 | 差別化ポイント | 無料ツール構成（FLUX.2[klein]+FFmpeg+直接API）で¥0/月運用。X API有料化（2026/2/7〜）を除外、3PF同時投稿 | SPEC.md §6.1, TODO.md P0-3 |
| 4 | NGトーン | 実在人物の顔生成NG、リンク誘導スパム（月3本以下抑制）、著作権侵害 | SPEC.md §5.2 |
| 5 | ステータス | 仕様確定・実行フェーズへ | SPEC.md, 統合戦略 |

---

### (B) ターゲットペルソナ

| # | 項目 | 値 | 抽出元 |
|---|------|---|--------|
| 1 | PF別ターゲット | YouTube: 金融/AI学習者、Instagram: ビジュアル重視、TikTok: トレンド感度高い若年層 | SPEC.md §3.1 |
| 2 | 心理 | AI生成画像への興味、自動化・効率化への期待 | 推測・SPEC.md コンテンツテンプレート |
| 3 | 行動 | ショート動画視聴→フォロー→コメント→説明欄リンククリック | SPEC.md §2 |
| 4 | 痛点 | 長尺動画は視聴時間がない、AIアートの学習情報が散在 | 推測・SPEC.md テンプレート設計 |
| 5 | 購買動機 | [推測] 無料視聴で信頼構築→デジタル販売（BOOTH等）への流入想定 | 統合戦略§5, デジタル販売連携 |

---

### (C) ファネル設計

| # | 項目 | 値 | 抽出元 |
|---|------|---|--------|
| 1 | Awareness (視聴) | YouTube Shorts / Instagram Reels / TikTok へ毎日2-3本投稿 | SPEC.md §1, TODO.md Phase 3 |
| 2 | Interest (フォロー) | キャプション＋ハッシュタグで#AIアート#FLUX認知 | SPEC.md §5.3 |
| 3 | Consideration (エンゲージメント) | コメント＋いいね＋保存（Instagramは保存数重視） | SPEC.md §4.2 Step 6 |
| 4 | Conversion (YouTube流入) | 説明欄リンク（外部リンク最大1個）で既存YouTubeチャネルへ | SPEC.md §5.3 YouTube Shorts |
| 5 | Monetization (収益化) | YouTube Partner Program + Instagram バッジ制度 + TikTok Creator Fund | [推測] SPEC.md §6.3 収入試算 |

---

### (D) KPI・撤退基準・改善レバー

| # | 項目 | 値 | 抽出元 |
|---|------|---|--------|
| 1 | KPI: 1ヶ月目 | 本数: 60本 / 日: 2本 / 想定月収: 0-1万 / API月額: ¥0 | SPEC.md §1 投資効果表 |
| 2 | KPI: 3ヶ月目 | 本数: 90本 / 日: 3本 / 想定月収: 1-3万 / API月額: ¥0 | SPEC.md §1 投資効果表 |
| 3 | KPI: 6ヶ月目 | 本数: 90本 / 日: 3本 / 想定月収: 5-15万 / API月額: ¥0 | SPEC.md §1 投資効果表 |
| 4 | KPI: 12ヶ月目 | 本数: 90本 / 日: 3本 / 想定月収: 10-30万 / API月額: ¥0 | SPEC.md §1 投資効果表 |
| 5 | Phase 2 GO判定条件 | AVG_VIEWS ≥ 500 / AVG_ENG_RATE ≥ 2% / エラー率 < 5% / 規約違反 0件 | TODO.md P2W2-3 |
| 6 | Phase 2 撤退条件（NO-GO） | 上記複数項目未達で改善困難 | TODO.md P2W2-3 |
| 7 | 改善レバー1 (Phase 2) | 長さ: 15秒 vs 30秒 vs 45秒 / BGMテンポ: upbeat vs calm / キャプション長 | TODO.md P2W1-2 A/Bテスト |
| 8 | 改善レバー2 (Phase 3) | テーマ別AVG_VIEWSランキング → 低パフォーマンステーマの改善 / 高パフォーマンステーマの拡大 | TODO.md P3-4 |
| 9 | 撤退基準（予測） | [推測] 3ヶ月経過時点でAVG_VIEWS < 200、エラー率 > 15%、技術的に再現困難な場合 | 推測・SPEC.md §7.2ビジネスリスク |

---

### (E) 既存コンテンツ資産

| # | 項目 | 値 | 抽出元 |
|---|------|---|--------|
| 1 | テンプレート1 | 「AIが描く○○」シリーズ（8-12秒、画像3→動画化） | SPEC.md §3.3 |
| 2 | テンプレート2 | ビフォーアフター系（10-15秒、変換過程を可視化） | SPEC.md §3.3 |
| 3 | テンプレート3 | AIアート制作過程（20-30秒、プロンプト表示＋中間ステップ） | SPEC.md §3.3 |
| 4 | テンプレート4 | 金融ワンポイント（15-20秒、既存CHとの連携） | SPEC.md §3.3 |
| 5 | 既存YouTube動画 | [推測] youtube_pipeline.py から既存長尺動画をショート化できる可能性 | TODO.md P0-6, SPEC.md §1 |
| 6 | BGM資産 | Pixabay（無料・商用OK）+ YouTube Audio Library（無料・ライセンス確認推奨） | SPEC.md §4.1, TODO.md P0-5 |
| 7 | 既存パイプライン再利用 | moviepy + Groq API + EC2環境の既存実装流用可能 | TODO.md P0-6 |

---

### (F) 制約条件の影響範囲

| # | 項目 | 値 | 影響 | 抽出元 |
|---|------|---|------|--------|
| 1 | 予算制約 | ¥0/月（API・ツール費無料構成） | ツール選定を無料OSS／直接API に限定。VRAM 6-12GB以上の GPU環境必須 | SPEC.md §6.1, 統合戦略 |
| 2 | 1人運用 | Claude Code が全フェーズ実装・運用 | 自動化・スケジューラー化が必須。部分失敗許容度が低い | CLAUDE.md ルール6 |
| 3 | X API有料化 | 2026/2/7〜完全有料化のため除外 | X投稿不可。YouTube / Instagram / Pinterest のみ | SPEC.md §4.1, TODO.md P0-3 |
| 4 | GCS/ストレージ | ¥100/月（30日自動削除） | ローカルバックアップ併用（7日分保持） | SPEC.md §6.1, TODO.md P1W2-4 |
| 5 | API レート制限 | YouTube: 10,000ユニット/日 / Instagram: 1日3本 / TikTok: 1日1本 | MAX_PARALLEL_JOBS = 3 で制限対応。投稿間隔 2-12時間以上 | SPEC.md §5.1 |
| 6 | ComfyUI VRAM | FLUX.2[klein] 6-12GB必須、Wan 2.1 は 8GB必須 | 低VRAM環境ではフォールバック（Bing Image Creator / AnimateDiff）必須 | SPEC.md §2, TODO.md P0-1, P0-2 |
| 7 | EC2リソース共用 | youtube_pipeline と共用（t4g.medium） | CPU 80% 以下、メモリ 2GB/プロセス制限 | SPEC.md §6.1, TODO.md P1W2-6 |

---

### (G) ツールアセットの活用可能性

| # | ツール | 機能 | ライセンス | 活用状況 | 抽出元 |
|---|--------|------|-----------|--------|--------|
| 1 | FLUX.2 [klein] 4B | 画像生成（1024x1024、0.5秒/枚） | Apache 2.0 | ✅ メイン採用（ComfyUI経由） | SPEC.md §2, §4.2 |
| 2 | Ken Burns + FFmpeg | 静止画→動画化（ズーム/パンエフェクト） | 無料OSS | ✅ メイン採用（デフォルト） | SPEC.md §2, §4.2 |
| 3 | Wan 2.1 1.3B | 高品質画像→動画化（VBench 86%） | Apache 2.0 | ✅ フォールバック/高品質時 | SPEC.md §2, リサーチ§12 |
| 4 | AnimateDiff | モーション追加アニメーション（8-12GB VRAM） | Apache 2.0 | ✅ フォールバック | SPEC.md §2, リサーチ§11 |
| 5 | moviepy | 動画編集・字幕・BGM合成 | 既存利用 | ✅ メイン採用 | SPEC.md §2, §4.2 |
| 6 | Groq LLM | 台本・プロンプト生成（無料枠） | 既存契約 | ✅ メイン採用 | SPEC.md §2, §4.1 |
| 7 | Pixabay | BGM・SE・画像素材（無料・商用OK） | CC0 / クレジット表記推奨 | ✅ メイン採用 | SPEC.md §4.1, TODO.md P0-5 |
| 8 | YouTube Audio Library | BGM（無料・商用OK） | YouTube所有 | ✅ メイン採用 | SPEC.md §4.1 |
| 9 | YouTube Data API | Shorts投稿・分析 | 無料 | ✅ メイン採用 | SPEC.md §2, §4.1 |
| 10 | Instagram Graph API | Reels投稿 | 無料（ビジネスアカウント必須） | ✅ メイン採用 | SPEC.md §2, §4.1, TODO.md P0-3 |
| 11 | Pinterest API | ピン投稿 | 無料（ビジネスアカウント必須） | ✅ メイン採用 | SPEC.md §2, §4.1 |
| 12 | Google Colab | GPU実行（T4 VRAM 15GB無料） | 無料 | ⭕ 代替案（ComfyUI等の予備実行環境） | リサーチ§27 |
| 13 | CogVideoX | テキスト→動画（Apache 2.0、VRAM 16GB） | Apache 2.0 | ⭕ 参考（Wan 2.1との比較検討） | リサーチ§9 |
| 14 | Stable Video Diffusion | 画像→動画（SV4D 2.0、48フレーム） | 要確認（Stability AI） | ⭕ 代替案（高品質必要時） | リサーチ§10 |
| 15 | Vidu AI Q3 | 無料8回/月、音声同期、16秒、1080p | 無料 | ⭕ 代替案（Wan 2.1が不安定時） | リサーチ§6 |
| 16 | Whisper | 自動字幕生成（80言語対応、SRT形式） | OpenAI CC0 | ⭕ 将来拡張（自動字幕化実装時） | リサーチ§15 |

---

### (H) 将来展開

| # | 項目 | 計画内容 | タイムライン | 抽出元 |
|---|------|---------|-----------|--------|
| 1 | TikTok対応 | 1日1本制限対応。新規アカウント3ヶ月育成期間確保 | Phase 2 途中開始 | TODO.md P0-4, SPEC.md §7.2 |
| 2 | Rena キャラ連携 | AIインフルエンサー Rena LoRA 学習完了後、キャラ一貫性を持つショート動画化 | Phase 3 〜4月 | 統合戦略§3, §5 |
| 3 | デジタル販売連携 | YouTubeショート→説明欄リンク→BOOTH/FANBOX でイラスト販売 | Phase 3 並行 | 統合戦略§4, §6 |
| 4 | テーマ拡張 | 現在4つ → 「トレンド図解」「AI似顔絵」「風景アート」「タイムラプス」追加 | Phase 3 週1-2 | TODO.md P3-2 |
| 5 | 自動選択AI | 前週パフォーマンス学習 → 推奨テーマ自動提示 | Phase 3 後半（オプション） | TODO.md P3-6 |
| 6 | マルチチャネルSNS統合 | YouTubeショート生成後、Instagram / Pinterest / TikTok へ同時配信自動化 | Phase 1完了後 | 統合戦略§2 |

---

### (I) コスト構造

| # | 項目 | 単価 | 月間使用量 | 月額 | 備考 | 抽出元 |
|---|------|------|-----------|------|------|--------|
| 1 | FLUX.2 [klein] 4B | ¥0 | 無制限 | ¥0 | ローカル実行 (Apache 2.0) | SPEC.md §6.1 |
| 2 | Ken Burns + FFmpeg / Wan 2.1 | ¥0 | 無制限 | ¥0 | OSS / コマンド1行 | SPEC.md §6.1 |
| 3 | 直接API (IG/YT/Pinterest) | ¥0 | 無制限 | ¥0 | 各PF個別実装 | SPEC.md §6.1 |
| 4 | Pixabay / YouTube Audio Library | ¥0 | 無制限 | ¥0 | 商用利用OK | SPEC.md §6.1 |
| 5 | Groq API | ¥0 | 無制限 | ¥0 | 既存契約の無料枠 | SPEC.md §6.1 |
| 6 | YouTube Data API | ¥0 | 10,000ユニット/日 | ¥0 | 既存利用中 | SPEC.md §6.1 |
| 7 | Instagram/Pinterest API | ¥0 | 無制限 | ¥0 | 認証済み | SPEC.md §6.1 |
| 8 | EC2 サーバー（既存共用） | ¥3,000/月 | 共用 | ¥0 | youtube_pipeline と共用 | SPEC.md §6.1 |
| 9 | GCS ストレージ | ¥100 | 30日自動削除 | ¥100 | 動画キャッシュ | SPEC.md §6.1 |
| 10 | 監視ツール (Datadog等) | 無料 | 基本プラン | ¥0 | 必要に応じて拡張 | SPEC.md §6.1 |
| **合計** | — | — | — | **¥100/月** | API・ツール費用ゼロ。EC2/ストレージは既存共用 | SPEC.md §6.1 |

### 収入試算（CPM ベース推測）

| 期間 | 月本数 | YT推定 | IG推定 | TT推定 | 合計月収 | コスト | 利益 | 抽出元 |
|------|--------|--------|-------|--------|----------|--------|------|--------|
| 1ヶ月目 | 60 | ¥500 | ¥300 | ¥200 | ¥1,000 | ¥0 | +¥1,000 | SPEC.md §6.3 |
| 3ヶ月目 | 90 | ¥5,000 | ¥2,000 | ¥1,000 | ¥8,000 | ¥0 | +¥8,000 | SPEC.md §6.3 |
| 6ヶ月目 | 90 | ¥30,000 | ¥8,000 | ¥3,000 | ¥41,000 | ¥0 | +¥41,000 | SPEC.md §6.3 |
| 12ヶ月目 | 90 | ¥50,000 | ¥15,000 | ¥5,000 | ¥70,000 | ¥0 | +¥70,000 | SPEC.md §6.3 |

---

### (J) 規約対応

| # | リスク | 対策 | 優先度 | 抽出元 |
|---|--------|------|--------|--------|
| 1 | BGM著作権 | Pixabay / YouTube Audio Library (無料, 商用OK) + クレジット表記推奨 | 🔴 必須 | SPEC.md §5.2 |
| 2 | FLUX画像著作権 | 生成画像は個人商用OK（利用規約確認） | 🟠 重要 | SPEC.md §5.2 |
| 3 | 顔認識（AI生成） | 実在人物の顔生成NG（各PF規約違反） | 🔴 必須 | SPEC.md §5.2 |
| 4 | 金融情報（免責事項） | "投資助言ではありません"を必ずCTA表記 | 🟠 重要 | SPEC.md §5.2 |
| 5 | プライバシー（背景人物） | AI生成画像なので無関係（但しテンプレート確認） | 🟡 推奨 | SPEC.md §5.2 |
| 6 | リンク誘導スパム | 1ヶ月に3本以下に抑制 | 🟡 推奨 | SPEC.md §5.2 |
| 7 | AI生成明記 | キャプション最後に #AIアート #生成AI | 🟡 推奨 | SPEC.md §5.2 |
| 8 | YouTube Shorts投稿 | 著作権チェック(Content ID) / BGM確認 / #Shorts必須 / サムネイル自動/カスタム対応 | SPEC.md §5.3 | |
| 9 | Instagram Reels投稿 | ビジネスアカウント確認 / 著作権: Instagram Licensed Music Library OR Pixabay / ハッシュタグ最大30個 / スケジュール最大10日先 | SPEC.md §5.3 | |
| 10 | TikTok投稿 | 個人認証(身分証) / BGM: TikTok Sounds Library OR Pixabay / #AIアート推奨 / リンク: プロフィールのみ / 1日1本(API制限) / アカウント年齢最低3ヶ月 | SPEC.md §5.3 | |

---

## 重要ポイント

### 1. 無料ツール構成の強み
- FLUX.2[klein]（Apache 2.0）+ FFmpeg + 直接API で**月額 ¥100 のみ**（GCSのみ）
- X API 有料化を除外し、YouTube / Instagram / Pinterest の3PF に集約
- フォールバック体制完備：Ken Burns → Wan 2.1 → AnimateDiff の3段階

### 2. 段階的ロードマップの明確性
- **Phase 0（3/7-3/10）**: セットアップ＆既存資源確認 — 9タスク
- **Phase 1（3/11-3/24）**: パイプライン構築 — 6つのコアスクリプト＋統括
- **Phase 2（3/25-4/7）**: テスト投稿35-70本＆データ分析 — GO/NO-GO判定
- **Phase 3（4/8-4/30）**: 本運用3本/日＆最適化

### 3. KPI と撤退基準の定量化
- **GO 条件**: AVG_VIEWS ≥ 500（7日平均）/ エラー率 < 5%
- **NO-GO**: 複数項目未達で改善困難 → プロジェクト見直し
- **月間目標**: 90本 / 月間推定収益 ¥1,000 → ¥70,000（成長曲線）

### 4. 4PJ統合への接続点
- **デジタル販売連携**: YouTubeショート説明欄 → BOOTH/FANBOX イラスト販売へ導線
- **Rena キャラ連携**: Phase 3 で LoRA 学習完了後、キャラ一貫性を持つショート化
- **マルチチャネルSNS**: Shorts Factory パイプライン出力を Instagram / Pinterest へ自動配信

### 5. 既存資産の活用
- **youtube_automation.py** から moviepy / Groq 連携部分をコピー
- **EC2 t4g.medium** を YouTube パイプラインと共用（CPU 80% 制限）
- **GCS ストレージ** 既存設定流用（30日自動削除ポリシー）

### 6. 制約条件への対応
- **¥0予算**: 全ツール無料OSS化 + 既存EC2共用 → ¥100/月のみ（GCS）
- **1人運用**: 完全自動化必須 → Cron + エラーハンドリング + 通知機能
- **API制限**: MAX_PARALLEL_JOBS = 3 で制限対応。投稿間隔 2-12時間以上

### 7. リスク対策の多層化
- **技術リスク**: API Rate Limit → キューイング + Exponential Backoff / 動画生成失敗 → 自動リトライ3回 + フォールバック
- **ビジネスリスク**: アルゴリズム変動 → 日次分析・週次最適化 / 新規アカウント制限 → TikTok 3ヶ月前倒し育成
- **規約リスク**: 著作権 → Pixabay/YT Audio Library 自動確認 / AI生成明記 → 全キャプションに #AIアート

### 8. 関連調査からの活用候補
- **Ken Burns効果**: FFmpeg `zoompan` フィルタで実装（1行コマンド）
- **Whisper 自動字幕**: 将来拡張（SRT形式出力対応）
- **Wan 2.1 / CogVideoX**: メイン（Wan 2.1）の不安定時のフォールバック
- **Vidu AI Q3**: Ken Burns+FFmpeg が不安定時の無料代替案（月8回無料）

