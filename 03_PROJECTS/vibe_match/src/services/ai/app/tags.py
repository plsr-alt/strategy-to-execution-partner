"""
VibeMatch 印象タグ定義 & CLIPプロンプト

8大カテゴリ × サブタグ。
各タグに対して英語/日本語の複数プロンプトを定義し、
CLIPのcos類似度でスコアリングする。
"""

from dataclasses import dataclass


@dataclass
class VibeTag:
    id: str
    label: str           # 日本語表示名
    category: str        # 大カテゴリ
    prompts_en: list[str]  # 英語CLIPプロンプト
    prompts_ja: list[str]  # 日本語CLIPプロンプト（Japanese CLIP用）


# ============================================
# 8大カテゴリ定義
# ============================================
CATEGORIES = [
    {"id": "natural", "label": "ナチュラル", "color": "#8B9E6B"},
    {"id": "fresh", "label": "フレッシュ", "color": "#87CEEB"},
    {"id": "cute", "label": "キュート", "color": "#FFB6C1"},
    {"id": "elegant", "label": "エレガント", "color": "#DDA0DD"},
    {"id": "cool", "label": "クール", "color": "#708090"},
    {"id": "wild", "label": "ワイルド", "color": "#CD853F"},
    {"id": "mysterious", "label": "ミステリアス", "color": "#483D8B"},
    {"id": "warm", "label": "ウォーム", "color": "#F4A460"},
]

CATEGORY_IDS = [c["id"] for c in CATEGORIES]

