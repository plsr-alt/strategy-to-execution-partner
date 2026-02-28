import boto3
import json
import logging
import base64
from typing import List, Optional

logger = logging.getLogger(__name__)

class DocGenerator:
    def __init__(self, use_mock: bool = False):
        self.use_mock = use_mock
        if not use_mock:
            self.client = boto3.client('bedrock-runtime')

    def generate_step_description(self, image_paths: List[str]) -> str:
        """
        Generate a runbook-style documentation from a list of screenshots.
        """
        if self.use_mock:
            logger.info(f"[MOCK] Generating documentation for {len(image_paths)} images")
            return """# AWS EC2 作成手順書 (自動生成)

## 概要
本資料は、実際の操作キャプチャを元に AI によって自動生成されました。

## 手順
1. **EC2 インスタンスの起動設定**
   - コンソールより「インスタンスを起動」を選択。
   - 名前: `my-web-server`
   - AMI: `Amazon Linux 2023`
   - インスタンスタイプ: `t3.micro`

2. **ネットワーク・セキュリティ設定**
   - セキュリティグループ: `launch-wizard-1`
   - 許可ポート: 22 (SSH), 80 (HTTP)

3. **起動確認**
   - インスタンスステータスが「実行中」であることを確認。
"""

        # Multimodal Prompt for Claude 3.5
        content = []
        for path in image_paths:
            with open(path, "rb") as f:
                img_data = base64.b64encode(f.read()).decode("utf-8")
                content.append({
                    "type": "image",
                    "source": {
                        "type": "base64",
                        "media_type": "image/png", # Assuming PNG/JPG based on extension
                        "data": img_data
                    }
                })
        
        system_prompt = """
あなたは、ITインフラ構築のインシデント対応や定常作業の「手順書（ランブック）」を作成する専門家です。
提供されたスクリーンショット群を時系列順に解析し、誰が読んでも再現可能な高精度な手順書を作成してください。

【構成案】
1. タイトル（何の手順か）
2. 概要（この作業の目的とゴール）
3. 事前準備（必要な権限、ツール、パラメータ等）
4. 作業手順（各ステップごとの詳細）
   - 各ステップには「何を」「どのように」「なぜ」行うかを記述
   - 設定した値（インスタンス名、ID等）を明記
5. 確認項目（作業が正しく完了したことをどう確認するか）
6. 注意事項（ハマりポイントや制限事項）

【トーン】
- 日本語で、丁寧かつ簡潔なITエンジニアらしいスタイル
- 専門用語は適切に使用
"""

        user_prompt = "これらのスクリーンショットは作業の記録です。これらを元に、上記構成案に従ったMarkdown形式の手順書を生成してください。"

        # In Bedrock, you would send this to the model...
        # Body would include messages with content list
        
        return "LIVE_GENERATION_PLACEHOLDER"
