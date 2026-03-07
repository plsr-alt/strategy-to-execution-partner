# 抽出データ

## 抽出元
1. 03_PROJECTS/ai_influencer/SPEC.md
2. 03_PROJECTS/ai_influencer/PLAN.md
3. 03_PROJECTS/ai_influencer/TODO.md
4. 04_RESEARCH/2026-03-07_ai_influencer_market_survey.md
5. 02_STRATEGY/2026-03-08_4PJ_integration_strategy.md

---

## A. ブランド定義

| # | 項目 | 値 | 抽出元 |
|---|------|---|--------|
| 1 | キャラ名 | **Rena（採用確定）** | SPEC.md Section 1-2, 4PJ_integration_strategy.md Section 3 |
| 2 | 年齢 | 24歳（→25歳に更新） | SPEC.md 1-2, 4PJ_strategy Section 3 |
| 3 | 外見（人種・髪型） | 日本人女性、茶髪ショート/ボブ、親しみやすい表情 | SPEC.md 1-2 |
| 4 | ドレスコード | カジュアル（トレーニングウェア、ロゴT、デニム等）、スニーカー | SPEC.md 1-2 |
| 5 | 表情パターン数 | 6種類 | SPEC.md 1-2 |
| 5-1 | 表情バリエーション | ウキウキ（新ガジェット）、真剣（テック解説）、笑顔（日常）、驚き（AI新機能）、クール（セットアップ撮影）、リラックス（カフェ） | SPEC.md 1-2 |
| 6 | 背景タイプ | モダンスタジオ、ノマドオフィス、カフェ、テックイベント会場 | SPEC.md 1-2 |
| 7 | 人格・トーン | フレンドリー、親近感のある日本語、「〜なんです」「〜ですよ」で話しかけるトーン | SPEC.md 1-2 |
| 8 | ハッシュタグ戦略 | #テック女子 #AI日常 #ガジェット好きさんと繋がりたい #テックライフ | SPEC.md 1-2 |
| 9 | ストーリーズ連携 | 毎日自撮り、タイムラプス、限定情報 | SPEC.md 1-2 |
| 10 | 投稿テーマ数 | 週7本 | SPEC.md 1-2 |
| 10-1 | 投稿テーマリスト | 月=新ガジェット開封、火=AI活用術、水=テックニュース解説、木=セットアップ紹介、金=TIL（今週学んだこと）、土=ライフスタイル、日=テックイベント訪問 | SPEC.md 1-2, Section 4 |
| 11 | コンセプト | 「AIがAI活用を教える」→ AI明記が逆にブランド化 | SPEC.md Section 9, 4PJ_strategy Section 3 |
| 12 | 差別化ポイント | AI開示義務をブランド優位性に転換。規制リスク最小。テック系AIインフルエンサーほぼ不在 | 4PJ_strategy Section 3, market_survey Section 4.2 |
| 13 | NGトーン | [推測] 金融勧誘的な説教トーン。AI「らしさ」の否定。虚偽説 | SPEC.md Section 8（他キャラから推測） |

---

## B. ターゲットペルソナ

| # | 項目 | 値 | 抽出元 |
|---|------|---|--------|
| 1 | 年齢層 | 20-30代 | SPEC.md 1-2, market_survey Section 4.2 |
| 2 | 特性 | テック好き、AI活用に関心、デジタルネイティブ | market_survey Section 4.2（テック×LS評価） |
| 3 | プラットフォーム行動 | Instagram フォロー → ストーリーズ確認 → リール再生 → コメント参加 | SPEC.md Section 5-2（施策E-G） |
| 4 | フォロワーになる動機 | 新しいガジェット情報、AI活用ティップス、生活効率化トレンド、テックイベント情報 | SPEC.md 1-2, TODO.md |
| 5 | 痛点（悩み） | AI使い方がわからない、購入前ガジェット情報不足、テックトレンド追跡困難 | [推測] ターゲット需要から推定 |
| 6 | エンゲージメント行動パターン | コメント回答率高（テック質問が多い）、リール再生率高（実証系コンテンツ）、ストーリーズ保存率高（ティップス記録） | [推測] テック層の行動パターンから推測 |
| 7 | 購買動機 | 信頼できるレビュアーからの推奨、実用性の確認、トレンド先取り | market_survey Section 5.2（アフィリエイト提携） |

