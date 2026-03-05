#!/usr/bin/env python3
"""
YouTube OAuth トークン生成スクリプト（ローカルPC用）
===================================================
ブラウザが使えるローカルPCで実行し、token.json を生成する。
生成後、EC2 に SCP でコピーする。

Usage:
    python generate_token.py
    python generate_token.py --client-secret /path/to/client_secret.json
    python generate_token.py --output /path/to/token.json

生成後:
    scp token.json ec2-user@<EC2_IP>:/home/ec2-user/task/03_PROJECTS/youtube_automation/
"""

import argparse
import sys
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(description="YouTube OAuth トークン生成")
    parser.add_argument(
        "--client-secret",
        default="client_secret.json",
        help="Google Cloud の client_secret.json パス (default: client_secret.json)",
    )
    parser.add_argument(
        "--output",
        default="token.json",
        help="出力先 token.json パス (default: token.json)",
    )
    args = parser.parse_args()

    client_secret = Path(args.client_secret)
    output_path = Path(args.output)

    if not client_secret.exists():
        print(f"[ERROR] client_secret.json が見つかりません: {client_secret}")
        print("Google Cloud Console からダウンロードしてください:")
        print("  https://console.cloud.google.com/apis/credentials")
        sys.exit(1)

    try:
        from google.oauth2.credentials import Credentials
        from google_auth_oauthlib.flow import InstalledAppFlow
    except ImportError:
        print("[ERROR] 必要なパッケージをインストールしてください:")
        print("  pip install google-auth google-auth-oauthlib google-api-python-client")
        sys.exit(1)

    SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]

    # 既存トークンの確認
    if output_path.exists():
        creds = Credentials.from_authorized_user_file(str(output_path), SCOPES)
        if creds and creds.valid:
            print(f"[OK] 既存の有効なトークンがあります: {output_path}")
            return
        if creds and creds.expired and creds.refresh_token:
            import google.auth.transport.requests
            print("[INFO] トークンをリフレッシュ中...")
            creds.refresh(google.auth.transport.requests.Request())
            output_path.write_text(creds.to_json())
            print(f"[OK] トークンをリフレッシュしました: {output_path}")
            return
        print("[INFO] 既存トークンが無効です。再認証します。")

    # OAuth フロー（ブラウザが開く）
    print("[INFO] ブラウザで Google アカウント認証を行います...")
    flow = InstalledAppFlow.from_client_secrets_file(str(client_secret), SCOPES)
    creds = flow.run_local_server(port=8080)

    output_path.write_text(creds.to_json())
    print(f"\n[OK] トークン生成完了: {output_path}")
    print(f"\nEC2 にコピーするコマンド:")
    print(f"  scp {output_path} ec2-user@<EC2_IP>:/home/ec2-user/task/03_PROJECTS/youtube_automation/")


if __name__ == "__main__":
    main()
