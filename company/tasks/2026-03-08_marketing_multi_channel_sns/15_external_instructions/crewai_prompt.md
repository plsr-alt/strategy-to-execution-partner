# CrewAI市場調査プロンプト — マルチチャネルSNS自動展開

## 調査テーマ
マルチチャネルSNS自動展開システムの市場動向・競合・成功事例・ターゲットインサイト

## 背景と目的
YouTube月産15本の動画をInstagram / X / Pinterest / TikTokへ自動展開し、総露出を4-5倍化するシステムを構築。Instagram Graph API + Pinterest API で直接投稿。月額¥0運用。コンテンツはAI×生活技術（家計管理・自動化・節約）。

本調査により、市場規模・競合ツール・成功事例・プラットフォーム別戦略を把握し、自社システムの位置付けと最適化方針を決定する。

## 調査対象（7項目）

### 1. SNSマルチチャネル展開ツール・競合マップ
**検索キーワード**:
- "YouTube to Instagram Pinterest X automatic cross-posting tools 2026"
- "social media repurposing automation Buffer Hootsuite Later IFTTT Zapier"
- "cross-platform content distribution AI tools"

**収集項目**:
- 主要ツール名（3-5件）
- 各ツールの特徴・料金・API対応状況
- 成功事例（2-3件）
- 市場シェア・トレンド

**信頼度**: 公式ドキュメント・ケーススタディ優先

### 2. Instagram/Pinterest/X教育系コンテンツ市場動向
**検索キーワード**:
- "financial education content Instagram market 2026"
- "personal finance Pinterest SEO strategy trends"
- "AI finance creators X Twitter growth"
- "educational content algorithm 2026 Instagram Pinterest X"

**収集項目**:
- プラットフォーム別のコンテンツ特性（形式・長さ・トーン）
- エンゲージメント率・フォロワー増加率のデータ
- アルゴリズムのポイント（2024-2026年版）
- 教育系コンテンツの市場規模

**信頼度**: Instagramビジネス公式ブログ・Pinterestピンデータ・X Analytics優先

### 3. YouTube→多チャネル横展開で成功した人物・企業
**検索キーワード**:
- "YouTuber multi-channel growth strategy case study"
- "financial education creator Instagram Pinterest growth"
- "content repurposing successful examples 2026"
- "personal finance channel cross-platform strategy"

**収集項目**:
- 具体的な人物名・企業名（必須）
- チャネル別のフォロワー数・成長率
- 使用ツール・自動化手法
- 成功の要因分析
- 初期段階での投資額（¥0事例優先）

**信頼度**: インタビュー記事・ケーススタディ・本人インタビュー動画優先

### 4. ターゲット層インサイト（25-45歳、IT高リテラシー、金融・自動化興味）
**検索キーワード**:
- "financial education audience demographics 2026"
- "personal finance content consumption behavior"
- "automation enthusiasts online behavior"
- "age 25-45 financial content preferences"

**収集項目**:
- ターゲット層の主要SNS（利用率・時間帯）
- コンテンツ形式への好み（短動画 vs 長編 vs 画像）
- 信頼できるコンテンツソース
- 購買・行動への影響度
- フォロー理由・期待値

**信頼度**: HubSpot・Content Marketing Institute等のレポート優先

### 5. プラットフォーム別最適コンテンツ戦略
**検索キーワード**:
- "Instagram Reels algorithm strategy 2026"
- "Pinterest SEO organic reach strategy"
- "X/Twitter content strategy 2026"
- "platform-specific content adaptation guide"

**収集項目**:
- 各プラットフォームのアルゴリズムのポイント（5-10個）
- 最適な投稿頻度・タイミング
- 画像 vs テキスト vs 動画 vs ストーリーの使い分け
- ハッシュタグ・キーワード戦略
- CTA（行動喚起）の効果的な方法

**信頼度**: 公式ビジネスブログ・業界レポート優先

### 6. ¥0予算・直接API統合での成功事例
**検索キーワード**:
- "free social media automation API 2026"
- "DIY cross-posting Python example"
- "Instagram Graph API Pinterest API no-cost"
- "automated content distribution zero budget"

**収集項目**:
- 無料ツール・オープンソース（3-5件）
- 実装難易度・技術要件
- 使用テクノロジー（Python/Node.js/Zapierなど）
- 実装事例・ブログ記事
- メリット・デメリット

**信頼度**: GitHubリポジトリ・技術ブログ・実装例優先

### 7. 時差投稿戦略の効果データ
**検索キーワード**:
- "social media scheduling time zone effectiveness 2026"
- "posting time analysis engagement rate"
- "best posting time Instagram Pinterest X by timezone"
- "scheduling algorithm impact on reach"

**収集項目**:
- 複数時間帯での投稿効果の数値化（エンゲージメント増減 %）
- 最適な投稿時刻（プラットフォーム別・曜日別）
- 時差投稿によるリーチ拡大の効果
- スケジューリングツールの精度データ
- グローバル対応戦略の事例

**信頼度**: 統計レポート・API提供元の公開データ優先

## 出力形式
```json
{
  "research_topic": "マルチチャネルSNS自動展開システムの市場調査",
  "findings": [
    {
      "category": "1. SNS展開ツール競合マップ",
      "fact": "〇〇というツールは〇〇を特徴とし、事例では〇〇%のリーチ増加を実現",
      "source": "https://example.com/case-study",
      "confidence": "高"
    },
    {
      "category": "2. 教育系コンテンツ市場動向",
      "fact": "InstagramではReelsが〇〇%のエンゲージメント率を示す一方、Pinterestでは〇〇形式が最適",
      "source": "https://example.com/report",
      "confidence": "高"
    },
    ...
  ],
  "success_cases": [
    {
      "name": "具体的な人物・企業名",
      "description": "YouTube→Instagram→Pinterestで展開し、フォロワー〇〇万人に成長",
      "tools": ["使用ツール1", "使用ツール2"],
      "key_factors": ["成功要因1", "成功要因2"],
      "investment": "月額¥0 or ¥XX",
      "source": "https://example.com"
    }
  ],
  "key_insights": [
    "ターゲット層は朝7-8時と夜21-22時のコンテンツ消費が最も多い",
    "Pinterestは検索エンジン的性質が強く、キーワードSEOが重要",
    "[推測] AI×金融教育ジャンルは今後2-3年で急成長の可能性が高い"
  ],
  "sources": ["url1", "url2", "url3", ...]
}
```

## 品質基準
- **最低限**: 各項目につき最低3件の事実+ソース
- **確実性**: 推測は必ず `[推測]` で明記
- **具体性**: 企業名・人物名・数値データが必須
- **鮮度**: 2025年以降の情報を優先

## 実行指示
1. すべてのキーワードで Web 検索を実行
2. 信頼度の高い公式ソース・ケーススタディを優先
3. 各事実に対して必ずソースURL を記載
4. JSON形式で構造化出力
5. 生ログも `raw_output.txt` で保存

## 納期
2026-03-08 10:00 UTC+9