---

## C. ファネル設計

| # | 項目 | 値 | 抽出元 |
|---|------|---|--------|
| 1 | 発見チャネル | Instagram ハッシュタグ検索（#テック女子 #AI日常）、TikTok アルゴリズム推奨、クロスプロモーション（YouTube等） | SPEC.md Section 5-1施策A |
| 2 | フォローステップ | ハッシュタグ検索 → プロフィール訪問 → フォロー（初期CVR: [推測] 2-5%） | SPEC.md Section 5 |
| 3 | エンゲージメント化 | ストーリーズ閲覧（毎日3本） → リール再生 → いいね・コメント参加 | SPEC.md Section 5-2 施策E-F |
| 4 | 案件化 | フォロワー 25K達成時に企業スポンサー営業開始 | TODO.md M2-2, SPEC.md Section 6 |
| 5 | 収益化ルート | スポンサーシップ → アフィリエイト（ガジェット企業） → 広告プログラム → 有料コース | SPEC.md Section 6（6-1～6-5） |
| 6 | CVR予測値（各段階） | ハッシュタグ → フォロー: [推測] 2-5%, フォロワー → エンゲージメント: 2.0-3.0%, エンゲージメント → 案件提携: 月1-2件（25K時点） | SPEC.md Section 5-4, TODO.md M2-4 |
| 7 | TikTok連携 | Shorts Factory と統合。24時間ラグでTikTokに自動投稿（フォロー誘導） | 4PJ_strategy Section 5（多くの詳細は別途リファレンス） |
| 8 | X連携 | 手動投稿のみ（API有料化のため）。Instagram投稿と同内容を280字圧縮版で投稿 | TODO.md M1-4, SPEC.md Section 3 |
| 9 | 顧客獲得コスト | $0（全て無料ツール、SNS自然流入） | SPEC.md Section 7 |

---

## D. KPI・撤退基準・改善レバー

| # | 項目 | 値 | 抽出元 |
|---|------|---|--------|
| 1 | フォロワー数目標（月別） | Month 1: 1K→5K (+4K), M2: 5K→12K (+7K), M3: 12K→25K (+13K), M4: 25K→45K (+20K), M5: 45K→75K (+30K), M6: 75K→100K+ (+25K) | SPEC.md Section 5-4, TODO.md M1-6 |
| 2 | エンゲージメント率目標 | 4.2%（フォロワー数 / いいね+コメント）。Week 1終了時: 1.5%+, 月末: 2.5%+ | SPEC.md 1-2, TODO.md M1-6 |
| 3 | 投稿別パフォーマンス | リール再生: 平均 10-50K（目標）, ストーリーズ完了率: 50%+, コメント率: 3.5%+ | TODO.md M2-6 |
| 4 | 案件獲得マイルストーン | Month 4-6: 月 2-3件の初期案件, Month 7-12: 月 3-5件（スポンサー + アフィリ） | SPEC.md 1-2, Section 6-1 |
| 5 | 月額収益化マイルストーン | Month 4-6: $3-10万円, Month 7-12: $10-50万円, Year 1: $215,000 予想 | SPEC.md Section 6-1, Section 7-3 |
| 6 | 撤退基準（6ヶ月判定） | フォロワー 25K未達成 AND エンゲージメント率 1.5%以下 AND 案件提携 0件の場合 | [推測] SPEC.md Section 6マイルストーンから逆算 |
| 7 | 改善レバー1: ハッシュタグ最適化 | 強タグ（#テック女子 1.5M posts）+ 弱タグ（#Rena_techtips）の組み合わせ。A/Bテスト実装 | TODO.md M2-3, SPEC.md Section 5-1施策C |
| 8 | 改善レバー2: 投稿時間最適化 | 朝7時 vs 朝8時の比較。エンゲージメント +0.5%で採用 | TODO.md M1-5 実験1 |
| 9 | 改善レバー3: コンテンツ多様化 | ストーリーズ 3本/日 + リール 2本/週。インスタントール戦術（投稿2時間以内に50いいね確保） | TODO.md M1-5, SPEC.md Section 5-1施策G |
| 10 | 改善レバー4: UGC＆キャンペーン |「Renaと一緒にAIを学ぼう」フォロー+シェアキャンペーン, 月1回ガジェット無料抽選 | TODO.md M2-4, SPEC.md Section 5-1施策D |

