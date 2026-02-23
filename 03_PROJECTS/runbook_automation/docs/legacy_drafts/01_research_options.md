# Runbook自動化 — 方式調査レポート

**作成日**: 2026-02-20
**調査対象**: 画像→データ抽出 / データ反映の全方式

---

## A. 画像→データ抽出レイヤー

### A-1. OCR（光学文字認識）

#### A-1-1. 汎用OCR
| ツール | 概要 | 強み | 弱み |
|--------|------|------|------|
| Tesseract 5 | OSS。LSTM搭載 | 無料・ローカル動作・カスタマイズ可 | 日本語精度やや低め。前処理依存 |
| Google Vision API | GCP提供クラウドOCR | 高精度・日本語強い・手書き対応 | クラウド送信必要。コスト発生 |
| Azure AI Vision OCR | MS提供 | レイアウト解析統合。Forms Recognizerと連携 | 同上 |
| AWS Textract | AWS提供 | フォーム/表抽出に特化。Key-Value抽出 | 英語中心。日本語表現で精度差 |

#### A-1-2. 帳票特化OCR
| ツール | 概要 | 強み | 弱み |
|--------|------|------|------|
| AWS Textract Queries | 質問形式でKey抽出 | 柔軟なKey指定。AWS内完結 | クエリ設計工数。日本語改善余地 |
| ABBYY FlexiCapture | エンタープライズ帳票 | 高精度・ゾーン定義可 | 高コスト・オンプレ前提 |
| DynaForms / AI-OCR系SaaS | 国内ベンダー多数 | 日本語特化・帳票学習済 | ベンダーロック・API品質差 |

#### A-1-3. 画面UI文字向け
| ツール | 概要 | 強み | 弱み |
|--------|------|------|------|
| EasyOCR | OSS。GPU対応 | 多言語。Pythonから簡単利用 | 速度やや遅い |
| PaddleOCR | Baidu系OSS | 高速・高精度。日本語モデルあり | 中国系。セキュリティポリシー確認必要 |
| docTR | Huggingface系OSS | モダンアーキ。カスタマイズ容易 | エコシステム発展途上 |

---

### A-2. フォーム・表構造抽出

#### A-2-1. 領域検出
- **物体検出系（YOLO / LayoutLM）**: 入力フィールド、ラベル、表の領域をbounding boxで検出
- **LayoutLMv3 / DocFormer**: レイアウト＋テキスト＋画像を統合したマルチモーダルモデル。帳票構造理解に強い
- **Rule-based領域抽出**: 座標ベースのゾーン定義。手順書フォーマットが固定の場合に有効

#### A-2-2. 表復元
- **Microsoft Table Transformer**: 表構造をセルレベルで復元
- **AWS Textract Table API**: セル座標・行列情報を返却
- **PaddleOCR表認識**: 日本語表に対応

#### A-2-3. ラベル-値ペア抽出
```
手法：
1. Key-Value OCR API (Textract, Forms Recognizer)
2. テキスト近傍解析（ラベルの右/下にある値を紐付け）
3. LLMによる構造解釈（後述）
```

---

### A-3. LLMによる正規化・構造化

#### 役割
OCR出力（生テキスト）をLLMが受け取り：
- 項目名の揺れ吸収（「氏名」「お名前」「NAME」→ `name`）
- JSON正規化（スキーマに合わせた変換）
- 欠損検知（必須項目が抽出できていない場合にフラグ）
- バリデーション（日付フォーマット、数値範囲チェック）

#### 選択肢
| モデル | 利用形態 | 適性 |
|--------|----------|------|
| Claude claude-sonnet-4-6 / claude-opus-4-6 | API（Anthropic） | 指示追従性高。構造化出力に強い |
| GPT-4o / GPT-4-turbo | API（OpenAI） | Vision対応。マルチモーダル直接入力可 |
| Gemini 1.5 Pro | API（Google） | 長コンテキスト。Document AI統合 |
| LLaMA 3 / Mistral | ローカル/SageMaker | データ外部送信なし。PII対応容易 |
| Amazon Bedrock | AWS管理API | Claudeを含む複数モデル。VPC内完結可 |

