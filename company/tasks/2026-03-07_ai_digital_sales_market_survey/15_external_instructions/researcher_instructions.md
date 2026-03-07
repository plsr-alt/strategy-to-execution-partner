# researcher（外部委譲）への指示

## タスク名
BOOTH / pixivFANBOX / DLsite の AI画像販売市場調査

## 実行方法
上記ディレクトリの `crewai_command.sh` を WSL から実行してください。

```bash
bash /mnt/c/Users/tshibasaki/Desktop/etc/work/task/company/tasks/2026-03-07_ai_digital_sales_market_survey/15_external_instructions/crewai_command.sh
```

## 調査サブテーマ（4つの CrewAI 並列実行）

### 1. BOOTH AI画像販売市場
**検索キーワード群**:
- BOOTH AI画像販売 2025 2026
- BOOTH クリエイター 売上 月収 事例
- BOOTH AI生成画像 ジャンル TOP5 人気
- BOOTH 価格帯 おすすめ 相場
- BOOTH AI画像 規約 ガイドラインライン AI申告

**期待情報**:
- 売れ筋ジャンル（イラスト・壁紙・3Dモデル等）の具体的ランキング
- 実例クリエイターの月収・支援者数・購入数
- 価格帯の傾向（300円～3000円等の分布）
- AI表記義務・禁止コンテンツの最新規約
- 成功の秘訣（企画・マーケティング・複合販売等）

---

### 2. pixivFANBOX AI画像支援
**検索キーワード群**:
- pixivFANBOX AI画像クリエイター 2025 2026
- pixivFANBOX AI画像 支援者数 月額 事例
- pixivFANBOX プラン構成 価格帯 最適化
- pixivFANBOX AI生成画像 規約 申告 禁止事項
- pixivFANBOX 月収 10万円 実績 クリエイター

**期待情報**:
- AI系クリエイターの支援者数の現実的な目安（10人～10,000人レンジ）
- 人気プラン構成（500円プランのコンテンツ内容例等）
- 月1万円～月10万円達成者の具体的なプラン設計
- AI規約・著作権に関する最新ルール
- ファンコミュニティの構築方法

---

### 3. DLsite AI専用ブース
**検索キーワード群**:
- DLsite AI画像販売 2025 2026
- DLsite AI生成コンテンツ ブース 売上
- DLsite AI画像 ジャンル 人気 ランキング
- DLsite イラスト 3Dモデル CG 売上規模
- DLsite AI販売戦略 成功 クリエイター 月収

**期待情報**:
- DLsite AI専用ブースの全体売上規模（推定値でも可）
- 人気ジャンル（アダルト・非アダルト別）
- 販売ランキング上位の価格帯・内容
- 手数料体系・振込ルール
- BOOTH/pixivFANBOX と比較した優位性・課題

---

### 4. 2025-2026年 AI画像販売トレンド総括
**検索キーワード群**:
- AI画像販売トレンド 2025 2026 注目
- AI画像販売 売れるコンセプト 差別化
- AI画像デジタル販売 著作権 規制 リスク
- AI画像販売 イラスト 壁紙 3Dモデル キャラクター
- AI生成画像 今後の市場 飽和 競争

**期待情報**:
- 売れるコンセプト（特定ニッチ・キャラ・スタイル等）
- 過飽和化している分野・避けるべきジャンル
- 規制リスク（著作権侵害・プラットフォーム規約違反）
- 差別化戦略（高度化・複合販売・SNS連携等）
- 2027年以降の市場予測

---

## 出力形式

各調査の CrewAI 実行により、以下が自動生成されます:

```
20_worker_outputs/
├── booth_research/
│   ├── report.json （構造化データ）
│   └── raw_output.txt （生ログ）
├── fanbox_research/
│   ├── report.json
│   └── raw_output.txt
├── dlsite_research/
│   ├── report.json
│   └── raw_output.txt
└── trends_research/
    ├── report.json
    └── raw_output.txt
```

## quality_bars（成功基準）

- [ ] 各 report.json に `market_definition`, `trends`, `sources` が含まれている
- [ ] 最低 5つ以上の URL ソースが `sources` に記載されている（プラットフォーム別）
- [ ] 具体的な数値（売上・支援者数・月収等）が最低 3件以上含まれている
- [ ] プレイヤー情報（クリエイター名・企業等）が最低 5件以上含まれている
- [ ] raw_output.txt が存在し、JSON パースに失敗した場合のフォールバック情報として機能

---

## 次ステップ（structurer への引き継ぎ）

CrewAI 実行完了後、内部ワーカー（structurer）が 4 つの report.json を受け取り、以下を実行：
1. 複数ソースからの重複排除・信頼度判定
2. BOOTH / pixivFANBOX / DLsite 別の比較フレームワーク作成
3. 表形式への構造化
4. 未確認事項・推測の抽出

---

**参照**: `company/external_tools.md` / `company/quality_bars.md`