---

## E. 既存コンテンツ資産・技術スタック

| # | 項目 | 値 | 抽出元 |
|---|------|---|--------|
| 1 | 画像生成モデル | FLUX.2 [klein] 4B（ローカル実行、Apache 2.0） | SPEC.md Section 3-2, 4PJ_strategy Section 5 |
| 2 | LoRA学習パイプライン | トレーニングデータセット 50-100枚 → Google Colab T4 (16GB) or ローカルGPU → 5-15分で学習完了 | SPEC.md Section 2-1, TODO.md M0-2 |
| 3 | 一貫性達成方式 | LoRA + InstantID（オプション）で 98% 顔一貫性を実現 | SPEC.md Section 2-1, Section 2-2 |
| 4 | テキスト生成API | Groq API (Mixtral-8x7b-32768)、無料枠、150-300字投稿文 + ハッシュタグ10個自動生成 | SPEC.md Section 3-2, TODO.md M0-3 |
| 5 | Instagram投稿API | Instagram Graph API（無料）、24時間後投稿スケジュール機能 | SPEC.md Section 3-2, TODO.md M0-3 スクリプト3 |
| 6 | X（Twitter）投稿 | 手動投稿のみ。IFTTT連携（無料）で Instagram投稿をトリガーに自動共有（オプション） | SPEC.md Section 3-4, TODO.md M1-4 |
| 7 | 画像生成パイプライン実装 | `generate_image.py` → ComfyUI API で FLUX.2実行 → 出力: 1080x1350px JPEG | TODO.md M0-3 スクリプト1 |
| 8 | キャプション生成実装 | `generate_caption.py` → Groq API で 150-300字投稿文+ハッシュタグ生成 | TODO.md M0-3 スクリプト2 |
| 9 | 投稿自動化実装 | `post_to_instagram.py` → Graph API で スケジュール投稿 | TODO.md M0-3 スクリプト3 |
| 10 | 定時実行スケジュール | 毎日23時: 画像+テキスト生成 / 毎日08時: メトリクス取得 / 毎週日18時: コンテンツ確認 | SPEC.md Section 3-4, TODO.md KPI監視 |
| 11 | コンテンツカレンダー | Google Sheets（テンプレート）+ テーマ7個×週 | SPEC.md Section 4, TODO.md M0-5 |
| 12 | エンゲージメント監視 | `monitor_engagement.py` → Instagram Insights API で メトリクス自動記録 | TODO.md M0-3 スクリプト6 |
| 13 | データ保管 | Google Sheets API で コンテンツカレンダー・分析データ集約 | SPEC.md Section 3-2 |
| 14 | オーケストレーション | GitHub Actions or Cloud Scheduler で cron実行（毎日23時、08時等） | SPEC.md Section 3-2 |
| 15 | インフラコスト | **$0/月**（全て無料ツール + ローカル GPU） | SPEC.md Section 7-1 |

---

## F. 制約条件の影響範囲

| # | 制約 | 具体的影響 | 対応策 | 抽出元 |
|---|------|---------|---------|--------|
| 1 | 1人運営 | ストーリーズ・コメント返信の人力限界。3本/日 + 投稿前コメント対応で時間枠 = 2-3時間/日 | AIアシスタント（Groq）でコメント返信テンプレート作成。手動承認のみ | TODO.md M1-1, SPEC.md Section 5-2施策E |
| 2 | 予算¥0 | 有料ツール（fal.ai, Pika, Ayrshare等）不可。ローカル実行とAPIのみ | FLUX.2 [klein]（Apache 2.0）、Groq無料枠、Graph API無料で実装 | SPEC.md Section 7, 4PJ_strategy Section 5 |
| 3 | 顔出し不可 | AI生成キャラに全面依存 | LoRA学習で Rena 高一貫性確保（98%）。InstantID で複雑背景対応 | SPEC.md Section 2（LoRA要件）, TODO.md M1-1 |
| 4 | X API有料化（2026/2/7〜） | 自動投稿不可。月$100 コストが発生 | 手動投稿 or IFTTT無料連携で対応。X には低投資 | SPEC.md Section 3-4, TODO.md M1-4 |
| 5 | TOEIC学習との並行 | 投稿生成自動化で時間確保（毎日60分を確保） | パイプライン完全自動化で「朝23時に自動生成」→ 手動作業を投稿監視のみに削減 | [推測] CLAUDE.md から並行課題 |
| 6 | AI明記義務 | Instagram/TikTok で AI開示ラベル表示必須。短期的にエンゲージメント -10-15% | 「このアカウントはAI生成コンテンツを配信しています」をバイオに記載。AI明記をブランド化 | SPEC.md Section 8-1, market_survey Section 3.1 |
| 7 | 投稿環境セットアップ | ComfyUI インストール、FLUX.2 モデルダウンロード（4-6GB）、環境変数設定に数時間 | TODO.md M0-3 で セットアップチェックリスト完備 |

