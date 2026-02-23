# Amazon Nova Act 代替ブラウザ自動化ライブラリ・サービス 調査レポート

**調査日**: 2026-02-23
**対象プロジェクト**: Runbook自動化（AWSコンソール操作 → スクリーンショット → AI手順書生成）
**調査者**: Claude（経営パートナー）

---

## 1. 比較表（全候補一覧）

| # | ツール | 種別 | コスト | Python対応 | スクショ | AWS統合 | 難易度 | GitHubスター |
|---|--------|------|--------|-----------|---------|---------|--------|-------------|
| 1 | **browser-use** | OSS + クラウドオプション | 無料（モデル費用のみ） | ✅ ネイティブ | ✅ 自動 | ✅ Bedrock対応 | 低 | ~60k+ (急上昇中) |
| 2 | **Playwright + LLM Vision** | 自前構成（OSS） | 無料（モデル費用のみ） | ✅ 完全 | ✅ 完全制御 | ✅ 柔軟 | 中 | Playwright: 70k+ |
| 3 | **Anthropic Computer Use** | API（従量課金） | $3～$15/M tokens | ✅ 公式SDK | ✅ スクリーンベース | ✅ Bedrock経由 | 低～中 | N/A（API） |
| 4 | **Bedrock AgentCore Browser** | AWSマネージド | 従量課金（秒単位） | ✅ Strands SDK | ✅ 組み込み | ✅ ネイティブ | 低 | N/A（AWS） |
| 5 | **Skyvern** | OSS + クラウド | 無料（セルフホスト） | ✅ Python 3.11 | ✅ Vision LLM | ✅ Bedrock対応 | 中 | ~20k |
| 6 | **AgentQL** | SaaS | Free/$99/月～ | ✅ SDK提供 | 間接的 | 間接的 | 低 | ~数千 |
| 7 | **Steel Browser** | OSS + クラウド | 無料100h/月～ | ✅ SDK提供 | ✅ APIで取得 | 柔軟 | 低 | ~6k |
| 8 | **Stagehand（Browserbase）** | SaaS | Free/$20～$99/月 | TypeScript主体 | ✅ | 間接的 | 中 | ~10k |
| 9 | **Anchor Browser** | SaaS | $0.01/step + $8/GB | 任意言語 | ✅ | 柔軟 | 低～中 | N/A（商用） |
| 10 | **Playwright MCP** | OSS（Microsoft） | 無料（モデル費用のみ） | Python/TS | アクセシビリティツリー | 間接的 | 中 | N/A（Microsoft） |
| 11 | **Selenium + LLM Vision** | 自前構成（OSS） | 無料（モデル費用のみ） | ✅ 完全 | ✅ | 柔軟 | 高 | Selenium: 30k+ |

**Nova Actとの比較**:
- Nova Act: $4.75/時間、us-east-1のみ、Chromiumのみ
- 上記候補はすべてリージョン制約なし（Bedrock AgentCoreは東京含む9リージョン）

---

## 2. 各候補の詳細説明

---

### 2-1. browser-use（最有力候補）

**概要**: PlaywrightベースのPythonライブラリ。LLMにブラウザを操作させるためのOSSフレームワーク。2025年初頭にGitHubトレンド1位を獲得し、急速に普及。

**仕組み**:
- DOMを構造化フォーマットに変換しLLMへ渡す
- スクリーンショット + アクセシビリティツリーを組み合わせた入力
- アクションはPydantic v2モデルで型安全に処理
- BU 2.0（2026/01/27リリース）でWebVoyager精度83.3%達成

**コスト**:
- ライブラリ自体は無料
- LLMモデル費用のみ（ClaudeやBedrock経由で利用可能）
- クラウド版（cloud.browser-use.com）は有料オプション

