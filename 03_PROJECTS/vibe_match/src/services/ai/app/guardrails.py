"""
VibeMatch ガードレール（禁止出力フィルタ）

- 有名人名の出力防止
- 人種/年齢/容姿評価の禁止
- ホワイトリスト方式でタグを制限
"""

from app.tags import TAGS_BY_ID

# ============================================
# 禁止ワードリスト
# ============================================
BANNED_WORDS_JA = [
    # 容姿評価
    "美人", "イケメン", "ブス", "不細工", "ブサイク", "可愛くない",
    "美しい", "醜い", "整形", "点数", "ランク", "偏差値", "スコア",
    # 人種・民族
    "白人", "黒人", "アジア人", "ハーフ", "混血", "外国人顔",
    # 年齢評価
    "老け顔", "おばさん", "おじさん", "老けて", "若作り",
    # 性的
    "セクシー度", "色気度", "エロ",
    # ジェンダー固定
    "男顔", "女顔", "おっさん", "おばちゃん",
]

BANNED_WORDS_EN = [
    "ugly", "beautiful score", "attractive score", "rating",
    "race", "ethnicity", "white", "black", "asian",
    "old looking", "young looking", "age",
    "sexy score", "hotness",
]

# 有名人名リスト（出力に含まれていたらブロック）
# 実運用では外部辞書ファイルから読み込む
CELEBRITY_NAMES = [
    # 日本
    "木村拓哉", "新垣結衣", "橋本環奈", "菅田将暉", "石原さとみ",
    "浜辺美波", "吉沢亮", "広瀬すず", "山崎賢人", "北川景子",
    # 海外
    "Brad Pitt", "Angelina Jolie", "BTS", "Blackpink",
    "Taylor Swift", "Timothee Chalamet",
]


def validate_output(tags: list[dict], explanations: list[dict]) -> dict:
    """
    AI出力のバリデーション。
    ホワイトリスト外のタグ、禁止ワードを含む説明をブロック。

    Returns:
        {
            "is_valid": bool,
            "filtered_tags": list,
            "filtered_explanations": list,
            "blocked_reasons": list[str],
        }
    """
    blocked_reasons = []
    filtered_tags = []
    filtered_explanations = []

    # 1. タグのホワイトリスト検証
    for tag in tags:
        tag_id = tag.get("id", "")
        if tag_id in TAGS_BY_ID:
            filtered_tags.append(tag)
        else:
            blocked_reasons.append(f"Unknown tag blocked: {tag_id}")

    # 2. 説明文の禁止ワードチェック
    for exp in explanations:
        text = exp.get("text", "")
        is_clean = True

        for word in BANNED_WORDS_JA + BANNED_WORDS_EN:
            if word.lower() in text.lower():
                blocked_reasons.append(f"Banned word in explanation: {word}")
                is_clean = False
                break

        for celeb in CELEBRITY_NAMES:
            if celeb.lower() in text.lower():
                blocked_reasons.append(f"Celebrity name blocked: {celeb}")
                is_clean = False
                break

        if is_clean:
            filtered_explanations.append(exp)

    return {
        "is_valid": len(blocked_reasons) == 0,
        "filtered_tags": filtered_tags,
        "filtered_explanations": filtered_explanations,
        "blocked_reasons": blocked_reasons,
        "guardrails": {
            "celebrity_similarity": "blocked",
            "identity_match": "blocked",
            "sensitive_inference": "blocked",
        },
    }