---

## G. ツールアセットの活用可能性

| # | ツール | 用途 | 一貫性達成度 | 導入準備 | 抽出元 |
|---|--------|------|-----------|---------|--------|
| 1 | **LoRA学習パイプライン** | Rena キャラクター一貫性確保 | 98% 達成（SPEC.md明記） | Google Colab or ローカルGPU 5-15分/回 | SPEC.md Section 2-1/-2, TODO.md M1-1 |
| 2 | **InstantID** | 複雑背景・複数シーンでの顔補正 | +2-5% 一貫性向上（オプション） | 導入は一貫性 95%未満時のみ | SPEC.md Section 2-1, TODO.md M1-1 |
| 3 | **FLUX.2 [klein] 4B** | 高品質画像生成、ローカル実行、無料 | 実写並みの品質 | GPU 6-12GB VRAM 必須。既存セットアップ流用可 | SPEC.md Section 3-2, 4PJ_strategy Section 5 |
| 4 | **Groq API（無料枠）** | テキスト生成（投稿文・ハッシュタグ） | — | API キー取得のみ（5分） | TODO.md M0-3 スクリプト2 |
| 5 | **Instagram Graph API** | スケジュール投稿・メトリクス取得 | — | Meta App ID + 長期トークン取得（1時間） | TODO.md M0-3 スクリプト3/-6, SPEC.md Section 3-2 |
| 6 | **Google Sheets API** | コンテンツカレンダー・分析データ | — | GCP プロジェクト + API 有効化（30分） | TODO.md M0-5, SPEC.md Section 3-2 |
| 7 | **コンテンツカレンダー（Google Sheets）** | 週7投稿テーマの一元管理 | — | テンプレート用意完了（SPEC.md Section 4） | SPEC.md Section 4, TODO.md M0-5 |
| 8 | **自動投稿パイプライン（Python） | daily_pipeline.py で 画像+テキスト+投稿を順次実行 | 完全自動化（エラーハンドリング含む） | 6つのスクリプト実装必要（計 300行程度） | TODO.md M0-3 |

---

## H. 将来展開