**Python実装例**:
```python
from browser_use import Agent
from langchain_aws import ChatBedrock

# Amazon Bedrockのモデルを使用（東京リージョン可）
llm = ChatBedrock(
    model_id="anthropic.claude-3-5-sonnet-20241022-v2:0",
    region_name="ap-northeast-1",  # 東京リージョン
)

agent = Agent(
    task="AWSコンソールにログインして、EC2インスタンス一覧のスクリーンショットを取得してください",
    llm=llm,
)

# 実行
result = await agent.run()

# スクリーンショットの取得
# agent.browser.page.screenshot(path="aws_console.png")
```

**認証済みセッションの扱い**:
```python
from browser_use import Agent, BrowserConfig, Browser

# 既存のセッション/Cookieを使用
browser = Browser(
    config=BrowserConfig(
        # 既存のChromeプロファイルを使用してAWSセッションを引き継ぐ
        chrome_instance_path="/path/to/chrome",
    )
)

agent = Agent(task="...", llm=llm, browser=browser)
```

**制限・注意点**:
- SPAの複雑なJavaScriptアプリ（AWSコンソール）でも動作するが、画面遷移が多い場合はトークン消費が増える
- 機密操作（AWSコンソール）では専用VPC/サンドボックス内での実行を推奨

**コミュニティ**: 60k+スター、BU 2.0まで継続的リリース、2026年最もホットなGitHubリポジトリの1つ

---

### 2-2. Playwright + LLM Vision（自前構成）

**概要**: Microsoftが開発するブラウザ自動化フレームワーク（Playwright）に、Claudeのマルチモーダル能力を組み合わせる自前構成。最も柔軟性が高い。

**仕組み**:
- Playwrightでブラウザを精密に制御
- スクリーンショットをClaudeに渡して「次のアクション」を判断させる
- 手順書生成もClaudeが担当（End-to-End統合）

**Python実装例（Runbook自動化向け）**:
```python
import asyncio
import base64
import anthropic
from playwright.async_api import async_playwright

client = anthropic.AnthropicBedrock(
    aws_region="ap-northeast-1",  # 東京リージョン
)

async def capture_and_analyze(page, step_description):
    """スクリーンショット取得 → Claudeで分析 → 次アクション決定"""

    # スクリーンショット取得
    screenshot = await page.screenshot()
    screenshot_b64 = base64.b64encode(screenshot).decode()

    # Claudeに画像を渡して分析
    response = client.messages.create(
        model="anthropic.claude-3-5-sonnet-20241022-v2:0",
        max_tokens=1024,
        messages=[{
            "role": "user",
            "content": [
                {
                    "type": "image",
                    "source": {
                        "type": "base64",
                        "media_type": "image/png",
                        "data": screenshot_b64,
                    },
                },
                {
                    "type": "text",
                    "text": f"""
                    現在の画面を確認して、手順書を生成してください。
                    手順: {step_description}

                    出力形式:
                    1. 現在の画面状態
                    2. 次に行うべき操作
                    3. 手順書テキスト（Markdown形式）
                    """
                }
            ],
        }]
    )
    return response.content[0].text

async def automate_aws_console():
    async with async_playwright() as p:
        # 既存のブラウザセッション（認証済み）を使用
        browser = await p.chromium.connect_over_cdp("http://localhost:9222")
        page = browser.contexts[0].pages[0]

        # AWSコンソールのEC2ページへ遷移
        await page.goto("https://ap-northeast-1.console.aws.amazon.com/ec2/")
        await page.wait_for_load_state("networkidle")

        # スクリーンショット取得・分析
        analysis = await capture_and_analyze(page, "EC2インスタンス一覧を確認する")
        print(analysis)

asyncio.run(automate_aws_console())
```

**認証済みセッション**:
- `playwright.chromium.connect_over_cdp("http://localhost:9222")` で起動中のChrome（AWS SSO済み）に接続可能
- セッションCookieをJSONでエクスポート/インポートする方法も使える

