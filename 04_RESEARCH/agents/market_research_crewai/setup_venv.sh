#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
echo "=== セットアップ開始: $SCRIPT_DIR ==="

echo "--- venv 作成 ---"
python3 -m venv "$SCRIPT_DIR/.venv"

echo "--- pip アップグレード ---"
"$SCRIPT_DIR/.venv/bin/pip" install --upgrade pip -q

echo "--- パッケージインストール ---"
"$SCRIPT_DIR/.venv/bin/pip" install crewai crewai-tools python-dotenv -q

echo "--- バージョン確認 ---"
"$SCRIPT_DIR/.venv/bin/python" -c "
import crewai, dotenv
from crewai_tools import DuckDuckGoSearchRun
print('crewai         :', crewai.__version__)
print('python-dotenv  : OK')
print('DuckDuckGoSearch: OK')
"
echo "=== セットアップ完了 ==="