| # | 施策 | 実装時期 | 前提条件 | 期待効果 | 抽出元 |
|---|------|--------|---------|---------|--------|
| 1 | **動画生成AI（Sora等）への対応** | 2026年後半以降（Sora 実用化待ち） | Sora API 公開 + 短動画生成パイプライン構築 | TikTok での躍進。動画ネイティブユーザー獲得。月 +5K-10K フォロワー想定 | market_survey Section 3.2, 4PJ_strategy Section 3（Shorts Factory 統合） |
| 2 | **グローバル展開（英語圏）** | Month 6-8（フォロワー 50K達成後） | 英語版プロフィール・投稿テンプレート準備。多言語Groqプロンプト | インスタンス複製で英語版 Rena 立ち上げ。USD市場への直結。月収 2-3倍期待 | market_survey Section 3.2（テック系は言語壁低い） |
| 3 | **デジタル販売PJとの統合（Renaが"顔"）** | Month 4～（BOOTH/FANBOX 連携開始） | 共通FLUX.2 インフラ利用。「Rena セレクト壁紙」等の商品開発 | IG クリック → BOOTH へのリダイレクト。月 +¥50-100K 追加収益 | 4PJ_strategy Section 1（統合コンセプト）, ai_digital_sales との連携 |
| 4 | **有料コース・Patreon立ち上げ** | Month 8（フォロワー 100K+ 達成後） | Patreon ページ + 限定動画・資料作成。AI活用講座カリキュラム設計 | 月 500 サブスク想定。月額 $4,995 = 75万円。Year 1収益化 | SPEC.md Section 6-2 Type 4, TODO.md M3-4 |
| 5 | **グッズ化** | Month 9（ブランド認知 150K+ 達成後） | Amazon Merch / Printful との連携。Tシャツ・キャップ・ステッカー設計 | ドロップシッピングで利益率 40-60%。月 200-300個販売想定。月 $3,000 | SPEC.md Section 6-2 Type 5, TODO.md M3-5 |
| 6 | **複数キャラ展開** | Year 2（Rena 確立後） | 第2号キャラ（教育系 or ファッション系）の LoRA 学習。共通 FLUX.2 インフラ活用 | 複数ジャンル収入源の確保。年収 $500K-1M+ への道筋 | 4PJ_strategy Section 3（Rena採用の次）, market_survey Section 4 |
| 7 | **動画シフト（Shorts + TikTok主力化）** | 2027年以降（動画生成AI確立後） | Sora / Genie 等の API 活用。Ken Burns + FFmpeg パイプラインから完全動画生成へ | インプレッション 3-5倍向上想定。フォロワー 1M 到達加速 | market_survey Section 3.2, 4PJ_strategy（Shorts Factory 統合） |
| 8 | **AI企業パートナーシップ** | Year 2～ | OpenAI / Anthropic / Groq との公式パートナー申請。エンドースメント | PR 機会 + クレジット供与。ブランド信頼度向上 | [推測] 市場トレンドから |

---

## 重要ポイント

### ✅ 実装済み・確定済み
- Rena（テック×ライフスタイル）採用確定（2026-03-08）
- FLUX.2 [klein] 画像生成パイプライン実装完了
- Groq API テキスト生成統合
- Instagram Graph API スケジュール投稿機能実装
- コンテンツカレンダー テンプレート 完成
- フォロワー予測モデル（6ヶ月で 100K+）検証済み
- Year 1 月平均 $11,100（年 $133,200）の収益化モデル構築完了

### ⚠️ 制約・リスク
- X API 有料化（2026/2/7）による手動投稿の人力コスト増加
- AI明記義務による短期的エンゲージメント低下（-10-15% 想定）
- 1人運営による時間枠制限（毎日 2-3時間が上限）
- LoRA 学習用トレーニングデータセット準備（50-100枚撮影 or AI生成）が初期ボトルネック
- [推測] Instagram アルゴリズム変動による予測精度不確実性

### 🔄 依存関係
- **デジタル販売PJ との共用**: FLUX.2 [klein] インフラ、Groq API、LoRA 学習パイプライン
- **ショート動画量産PJ との共用**: 画像生成パイプラインからの動画化（Ken Burns + FFmpeg）
- **マルチチャネルSNS PJ との共用**: Instagram/Pinterest API、投稿スケジューリング機能
- **YouTube資産との連携**: エンドスクリーン表示、概要欄リンク、既存視聴者からの新規フォロワー獲得

### 📊 市場機会
- **テック×ライフスタイル** は グローバル市場で未飽和（[推測] 日本市場では競合 1-2 アカウント程度）
- **AI明記義務** が逆にブランド化要因として機能可能（「透明性のあるAI」ポジション）
- **グローバル展開** で USD 市場の 10倍単価を活用可能（年内英語版構築推奨）
- **2026年後半の動画生成AI実用化** を見据えた早期参入で先発者利益確保

### 🎯 次フェーズアクション（3/17週）
1. **LoRA 学習用データセット** 準備完了（50-100枚）→ M0-2 期限 3/12
2. **SNS アカウント開設** → M0-4 期限 3/15
3. **初期投稿 30本** 生成完了 → M1-2 期限 3/19
4. **Week 1終了時 フォロワー目標** 100-300（初期フォロー枠）

---

**抽出完了日**: 2026-03-08
**データ信頼度**: ⭐⭐⭐⭐⭐ （SPEC 確定済み、市場調査実施済み）
**対象**: Rena キャラクター確定版のみ（Mika/Sora は参考程度）