# ============================================
# タグ一覧（8カテゴリ × 各4サブタグ = 32タグ）
# ============================================
VIBE_TAGS: list[VibeTag] = [
    # --- ナチュラル ---
    VibeTag(
        id="honwaka", label="ほんわか", category="natural",
        prompts_en=[
            "a person with a soft warm gentle face and kind eyes",
            "a friendly approachable face with a gentle smile",
        ],
        prompts_ja=["ほんわかした優しい雰囲気の顔", "柔らかくて親しみやすい表情の人"],
    ),
    VibeTag(
        id="soboku", label="素朴ナチュラル", category="natural",
        prompts_en=[
            "a person with a simple natural unadorned face",
            "a natural looking face without heavy makeup",
        ],
        prompts_ja=["素朴でナチュラルな顔立ちの人", "飾らない自然体の印象の顔"],
    ),
    VibeTag(
        id="earth", label="アースカラー", category="natural",
        prompts_en=[
            "a person with earthy warm toned natural appearance",
            "a calm grounded face with warm natural tones",
        ],
        prompts_ja=["落ち着いたアースカラーが似合う雰囲気の人", "大地のような安定感のある顔"],
    ),
    VibeTag(
        id="nonbiri", label="のんびり系", category="natural",
        prompts_en=[
            "a person with a relaxed easygoing gentle expression",
            "a laid back calm face with droopy peaceful eyes",
        ],
        prompts_ja=["のんびりした穏やかな表情の人", "マイペースそうなゆったりした雰囲気"],
    ),

    # --- フレッシュ ---
    VibeTag(
        id="sawayaka", label="さわやか", category="fresh",
        prompts_en=[
            "a person with a fresh clean refreshing face",
            "a bright clean-cut face with clear skin",
        ],
        prompts_ja=["さわやかで清潔感のある顔", "明るくすっきりした印象の人"],
    ),
    VibeTag(
        id="clean_beauty", label="クリーンビューティ", category="fresh",
        prompts_en=[
            "a person with clean minimal beauty and clear features",
            "a neat tidy face with simple clean appearance",
        ],
        prompts_ja=["クリーンで洗練された清潔感のある人", "シンプルで美しい顔立ち"],
    ),
    VibeTag(
        id="toumei", label="透明感", category="fresh",
        prompts_en=[
            "a person with a translucent pure ethereal appearance",
            "a light bright face with an airy transparent quality",
        ],
        prompts_ja=["透明感のある澄んだ印象の人", "透き通るような清らかな雰囲気"],
    ),
    VibeTag(
        id="asatsuyu", label="朝露系", category="fresh",
        prompts_en=[
            "a person with a dewy fresh morning-like appearance",
            "a youthful glowing face with fresh energy",
        ],
        prompts_ja=["朝露のようにみずみずしい印象の人", "フレッシュで若々しいエネルギー"],
    ),

    # --- キュート ---
    VibeTag(
        id="marutto", label="まるっと可愛い", category="cute",
        prompts_en=[
            "a person with round cute features and big expressive eyes",
            "an adorable face with soft round cheeks",
        ],
        prompts_ja=["まるっとした可愛い顔立ちの人", "丸みのある愛らしい印象"],
    ),
    VibeTag(
        id="azato", label="あざと可愛い", category="cute",
        prompts_en=[
            "a person with a charming calculated cute expression",
            "a playfully cute face with knowing eyes",
        ],
        prompts_ja=["あざと可愛い計算された魅力の人", "小悪魔的な可愛さのある顔"],
    ),
    VibeTag(
        id="pop", label="ポップ", category="cute",
        prompts_en=[
            "a person with a bright colorful pop style appearance",
            "an energetic vibrant face with a fun playful vibe",
        ],
        prompts_ja=["ポップで明るい雰囲気の人", "カラフルでエネルギッシュな印象"],
    ),
    VibeTag(
        id="sweet", label="スイート", category="cute",
        prompts_en=[
            "a person with a sweet gentle lovely appearance",
            "a soft sweet face with warm lovely features",
        ],
        prompts_ja=["スイートで甘い雰囲気の人", "優しくてふんわりした可愛さ"],
    ),

    # --- エレガント ---
    VibeTag(
        id="classical", label="クラシカル", category="elegant",
        prompts_en=[
            "a person with classical refined elegant features",
            "a timeless elegant face with sophisticated beauty",
        ],
        prompts_ja=["クラシカルで洗練された顔立ちの人", "時代を超えた上品な美しさ"],
    ),
    VibeTag(
        id="hanayaka", label="華やか", category="elegant",
        prompts_en=[
            "a person with glamorous gorgeous striking features",
            "a radiant dazzling face with strong presence",
        ],
        prompts_ja=["華やかで存在感のある人", "パッと目を引く輝きのある顔"],
    ),
    VibeTag(
        id="feminine", label="フェミニン", category="elegant",
        prompts_en=[
            "a person with feminine graceful delicate features",
            "a soft feminine face with gentle curves",
        ],
        prompts_ja=["フェミニンで繊細な美しさの人", "女性らしい柔らかな雰囲気"],
    ),
    VibeTag(
        id="graceful", label="グレイスフル", category="elegant",
        prompts_en=[
            "a person with graceful poised dignified appearance",
            "a composed elegant face with quiet confidence",
        ],
        prompts_ja=["グレイスフルで品のある佇まいの人", "優雅で落ち着いた気品"],
    ),

    # --- クール ---
    VibeTag(
        id="mode", label="モード", category="cool",
        prompts_en=[
            "a person with a high fashion editorial cool look",
            "a sharp stylish face with avant-garde appeal",
        ],
        prompts_ja=["モードでファッショナブルな雰囲気の人", "エッジの効いたスタイリッシュな顔"],
    ),
    VibeTag(
        id="intellectual", label="知的クール", category="cool",
        prompts_en=[
            "a person with an intelligent sharp cool expression",
            "a smart composed face with piercing thoughtful eyes",
        ],
        prompts_ja=["知的でクールな印象の人", "頭の良さが滲む鋭い表情"],
    ),
    VibeTag(
        id="minimal", label="ミニマル", category="cool",
        prompts_en=[
            "a person with minimalist clean sharp features",
            "a simple refined face with understated elegance",
        ],
        prompts_ja=["ミニマルで研ぎ澄まされた印象の人", "シンプルで無駄のない顔立ち"],
    ),
    VibeTag(
        id="urban", label="アーバン", category="cool",
        prompts_en=[
            "a person with an urban sophisticated city cool look",
            "a modern cosmopolitan face with confident expression",
        ],
        prompts_ja=["都会的で洗練された雰囲気の人", "アーバンでスマートな印象"],
    ),

    # --- ワイルド ---
    VibeTag(
        id="outdoor", label="アウトドア系", category="wild",
        prompts_en=[
            "a person with a rugged outdoorsy healthy appearance",
            "a tanned fit face with an adventurous active vibe",
        ],
        prompts_ja=["アウトドアが似合う健康的な人", "アクティブでたくましい印象"],
    ),
    VibeTag(
        id="street", label="ストリート", category="wild",
        prompts_en=[
            "a person with street style edgy urban appearance",
            "a bold expressive face with streetwear vibes",
        ],
        prompts_ja=["ストリート系のエッジィな雰囲気の人", "個性的で存在感のある顔"],
    ),
    VibeTag(
        id="wild_sexy", label="ワイルドセクシー", category="wild",
        prompts_en=[
            "a person with wild masculine rugged attractive features",
            "a strong confident face with intense charisma",
        ],
        prompts_ja=["ワイルドでセクシーな魅力の人", "力強くてカリスマ性のある顔"],
    ),
    VibeTag(
        id="athlete", label="アスリート系", category="wild",
        prompts_en=[
            "a person with an athletic strong healthy appearance",
            "a fit energetic face with disciplined determined look",
        ],
        prompts_ja=["アスリートのような引き締まった印象の人", "スポーティで精悍な顔"],
    ),

    # --- ミステリアス ---
    VibeTag(
        id="mysterious", label="ミステリアス", category="mysterious",
        prompts_en=[
            "a person with mysterious enigmatic alluring features",
            "an intriguing face with deep captivating eyes",
        ],
        prompts_ja=["ミステリアスで惹きつける魅力の人", "謎めいた深みのある表情"],
    ),
    VibeTag(
        id="ennui", label="アンニュイ", category="mysterious",
        prompts_en=[
            "a person with a languid dreamy ennui expression",
            "a wistful melancholic face with artistic beauty",
        ],
        prompts_ja=["アンニュイで儚げな雰囲気の人", "けだるい色気のある表情"],
    ),
    VibeTag(
        id="dark_romance", label="ダークロマンス", category="mysterious",
        prompts_en=[
            "a person with dark romantic gothic beautiful features",
            "a dramatic intense face with dark allure",
        ],
        prompts_ja=["ダークロマンスな妖艶さの人", "ドラマティックで深い魅力"],
    ),
    VibeTag(
        id="smoky", label="スモーキー", category="mysterious",
        prompts_en=[
            "a person with smoky sultry hazy attractive appearance",
            "a smoldering face with subtle intense appeal",
        ],
        prompts_ja=["スモーキーで色気のある人", "けむるような妖しい魅力"],
    ),

    # --- ウォーム ---
    VibeTag(
        id="odayaka", label="おだやか", category="warm",
        prompts_en=[
            "a person with a calm peaceful serene gentle face",
            "a tranquil soothing face with soft kind eyes",
        ],
        prompts_ja=["おだやかで穏やかな印象の人", "静かで安心感のある表情"],
    ),
    VibeTag(
        id="houyou", label="包容力系", category="warm",
        prompts_en=[
            "a person with a warm embracing comforting appearance",
            "a reassuring face with nurturing protective warmth",
        ],
        prompts_ja=["包容力のある安心感たっぷりの人", "包み込むような温かさの顔"],
    ),
    VibeTag(
        id="gentle", label="ジェントル", category="warm",
        prompts_en=[
            "a person with a gentle refined warm mannered face",
            "a kind courteous face with quiet warm charm",
        ],
        prompts_ja=["ジェントルで紳士的な温かさの人", "優しく品のある雰囲気"],
    ),
    VibeTag(
        id="heart_warm", label="ハートウォーム", category="warm",
        prompts_en=[
            "a person with a heartwarming bright cheerful smile",
            "a warm friendly face that makes you feel happy",
        ],
        prompts_ja=["ハートウォームな温かい笑顔の人", "見ているだけで幸せになる雰囲気"],
    ),
]

