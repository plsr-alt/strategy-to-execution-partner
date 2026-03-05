"""
VibeMatch AI PoC テストスクリプト

使い方:
  1. WSLで実行
  2. テスト用の顔写真を用意（自分の写真でOK）
  3. 以下を実行:

  cd /mnt/c/Users/tshibasaki/Desktop/etc/work/task/03_PROJECTS/vibe_match/src/services/ai
  python3 -m venv .venv && source .venv/bin/activate
  pip install open-clip-torch torch Pillow numpy

  python poc_test.py --photo /path/to/photo.jpg

目的:
  - CLIPの印象タグ推定が実用レベルか確認
  - プロンプトのチューニング材料を得る
  - 手動診断の「裏付け」として使う
"""

import argparse
import sys
import time

from PIL import Image


def main():
    parser = argparse.ArgumentParser(description="VibeMatch AI PoC Test")
    parser.add_argument("--photo", required=True, help="テスト用顔写真のパス")
    parser.add_argument("--top_k", type=int, default=5, help="表示するタグ数")
    args = parser.parse_args()

    print("=" * 50)
    print("  VibeMatch AI PoC テスト")
    print("=" * 50)
    print()

    # 画像読み込み
    try:
        image = Image.open(args.photo).convert("RGB")
        print(f"✅ 画像読み込み: {args.photo}")
        print(f"   サイズ: {image.size[0]}x{image.size[1]}")
    except Exception as e:
        print(f"❌ 画像読み込みエラー: {e}")
        sys.exit(1)

    # 顔検出
    print()
    print("🔍 顔検出中...")
    from app.face_detector import FaceDetector
    detector = FaceDetector()
    detector.load()

    detection = detector.detect_and_crop(image)
    print(f"   品質スコア: {detection['quality_score']}/100")
    if detection["issues"]:
        print(f"   ⚠️  問題点: {', '.join(detection['issues'])}")
    if detection["suggestions"]:
        for s in detection["suggestions"]:
            print(f"   💡 {s}")

    if not detection["success"] and detection["face_image"] is None:
        print("❌ 顔が検出できませんでした。別の写真で試してください。")
        sys.exit(1)

    face_image = detection["face_image"]
    print(f"   ✅ 顔クロップ完了: {face_image.size[0]}x{face_image.size[1]}")

    # 印象タグ推定
    print()
    print("🧠 CLIPモデルをロード中（初回は2-3分かかります）...")
    from app.impression_tagger import ImpressionTagger
    tagger = ImpressionTagger()
    tagger.load()

    print("🎯 印象タグを推定中...")
    start = time.time()
    result = tagger.predict(face_image, top_k=args.top_k)
    elapsed = time.time() - start

    # 結果表示
    print()
    print("=" * 50)
    print("  📊 診断結果")
    print("=" * 50)
    print()
    print(f"  総合信頼度: {result['overall_confidence']}%")
    print()
    print("  🏷️  印象タグ Top{0}:".format(args.top_k))
    print("  " + "-" * 40)
    for i, tag in enumerate(result["tags"], 1):
        bar = "█" * int(tag["prob"] * 40)
        print(f"  {i}. {tag['label']:10s} {tag['prob']:.1%} {bar}")
    print()

    print("  💬 説明:")
    for exp in result["explanation"]:
        print(f"    • {exp['text']}")
    print()

    print(f"  ⏱️  推論時間: {elapsed:.2f}秒")
    print()

    # タグベクトル（デバッグ用）
    from app.tags import CATEGORIES
    print("  📐 タグベクトル（8カテゴリ）:")
    for cat, val in zip(CATEGORIES, result["tag_vector"]):
        bar = "█" * int(val * 30)
        print(f"    {cat['label']:12s} {val:.3f} {bar}")
    print()

    # ガードレール確認
    from app.guardrails import validate_output
    validation = validate_output(result["tags"], result["explanation"])
    if validation["is_valid"]:
        print("  ✅ ガードレール: 全チェックOK")
    else:
        print("  ⚠️  ガードレール:")
        for reason in validation["blocked_reasons"]:
            print(f"    ❌ {reason}")

    print()
    print("=" * 50)
    print()
    print("次のステップ:")
    print("  1. 結果が直感と合っているか確認")
    print("  2. 合っていない場合 → tags.py のプロンプトを調整")
    print("  3. 5-10枚で繰り返してチューニング")
    print()


if __name__ == "__main__":
    main()
