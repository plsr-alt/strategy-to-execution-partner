#!/usr/bin/env python3
"""既存YouTube動画を全削除 → v5パイプラインで1本生成"""
import json
import sys
from pathlib import Path

# === Step 1: 既存動画を全削除 ===
def delete_all_videos():
    from googleapiclient.discovery import build
    from google.oauth2.credentials import Credentials
    import google.auth.transport.requests

    SCOPES = ["https://www.googleapis.com/auth/youtube"]
    TOKEN_FILE = Path("/home/ec2-user/youtube_automation/token.json")

    if not TOKEN_FILE.exists():
        print("ERROR: token.json not found")
        return

    creds = Credentials.from_authorized_user_file(str(TOKEN_FILE), SCOPES)
    if not creds.valid:
        if creds.expired and creds.refresh_token:
            creds.refresh(google.auth.transport.requests.Request())
            TOKEN_FILE.write_text(creds.to_json())

    youtube = build("youtube", "v3", credentials=creds)

    # 自分のチャンネルの動画を一覧
    deleted = 0
    next_page = None
    while True:
        request = youtube.search().list(
            part="id",
            forMine=True,
            type="video",
            maxResults=50,
            pageToken=next_page
        )
        response = request.execute()

        for item in response.get("items", []):
            video_id = item["id"]["videoId"]
            try:
                youtube.videos().delete(id=video_id).execute()
                print(f"  DELETED: {video_id}")
                deleted += 1
            except Exception as e:
                print(f"  FAILED to delete {video_id}: {e}")

        next_page = response.get("nextPageToken")
        if not next_page:
            break

    print(f"\n=== {deleted} videos deleted ===\n")


if __name__ == "__main__":
    print("=" * 50)
    print("Step 1: Deleting all existing YouTube videos...")
    print("=" * 50)
    delete_all_videos()

    print("=" * 50)
    print("Step 2: Running pipeline v5 (1 video)...")
    print("=" * 50)

    # パイプラインを実行
    sys.path.insert(0, "/home/ec2-user/youtube_automation")
    from youtube_pipeline import YouTubeAutomationPipeline, setup_logging, validate_dependencies, validate_env_vars
    import logging

    logger = setup_logging("/home/ec2-user/youtube_automation/out/v5_run.log")
    logger.info("v5 Pipeline starting...")

    if not validate_dependencies():
        sys.exit(1)
    if not validate_env_vars():
        sys.exit(1)

    pipeline = YouTubeAutomationPipeline(theme_mode="finance")
    success = pipeline.run()

    if success:
        print("\n=== SUCCESS: 1 video generated and uploaded ===")
    else:
        print("\n=== FAILED: pipeline error ===")
        sys.exit(1)
