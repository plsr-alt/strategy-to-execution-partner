# マルチチャネル自動展開システム — PLAN.md

> 初版: 2026-03-07

## 背景・課題
- YouTube動画1本を投稿→ 1つのプラットフォームにしか露出されない
- 現在EC2で月産15-20本のYouTube動画を全自動化中
- **機会損失**: Instagram / X / Pinterest / TikTok への露出がゼロ
- **ゴール**: 1つのコンテンツから複数SNSへ自動展開し、総露出を4-5倍化

## 展開ビジョン
```
YouTube 動画生成完了（EC2 Cron）
  ↓
  ├→ 【Instagram】 サムネ + 要約150字 + ハッシュタグ（フィード投稿）
  ├→ 【X】 サムネ + 核心1行 + URL + ハッシュタグ
  ├→ 【Pinterest】 縦長サムネ + SEOキーワード + URL
  └→ 【TikTok】 ショート切り出し版（将来）

効果測定: 週次でSNS訪問流入 + YouTube登録者増加を監視
```

## 技術選択肢（リサーチ済み）
### Option A: Ayrshare API（推奨）
- **料金**: $29/月
- **対応**: Instagram / X / Pinterest / TikTok
- **メリット**: 1つのAPIで複数SNS一括投稿可能
- **デメリット**: TikTokは限定的

### Option B: 個別API統合
- **Instagram Graph API**: フィード対応（ReelsはNG）
- **X API v2**: 画像+動画OK
- **Pinterest API**: ピン投稿OK
- **TikTok Business API**: 審査必須、厳しい
- **メリット**: 柔軟性高し
- **デメリット**: 4つのAPI設定・保守コスト高い

## 採用方針
- **Phase 1**: Ayrshare API で Instagram / X / Pinterest
- **Phase 2 以降**: 必要に応じて個別API切り替え検討

## コンテンツ変換ルール（素案）

### Instagram 用
- サムネ画像（縦長: 1080x1350）
- 要約: 150字以内 + ハッシュタグ10個
- 投稿タイミング: YouTube公開から2時間後（差別化・時間差戦略）

### X 用
- サムネ画像（16:9）
- テキスト: 核心1行 + URL + ハッシュタグ3個（280字以内）
- 投稿タイミング: YouTube公開と同時

### Pinterest 用
- サムネ画像（縦長1000x1500）
- 説明: SEOキーワード + URL + 1行説明
- 投稿タイミング: YouTube公開の24時間後

### TikTok 用（将来）
- 15分動画から15秒～60秒ショート版を自動切り出し
- 投稿タイミング: YouTube公開から3日後

## スケジュール感
- **Week 1 (3/9-3/15)**: API申請・テスト投稿3本
- **Week 2 (3/16-3/22)**: 本格投稿・効果測定開始
- **Week 3+ (3/23-)**: 自動化・スケール・TikTok検討

## 次アクション
1. Ayrshare / 各SNS APIの申請手続き確認
2. API仕様ドキュメント精読
3. SPEC.md で詳細設計開始
