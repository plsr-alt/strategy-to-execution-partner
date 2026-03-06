#!/usr/bin/env python3
# ============================================================
# Groq Executor — Phase 2 自動実装スクリプト
# ============================================================
# 役割: Groq API を呼び出して、Step 1-8 の実装コードを自動生成
# 実行: python3 groq_executor.py
# 出力: youtube_pipeline.py に実装コードを統合

import os
import json
import logging
from pathlib import Path
from groq import Groq
from dotenv import load_dotenv

# ============================================================
# 設定
# ============================================================

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
if not GROQ_API_KEY:
    print("❌ GROQ_API_KEY が設定されていません")
    exit(1)

client = Groq(api_key=GROQ_API_KEY)

# ログ設定
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] [%(levelname)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

# パイプラインパス
PIPELINE_PATH = Path(__file__).parent / "youtube_pipeline.py"

# ============================================================
# プロンプトテンプレート
# ============================================================

PROMPTS = {
    "step1": """
You are a Python expert. Implement the following function for YouTube video automation.

Function: generate_theme(theme_mode: str = "auto") -> dict

Requirements:
- Use Groq API to analyze trends and generate video themes
- Return dict with: theme, keywords (list), hook, duration_min, category
- Handle theme_mode: "auto", "finance", "tech", "business"
- Include error handling and logging
- Return JSON format response

Context:
- Target audience: Japanese salarymen
- Platform: YouTube
- Use Groq Llama 3.1

Return ONLY valid Python code (no markdown, no explanation):
""",

    "step2": """
You are a Python expert. Implement the following function for YouTube video automation.

Function: generate_script(theme: dict, language: str = "ja") -> str

Requirements:
- Use Groq API to generate YouTube video script
- Script structure: [フック] (0-15s), [本題] (15s-6min, 3-5 points), [CTA] (6-7min)
- Include natural pauses (indicated by ellipsis)
- Return formatted script string
- Include error handling and logging
- Use Groq Llama 3.1 model

Context:
- Video duration: 8-12 minutes
- Language: {language}
- Tone: Engaging, conversational

Return ONLY valid Python code (no markdown, no explanation):
""",

    "step3": """
You are a Python expert. Implement the following function for YouTube video automation.

Function: generate_voiceover(script: str, voicevox_url: str = "http://localhost:50021") -> str

Requirements:
- Use VOICEVOX API to convert script to audio (Japanese TTS)
- Speaker: 0 (初音ミク), Speed: 1.2x
- Return path to generated WAV file
- Handle API errors gracefully
- Save to: /home/ec2-user/task/tmp/voiceover_YYYYMMDD_HHMMSS.wav
- Include timeout (30s per sentence)

Context:
- VOICEVOX endpoint: POST /audio_query, POST /synthesis
- Split script into sentences for processing
- Concatenate audio clips using pydub

Return ONLY valid Python code (no markdown, no explanation):
""",

    "step4": """
You are a Python expert. Implement the following function for YouTube video automation.

Function: collect_footage(keywords: list, num_clips: int = 5) -> list
Function: generate_infographics(theme: dict) -> list

Requirements for collect_footage:
- Use Pexels API to search and download video clips
- Return list of dicts: [{"path": "...", "duration": 10.5}, ...]
- Save to: /home/ec2-user/task/tmp/
- Handle Pexels API errors and fallback to infographics generation

Requirements for generate_infographics:
- Use matplotlib + Pillow to generate chart/slide images
- Create: bar charts, comparison slides, point summary
- Image size: 1280x720px, 16:9 ratio
- Return list of image paths with durations
- Use Japanese font (Noto Sans JP if available)

Context:
- Pexels API endpoint: GET /videos/search
- Fallback if no videos found: generate info graphics

Return ONLY valid Python code (no markdown, no explanation):
""",

    "step5": """
You are a Python expert. Implement the following function for YouTube video automation.

Function: edit_video(footage: list, voiceover_path: str, script: str, output_path: str) -> str

Requirements:
- Use moviepy to concatenate video clips and add audio
- Generate SRT subtitle file from script
- Call video_auto_edit subprocess: /home/ec2-user/task/03_PROJECTS/video_auto_edit/main.py
- Return final video path
- Include comprehensive error handling
- Handle subtitle timing from script structure

Context:
- Output directory: /home/ec2-user/task/out/
- SRT format: timestamp --> text
- video_auto_edit parameters: --input, --config
- Processing time estimate: 5-10 minutes

Return ONLY valid Python code (no markdown, no explanation):
""",

    "step6": """
You are a Python expert. Implement the following function for YouTube video automation.

Function: generate_thumbnail(theme: dict, output_path: str) -> str

Requirements:
- Use Pillow (PIL) to create YouTube thumbnail
- Size: 1280x720px
- Add theme text with: white font + black outline
- Use bold Japanese font (Noto Sans JP)
- Font size: 48, bold
- Color: white (#FFFFFF) with black outline
- Position: center, lower half
- Save as PNG
- Include fallback if template not found

Context:
- Template path: /home/ec2-user/task/03_PROJECTS/youtube_automation/assets/thumbnail_template.png
- If template missing: create simple background + text
- Text: 3-5 words from theme

Return ONLY valid Python code (no markdown, no explanation):
""",

    "step7": """
You are a Python expert. Implement the following function for YouTube video automation.

Function: optimize_metadata(theme: dict, script: str) -> dict

Requirements:
- Use Groq API to optimize YouTube metadata for SEO
- Generate: title (50 chars max), description (500 chars max), tags (max 15)
- Title must include main keyword in first 5 words
- Description include 2ndary keywords and links
- Tags: 3 large-scale + 5 medium + 7 specific
- Return dict with: title, description, tags, category

Context:
- Target: Japanese salarymen
- Platform: YouTube Education category
- Use Groq Llama 3.1 for optimization
- Focus on CTR (click-through rate)

Return ONLY valid Python code (no markdown, no explanation):
""",

    "step8": """
You are a Python expert. Implement the following function for YouTube video automation.

Function: upload_to_youtube(video_path: str, metadata: dict, thumbnail_path: str, publish_mode: str = "SCHEDULE") -> str

Requirements:
- Use YouTube Data API v3 to upload video
- OAuth authentication from YOUTUBE_API_KEY in .env
- Resumable upload for large files
- Set metadata: title, description, tags, category
- Set thumbnail from file
- Publish mode: "SCHEDULE" (next day 6AM JST), "PRIVATE", "PUBLIC"
- Return video_id
- Include comprehensive error handling

Context:
- API scopes: https://www.googleapis.com/auth/youtube.upload
- Timezone: Asia/Tokyo (JST)
- Video category: Education (22)
- Status: uploaded (SCHEDULE), private, or public

Return ONLY valid Python code (no markdown, no explanation):
""",
}

# ============================================================
# メイン処理
# ============================================================

def generate_step_code(step_num: int, step_name: str) -> str:
    """Groq API を呼び出して、ステップのコードを生成"""
    logger.info(f"🔄 {step_name} を生成中...")

    try:
        message = client.messages.create(
            model="llama-3.1-70b-versatile",
            max_tokens=3000,
            messages=[
                {
                    "role": "user",
                    "content": PROMPTS.get(f"step{step_num}", "Generate Python code")
                }
            ]
        )

        code = message.content[0].text.strip()
        logger.info(f"✅ {step_name} コード生成完了（{len(code)} chars）")
        return code

    except Exception as e:
        logger.error(f"❌ {step_name} 生成エラー: {str(e)}")
        return f"# Error generating {step_name}: {str(e)}\npass"


def update_pipeline(step_num: int, code: str) -> bool:
    """youtube_pipeline.py の該当ステップを更新"""

    try:
        with open(PIPELINE_PATH, 'r', encoding='utf-8') as f:
            content = f.read()

        # 置換対象: _step_generate_xxx の関数内容
        step_methods = {
            1: "_step_generate_theme",
            2: "_step_generate_script",
            3: "_step_generate_voiceover",
            4: "_step_collect_footage",
            5: "_step_edit_video",
            6: "_step_generate_thumbnail",
            7: "_step_optimize_metadata",
            8: "_step_upload_to_youtube",
        }

        method_name = step_methods[step_num]

        # 関数内の TODO コメントを実装コードに置換
        # パターン: def _step_xxx(self): ... logger.info(...) まで

        import re
        pattern = rf'(def {method_name}\(self\):.*?)(logger\.info\("   🔄.*?\n.*?logger\.info\("   ✅.*?\n)'
        replacement = rf'\1{code}\n\n        '

        updated_content = re.sub(pattern, replacement, content, flags=re.DOTALL)

        if updated_content == content:
            logger.warning(f"⚠️ {method_name} パターンマッチ失敗。手動確認が必要です。")
            return False

        with open(PIPELINE_PATH, 'w', encoding='utf-8') as f:
            f.write(updated_content)

        logger.info(f"✅ youtube_pipeline.py を更新しました（Step {step_num}）")
        return True

    except Exception as e:
        logger.error(f"❌ ファイル更新エラー: {str(e)}")
        return False


def main():
    """メイン処理"""

    logger.info("=" * 60)
    logger.info("🚀 Groq Executor — Phase 2 自動実装開始")
    logger.info("=" * 60)

    steps = [
        (1, "Step 1: 企画エンジン（トレンド分析）"),
        (2, "Step 2: 台本生成"),
        (3, "Step 3: 音声生成"),
        (4, "Step 4: 映像素材収集"),
        (5, "Step 5: 動画編集"),
        (6, "Step 6: サムネイル生成"),
        (7, "Step 7: メタデータ最適化"),
        (8, "Step 8: YouTube アップロード"),
    ]

    results = {}

    for step_num, step_name in steps:
        logger.info(f"\n📋 {step_name}")

        # コード生成
        code = generate_step_code(step_num, step_name)
        results[step_num] = {"name": step_name, "code": code}

        # パイプライン更新（オプション）
        # update_pipeline(step_num, code)

    # 結果をログファイルに保存
    log_path = Path(__file__).parent / "groq_implementation_output.json"
    with open(log_path, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    logger.info(f"\n✅ すべてのステップを生成完了！")
    logger.info(f"📁 出力: {log_path}")
    logger.info("\n次のステップ:")
    logger.info("1. groq_implementation_output.json を確認")
    logger.info("2. 各ステップのコードを youtube_pipeline.py に手動統合")
    logger.info("3. テスト実行: python youtube_pipeline.py --theme finance")

    return 0


if __name__ == "__main__":
    exit(main())