**制限・注意点**:
- 実装工数がかかる（自前でループ/エラーハンドリング/リトライを実装）
- ただし最もカスタマイズ性が高い

---

### 2-3. Anthropic Computer Use（API）

**概要**: Anthropicが提供するβ機能。Claudeがスクリーンショットを見て、マウス・キーボード操作を決定し実行する。Amazon Bedrock経由で東京リージョンから利用可能。

**仕組み**:
- `computer_20251124` ツールを使用
- Claudeがスクリーンを認識 → アクション（クリック/タイプ）を返す → 実行 → スクリーンショット → ループ
- Claude Sonnet 4.6でハルシネーション率が大幅改善（リンクハルシネーション: 1/3 → 0）

**Python実装例（Bedrock経由）**:
```python
import anthropic
import subprocess
import base64

# Amazon Bedrock経由（東京リージョン）
client = anthropic.AnthropicBedrock(
    aws_region="ap-northeast-1",
)

def run_computer_use_loop(task: str):
    messages = [{"role": "user", "content": task}]

    while True:
        response = client.beta.messages.create(
            model="anthropic.claude-sonnet-4-5-20250514-v1:0",
            max_tokens=4096,
            tools=[
                {
                    "type": "computer_20251124",
                    "name": "computer",
                    "display_width_px": 1920,
                    "display_height_px": 1080,
                    "display_number": 1,
                },
            ],
            messages=messages,
            betas=["computer-use-2025-11-24"],
        )

        # ツール実行結果を処理
        # (スクリーンショット取得、マウス操作実行等)

        if response.stop_reason == "end_turn":
            break

    return response

# 使用例
result = run_computer_use_loop(
    "AWSコンソールでEC2のインスタンス一覧を開いて、スクリーンショットを取得してください"
)
```

**コスト目安（Claude Sonnet 3.5 via Bedrock）**:
- 入力: $3/1Mトークン
- 出力: $15/1Mトークン
- スクリーンショット1枚: 約1,000〜3,000トークン（画像サイズによる）

**制限・注意点**:
- Dockerコンテナ内でのVNC/仮想デスクトップ環境が必要
- 実行速度はやや遅い（スクリーンショット → LLM推論のループ）
- 公式リファレンス実装あり（anthropics/claude-quickstarts）

---

### 2-4. Amazon Bedrock AgentCore Browser（AWS純正）

**概要**: AWSが2025年7月プレビュー、同年10月GAリリースしたマネージドブラウザツール。Bedrock AgentCore内の組み込みツールとして提供。東京含む9リージョンで利用可能。

**仕組み**:
- コンテナ化されたエフェメラルブラウザ環境をAWSが管理
- Playwright / browser-use / Nova Act SDKから利用可能
- AWS CloudTrailとの統合でセッションログが自動記録される

**Python実装例（Strands SDK）**:
```python
from strands import Agent
from strands_tools.browser import AgentCoreBrowser
from strands.models import BedrockModel
import boto3

# 東京リージョンのBedrockモデル
bedrock_session = boto3.Session(region_name="ap-northeast-1")
model = BedrockModel(
    model_id="anthropic.claude-3-5-sonnet-20241022-v2:0",
    boto_session=bedrock_session
)

# AgentCore Browserツールの初期化
browser_tool = AgentCoreBrowser(region="ap-northeast-1")

# エージェント作成
agent = Agent(
    model=model,
    tools=[browser_tool.browser]
)

# 実行
response = agent(
    "AWSコンソールにアクセスして、EC2インスタンスの状態を確認し、手順書を生成してください"
)
print(response.message["content"][0]["text"])
```

**コスト**:
- CPUとメモリの使用量に応じた秒単位課金
- I/O待機時（LLM推論中）はCPUチャージなし → 実質コストはかなり低い
- 月10Mリクエストのカスタマーサポートエージェント例: ~$7,625/月

**制限・注意点**:
- Strands SDKの学習が必要
- Nova Actとの組み合わせが公式推奨だが、browser-useも対応