# タグIDでルックアップ
TAGS_BY_ID: dict[str, VibeTag] = {t.id: t for t in VIBE_TAGS}

# カテゴリIDでフィルタ
TAGS_BY_CATEGORY: dict[str, list[VibeTag]] = {}
for tag in VIBE_TAGS:
    TAGS_BY_CATEGORY.setdefault(tag.category, []).append(tag)


# ============================================
# 補完マッチ 相性行列
# ============================================
# スコア: 0.0（低） 〜 1.0（最高）
COMPLEMENT_MATRIX: dict[str, dict[str, float]] = {
    "natural":    {"natural": 0.0, "fresh": 0.3, "cute": 0.3, "elegant": 0.6, "cool": 0.9, "wild": 0.6, "mysterious": 0.9, "warm": 0.0},
    "fresh":      {"natural": 0.3, "fresh": 0.0, "cute": 0.3, "elegant": 0.9, "cool": 0.3, "wild": 0.9, "mysterious": 0.6, "warm": 0.3},
    "cute":       {"natural": 0.3, "fresh": 0.3, "cute": 0.0, "elegant": 0.3, "cool": 0.9, "wild": 0.9, "mysterious": 0.6, "warm": 0.3},
    "elegant":    {"natural": 0.6, "fresh": 0.9, "cute": 0.3, "elegant": 0.0, "cool": 0.3, "wild": 0.6, "mysterious": 0.3, "warm": 0.6},
    "cool":       {"natural": 0.9, "fresh": 0.3, "cute": 0.9, "elegant": 0.3, "cool": 0.0, "wild": 0.6, "mysterious": 0.0, "warm": 0.9},
    "wild":       {"natural": 0.6, "fresh": 0.9, "cute": 0.9, "elegant": 0.6, "cool": 0.6, "wild": 0.0, "mysterious": 0.3, "warm": 0.6},
    "mysterious": {"natural": 0.9, "fresh": 0.6, "cute": 0.6, "elegant": 0.3, "cool": 0.0, "wild": 0.3, "mysterious": 0.0, "warm": 0.9},
    "warm":       {"natural": 0.0, "fresh": 0.3, "cute": 0.3, "elegant": 0.6, "cool": 0.9, "wild": 0.6, "mysterious": 0.9, "warm": 0.0},
}

# 統一感マッチ: タグベクトルのcos類似度で計算（別途関数）