#### プロンプト設計のポイント
```
- Few-shot例（3〜5例）を含める
- 出力形式をJSONスキーマで指定
- 不確かな場合は confidence スコアを返させる
- システムプロンプトで業務ドメイン知識を注入
```

---

### A-4. 精度向上施策

| 施策 | 概要 | 効果 |
|------|------|------|
| 前処理 | グレースケール化、二値化、ノイズ除去、傾き補正 | OCR精度+10〜20% |
| 辞書補完 | 業務固有語辞書（勘定科目、部署名等）でルール補正 | 固有名詞精度向上 |
| ファインチューニング | 社内データでOCRモデルを追加学習 | 特定フォームの精度大幅向上 |
| アンサンブル | 複数OCRの結果を多数決/信頼度加重で合成 | 頑健性向上 |
| 人手フィードバック | 確認UIで訂正データを蓄積し再学習 | 継続的改善 |
| 評価設計 | Precision/Recall/F1で定量評価。テストセット固定 | 改善サイクル可視化 |

---

## B. データ反映レイヤー

### B-1. CSV / Google Sheets出力
- **概要**: 抽出結果をCSVに出力。SheetsはGAS/API経由で書き込み
- **強み**: 実装最速。既存業務フローと親和性高
- **弱み**: 最終入力は人手。自動反映でない
- **適性**: MVP初期段階

### B-2. API登録
- **概要**: 既存システムのAPIエンドポイントに直接POST
- **強み**: リアルタイム反映。正確
- **弱み**: API仕様調査・認証設計が必要。システム改修コスト
- **適性**: 既存システムにAPIがある場合の中期目標

### B-3. 画面自動入力（RPA/ブラウザ自動化）
| ツール | 概要 | 強み | 弱み |
|--------|------|------|------|
| UiPath | エンタープライズRPA | GUI操作自動化。Excel/Web統合 | 高コスト・UI変更に脆弱 |
| Automation Anywhere | 同上 | AI連携機能 | 同上 |
| Playwright / Puppeteer | OSS。ブラウザ自動化 | 安価・柔軟・テストと共用可 | 保守コスト |
| Selenium | OSS定番 | 実績豊富 | 速度・保守コスト |
| pyautogui | Python OSS | シンプル | デスクトップアプリ向き |

### B-4. 中継サーバ方式（オーケストレーション）
```
[抽出サービス] → [中継API(FastAPI/Lambda)] → [各システム]
                        ↓
                  [監査ログDB]
                  [ステータス管理]
                  [リトライ制御]
```
- **強み**: 一元管理。ログ集中。システム追加が容易
- **弱み**: インフラ設計・運用コスト

### B-5. ハイブリッド構成（推奨）
```
高精度・API対応システム → API直接登録
低精度・API非対応システム → RPA/Playwright + 人手確認
すべてのケース → 中継サーバで監査ログ一元管理
```

---

## C. AWS サービス活用案

```
S3          → 画像・手順書の保存
Textract    → OCR・フォーム抽出
Bedrock     → LLM正規化（Claude/Mistral等）
Lambda      → 処理オーケストレーション
Step Functions → ワークフロー管理・リトライ
DynamoDB    → 抽出結果・ステータス管理
API Gateway → 外部システム連携
CloudWatch  → ログ・アラート監視
Rekognition → 画像前処理・領域検出補助
SageMaker   → カスタムモデル学習（発展）
```

### 代替スタック（非AWS）
```
GCP: Document AI + Vertex AI + Cloud Functions + BigQuery
Azure: Form Recognizer + OpenAI Service + Functions + Cosmos DB
オンプレ/OSS: Tesseract + LLaMA + FastAPI + PostgreSQL + Airflow
```

---

*調査ソース（仮定）: AWS公式docs、Anthropic docs、各種技術ブログ、社内システム仕様書（未確認）*