---

### 2-5. Skyvern

**概要**: LLMとコンピュータビジョンを組み合わせたブラウザ自動化ツール。AGPL-3.0ライセンスのOSS。スクリーンショット → Vision LLMで要素を特定するアプローチ。

**Python実装例**:
```python
from skyvern import Skyvern

client = Skyvern(api_key="your-api-key")  # クラウド版
# または: セルフホスト版（pip install skyvern && skyvern quickstart）

# タスク実行
task = await client.agent.create_task(
    url="https://ap-northeast-1.console.aws.amazon.com/ec2/",
    navigation_goal="EC2インスタンス一覧を確認してスクリーンショットを取得する",
    llm_config={
        "provider": "BEDROCK",
        "model": "anthropic.claude-3-5-sonnet-20241022-v2:0",
    }
)
```

**制限・注意点**:
- Python 3.11必須
- AGPL-3.0ライセンス（商用利用時は確認必要）
- AWSコンソールのような複雑なSPAでは精度が下がる場合がある
- セルフホストはリソース消費が大きい

---

### 2-6. AgentQL

**概要**: 自然言語クエリでWebページの要素を特定する独自クエリ言語を持つツール。Playwright上で動作するPython SDKを提供。セレクターが壊れにくい。

**Python実装例**:
```python
import agentql
from playwright.sync_api import sync_playwright

with sync_playwright() as playwright:
    browser = playwright.chromium.launch(headless=False)
    page = agentql.wrap(browser.new_page())  # AgentQLでラップ

    page.goto("https://ap-northeast-1.console.aws.amazon.com/ec2/")

    # 自然言語クエリでEC2インスタンス一覧を取得
    QUERY = """
    {
        instances_table {
            instance_rows[] {
                instance_id
                state
                instance_type
            }
        }
    }
    """
    response = page.query_elements(QUERY)

    # スクリーンショット
    page.screenshot(path="ec2_instances.png")
```

**コスト**: 無料300 API calls → $99/月（Professional）

**制限・注意点**:
- 主にデータ抽出・スクレイピング用途で最適化
- 完全自律エージェントよりも「人間が手順を定義 → AI要素特定」の半自動に向いている

---

### 2-7. Steel Browser

**概要**: AIエージェント向けのヘッドレスブラウザAPI。セルフホスト可能なOSS版とクラウド版を提供。月100時間無料。

**Python実装例**:
```python
from steel import Steel
import anthropic

steel_client = Steel(steel_api_key="your_api_key")

# ブラウザセッション作成
session = steel_client.sessions.create()

# Playwrightで接続
from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    browser = p.chromium.connect_over_cdp(session.websocket_url)
    page = browser.contexts[0].pages[0]

    page.goto("https://ap-northeast-1.console.aws.amazon.com/ec2/")

    # スクリーンショット取得
    screenshot_bytes = page.screenshot()

    # Claudeに渡して分析
    client = anthropic.AnthropicBedrock(aws_region="ap-northeast-1")
    # ... (Playwright + LLM Vision と同様の処理)

    # セッション終了
    steel_client.sessions.release(session.id)
```

**制限・注意点**:
- GitHubスター: ~6k（まだ成長途中）
- エンタープライズ向けの機能は発展途上

---

### 2-8. Stagehand（Browserbase）

**概要**: Browserbaseが開発するAIブラウザ自動化フレームワーク。Playwright上に`act/extract/observe`という自然言語プリミティブを追加。TypeScript主体。

**Python対応**: 公式Python SDKあり（`stagehand` パッケージ）
**コスト**: Browserbase $20〜$99/月

**制限・注意点**:
- TypeScriptが主体。PythonはCanonical Stagehand API経由
- Browserbaseのインフラに依存

---

### 2-9. Anchor Browser

**概要**: イスラエルのスタートアップが開発するエンタープライズ向けクラウドブラウザ。最大50,000並列ブラウザ、CAPTCHA解除、Okta/Azure AD統合。

**コスト**: $0.01/step + $8/GB（AWSマーケットプレイス経由も可）
**制限・注意点**: 商用SaaSのみ、セルフホスト不可、新興サービスで実績が少ない

---

### 2-10. Playwright MCP（Microsoft）

**概要**: MicrosoftがリリースしたPlaywright向けのMCPサーバー。LLMがアクセシビリティツリーを通じてブラウザを制御。スクリーンショット不要で軽量。

**特徴**:
- アクセシビリティツリー使用（スクリーンショットなし）: 2〜5KB/リクエスト
- スクリーンショット方式: 500KB〜2MB/リクエスト（10〜100x遅い）
- 25+のブラウザ操作ツールをMCP経由で提供

**制限・注意点**:
- Runbook手順書生成には「見た目」のスクリーンショットが必要なため、本プロジェクトではVision Modeが必要
- Claude Code / Cursor等のMCPクライアントとの統合には強い

---

### 2-11. Selenium + LLM Vision（自前構成）

**概要**: 従来のSeleniumに、スクリーンショット → Claude分析を組み合わせる構成。最も枯れた技術だが実装コストが高い。

**制限・注意点**:
- 非同期処理・ウェイト管理がPlaywrightより複雑
- AWSのSPA環境での安定性はPlaywrightより低い傾向
- SeleniumBase（拡張ライブラリ）でかなり改善可能

---

## 3. Runbook自動化プロジェクトへの推奨度ランキング

### 前提条件の整理

| 要件 | 詳細 |
|------|------|
| 対象 | AWSコンソール（複雑なSPA） |
| 操作 | ブラウザ自動化 + スクリーンショット取得 |
| AI統合 | Amazon Bedrock / Claude で手順書生成 |
| 言語 | Python |
| リージョン | 東京（ap-northeast-1）中心 |
| Nova Act問題 | コスト高・us-east-1制約 |

---

### 推奨ランキング

#### 1位: Playwright + LLM Vision（自前構成）★★★★★

**理由**:
- AWSコンソール（SPA）との相性が最高。Playwrightはネットワーク待機・動的コンテンツに強い
- スクリーンショットを完全にコントロールできる（手順書の各ステップ画像として使える）
- Bedrock + Claude への統合が直接的で、東京リージョンそのまま使える
- 認証済みセッション（既存のChromeプロファイル / Cookieエクスポート）も自在に扱える
- コスト: LLMトークン費用のみ（Nova Actの$4.75/hゼロ）
- 実装コストはかかるが、`03_PROJECTS/runbook_automation/src/` に既存コードがある

**推奨構成**:
```
Playwright（ブラウザ制御・スクリーンショット）
    ↓ 画像 + テキスト
Claude claude-3-5-sonnet via Bedrock（東京）
    ↓ 手順書Markdown
出力ファイル保存
```

---

#### 2位: browser-use ★★★★☆

**理由**:
- Playwrightをラップしており、LLMとの統合が既にできている
- Bedrock + Claudeとの組み合わせが公式でサポートされている
- BU 2.0で精度83.3%（2026/01時点）
- Nova Actより自律度が高く、複雑な操作フローを自然言語で指示できる
- セルフホストなのでリージョン制約なし

**注意**: AWSコンソールのような機密環境では、エージェントの自律判断がどこまで許容されるか要確認。

---

#### 3位: Amazon Bedrock AgentCore Browser ★★★★☆

**理由**:
- AWS純正のため、AWSコンソール操作との相性が良い
- CloudTrailログ統合で監査証跡が取れる（エンタープライズ要件に適合）
- 東京リージョン含む9リージョンで利用可能（Nova Actのリージョン制約を完全解消）
- 秒単位課金でI/O待機中は無課金（実コストはNova Actより大幅に安い）
- Nova Act / browser-use の両方を呼び出せるフレキシブルな構造

**注意**: Strands SDKの習熟が必要。まだ比較的新しいサービス（GA: 2025/10）。

---

#### 4位: Anthropic Computer Use ★★★☆☆

**理由**:
- Claude Sonnet 4.6でリンクハルシネーションがゼロ化され、信頼性が大幅向上
- Bedrock経由で東京リージョンから利用可能
- AWSコンソールのような複雑なUIでも「見て操作する」ため適応力が高い

**注意**: 仮想デスクトップ（Docker + VNC）環境の構築が必要。速度は遅め。既存の`poc/`コードとの整合性を確認してから採用を検討。

---

#### 5位: Skyvern ★★★☆☆

**理由**:
- Vision LLMによる画面認識でXPath等の破損リスクがない
- Bedrock（Claude）との統合サポートあり
- セルフホスト可能

**注意**: AGPL-3.0ライセンス（商用利用時に確認必要）。Python 3.11固定。AWSコンソールのような複雑なSPAで精度が落ちる報告あり。

---

#### 6位以下（参考）

| 順位 | ツール | 理由 |
|------|--------|------|
| 6 | Steel Browser | インフラ隠蔽に便利だが、スター数少なくまだ成熟途中 |
| 7 | AgentQL | データ抽出には強いが、完全自律エージェントには向かない |
| 8 | Playwright MCP | スクリーンショット取得がメイン用途に合わない（アクセシビリティツリー主体） |
| 9 | Stagehand | Python主体でないため採用コスト高 |
| 10 | Anchor Browser | エンタープライズ向けだが商用SaaSのみ、実績が少ない |
| 11 | Selenium + LLM | 技術的に可能だが、PlaywrightよりSPA対応が弱い |

---

## 4. 最終推奨アクション

### 短期（今週）: Playwright + LLM Vision で PoC 実装

```bash
pip install playwright anthropic boto3
playwright install chromium
```

1. 既存の `03_PROJECTS/runbook_automation/poc/` に Playwright + Claude（Bedrock）の基本ループを実装
2. AWSコンソールの1ステップ（例: EC2一覧表示）でスクリーンショット → Claude → Markdown手順書を確認
3. 認証セッションの持ち込み方法（CDPアタッチ or Cookie注入）を確立

### 中期（来月）: browser-use で高度化

browser-useを導入し、「スクリーンショット自動撮影 + 手順書生成」をエージェント化。自然言語タスク指定で手順書を自動生成するデモを作る。

### 長期（要件次第）: Bedrock AgentCore Browser への移行

エンタープライズ運用・監査証跡が必要になったタイミングで、Bedrock AgentCore Browserへ移行。Nova ActはAWS純正の選択肢として残しつつ、コストとリージョン制約の解消を確認してから再評価。

---

## 参考リンク

- [browser-use GitHub](https://github.com/browser-use/browser-use)
- [browser-use BU 2.0 リリース](https://browser-use.com/changelog)
- [Browserbase / Stagehand](https://github.com/browserbase/stagehand)
- [Skyvern GitHub](https://github.com/Skyvern-AI/skyvern)
- [Steel Browser GitHub](https://github.com/steel-dev/steel-browser)
- [Playwright MCP GitHub](https://github.com/microsoft/playwright-mcp)
- [AgentQL](https://www.agentql.com)
- [Anchor Browser](https://anchorbrowser.io)
- [Anthropic Computer Use API Docs](https://platform.claude.com/docs/en/agents-and-tools/tool-use/computer-use-tool)
- [Amazon Bedrock AgentCore Browser](https://aws.amazon.com/blogs/machine-learning/introducing-amazon-bedrock-agentcore-browser-tool/)
- [Amazon Bedrock AgentCore Pricing](https://aws.amazon.com/bedrock/agentcore/pricing/)
- [Nova Act GitHub](https://github.com/aws/nova-act)
