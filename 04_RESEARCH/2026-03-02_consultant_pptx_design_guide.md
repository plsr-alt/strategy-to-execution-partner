# コンサルクオリティ PowerPoint 制作ガイド（python-pptx実装）

> 作成日: 2026-03-02
> 目的: McKinsey / BCG / Accenture レベルのPPTをpython-pptxで自動生成するための設計原則・実装テクニック集

---

## 1. デザイン原則（コンサルスタイル）

### 1.1 カラースキーム

コンサルファームは**2〜3色+グレー階調**が基本。派手さではなく「信頼感」を演出する。

#### 推奨パレット

| 用途 | 色名 | HEX | RGB | 使用箇所 |
|------|------|-----|-----|---------|
| プライマリ（濃紺） | Dark Navy | `#1F497D` | (31,73,125) | タイトル、セクションヘッダー、強調テキスト |
| セカンダリ（青） | Corporate Blue | `#2B579A` | (43,87,154) | チャートメイン、アイコン、リンク |
| アクセント（ティール） | Accent Teal | `#0078D4` | (0,120,212) | CTA、ハイライト、重要数値 |
| 警告・注意 | Alert Red | `#C00000` | (192,0,0) | 注記、リスク、要確認事項 |
| 成功・ポジティブ | Success Green | `#2E7D32` | (46,125,50) | 達成、承認、OK表示 |
| テキスト（黒） | Near Black | `#333333` | (51,51,51) | 本文テキスト（真っ黒は避ける） |
| サブテキスト | Medium Gray | `#666666` | (102,102,102) | 補足、出典、注釈 |
| 背景グレー | Light Gray BG | `#F2F2F2` | (242,242,242) | テーブル交互色、カード背景 |
| 白 | White | `#FFFFFF` | (255,255,255) | スライド背景 |
| 区切り線 | Border Gray | `#D9D9D9` | (217,217,217) | テーブル罫線、divider |

```python
# python-pptx カラー定数
from pptx.dml.color import RGBColor

COLOR_NAVY      = RGBColor(0x1F, 0x49, 0x7D)
COLOR_BLUE      = RGBColor(0x2B, 0x57, 0x9A)
COLOR_ACCENT    = RGBColor(0x00, 0x78, 0xD4)
COLOR_RED       = RGBColor(0xC0, 0x00, 0x00)
COLOR_GREEN     = RGBColor(0x2E, 0x7D, 0x32)
COLOR_TEXT       = RGBColor(0x33, 0x33, 0x33)
COLOR_SUBTEXT   = RGBColor(0x66, 0x66, 0x66)
COLOR_BG_GRAY   = RGBColor(0xF2, 0xF2, 0xF2)
COLOR_WHITE     = RGBColor(0xFF, 0xFF, 0xFF)
COLOR_BORDER    = RGBColor(0xD9, 0xD9, 0xD9)
```

#### McKinseyスタイル配色の特徴
- 濃紺 + 白 + アクセント1色（水色 or ゴールド）
- グラフは濃→薄のグラデーション（同系色3-4段階）
- **絶対にやらないこと**: レインボー配色、3Dエフェクト、グラデーション背景

#### BCGスタイル配色の特徴
- 緑（BCGグリーン `#00A651`）+ 濃紺 + グレー
- チャートはBCGグリーンの濃淡

#### Accentureスタイル配色の特徴
- 紫（`#A100FF`）+ 黒 + 白
- 大胆な単色面


### 1.2 タイポグラフィ

#### フォント選定

| 優先度 | 日本語 | 英語/数字 | 用途 |
|--------|--------|-----------|------|
| 第1候補 | **メイリオ** | **Segoe UI** / **Calibri** | 最も安全。Windows標準 |
| 第2候補 | **游ゴシック Medium** | **Arial** | macOS互換が必要な場合 |
| 避けるべき | MS Pゴシック、HG系 | Times New Roman | 古い印象。コンサル資料では使わない |

#### フォントサイズ階層（コンサル標準）

| 要素 | サイズ | 太さ | 色 |
|------|--------|------|-----|
| スライドタイトル | **18-20pt** | Bold | 濃紺 `#1F497D` |
| セクションヘッダー（中表紙） | **28-32pt** | Bold | 濃紺 or 白（背景色あり時） |
| サブヘッド/見出し | **14-16pt** | Bold | 濃紺 |
| 本文 | **11-12pt** | Regular | 黒 `#333333` |
| 箇条書き | **11-12pt** | Regular | 黒 |
| 注釈・出典 | **8-9pt** | Regular | グレー `#666666` |
| 数値ハイライト | **24-36pt** | Bold | アクセント色 |
| ページ番号 | **8pt** | Regular | グレー |

```python
from pptx.util import Pt

# フォントサイズ定数
FONT_TITLE      = Pt(20)
FONT_SECTION    = Pt(28)
FONT_SUBHEAD    = Pt(14)
FONT_BODY       = Pt(11)
FONT_BULLET     = Pt(11)
FONT_NOTE       = Pt(8)
FONT_KPI_NUMBER = Pt(36)
FONT_PAGE_NUM   = Pt(8)
```

#### タイポグラフィのルール
1. **1スライド内でフォントサイズは3段階まで**（タイトル / 本文 / 注釈）
2. **太字は見出しのみ**。本文を太字にしない（強調はアクセント色で）
3. **行間は1.2〜1.5倍**（詰めすぎない。読みやすさ最優先）
4. **文字の左揃え**が基本。中央揃えは表紙・セクションヘッダーのみ
5. **1行の文字数は40文字以下**を目安に


### 1.3 レイアウトグリッドとスペーシング

#### スライドサイズ
- **ワイド (16:9)**: 幅 13,716,000 EMU (33.867cm) x 高さ 7,772,400 EMU (19.05cm)
- コンサルファームはほぼ全て16:9

#### マージン・グリッドルール

```
+----------------------------------------------------------+
|  上マージン: 0.5インチ (457,200 EMU)                       |
|  +------------------------------------------------------+|
|  | タイトルエリア: 高さ約1インチ                            ||
|  +------------------------------------------------------+|
|  |                                                      ||
|  | コンテンツエリア                                       ||
|  | 左マージン: 0.75インチ   右マージン: 0.75インチ           ||
|  |                                                      ||
|  |                                                      ||
|  +------------------------------------------------------+|
|  下マージン: 0.5インチ + フッター                           |
+----------------------------------------------------------+
```

```python
from pptx.util import Inches, Emu

# レイアウト定数
MARGIN_LEFT   = Inches(0.75)
MARGIN_RIGHT  = Inches(0.75)
MARGIN_TOP    = Inches(0.5)
MARGIN_BOTTOM = Inches(0.5)

# タイトルバー
TITLE_LEFT    = MARGIN_LEFT
TITLE_TOP     = MARGIN_TOP
TITLE_WIDTH   = Inches(12.0)
TITLE_HEIGHT  = Inches(0.7)

# コンテンツエリア
CONTENT_LEFT   = MARGIN_LEFT
CONTENT_TOP    = Inches(1.4)
CONTENT_WIDTH  = Inches(12.0)
CONTENT_HEIGHT = Inches(5.5)

# 2カラムレイアウト
COL_WIDTH      = Inches(5.75)
COL_GAP        = Inches(0.5)
COL2_LEFT      = Inches(0.75) + COL_WIDTH + COL_GAP
```

#### ホワイトスペースのルール
- **コンテンツ占有率は60-70%が理想**。空白が30-40%あると高級感が出る
- 要素間のギャップは最低0.15インチ（テーブルのセル内余白含む）
- タイトルとコンテンツの間は最低0.3インチの空白
- スライド端ギリギリまで要素を配置しない


### 1.4 スライド構造パターン

#### A. Assertion-Evidence（主張-根拠）構造 -- McKinsey標準
```
+----------------------------------------------------------+
| [主張（1行の完全文）]                                       |
| "クラウド移行により年間コストを30%削減できる"                  |
+----------------------------------------------------------+
|                                                          |
|   [根拠となるデータ・チャート・表]                           |
|                                                          |
|   出典: xx調査 2025年                                     |
+----------------------------------------------------------+
```
- タイトルは「名詞」ではなく「主張文（SVO文）」
- 悪い例: "コスト比較" / 良い例: "クラウド移行で年間30%のコスト削減が見込める"

#### B. ピラミッド構造（MECE）
```
+----------------------------------------------------------+
| [結論（1文）]                                              |
+----------------------------------------------------------+
|  [理由1]         [理由2]         [理由3]                    |
|  +-----------+   +-----------+   +-----------+             |
|  | 根拠A     |   | 根拠D     |   | 根拠G     |             |
|  | 根拠B     |   | 根拠E     |   | 根拠H     |             |
|  | 根拠C     |   | 根拠F     |   | 根拠I     |             |
|  +-----------+   +-----------+   +-----------+             |
+----------------------------------------------------------+
```

#### C. Executive Summary（エグゼクティブサマリ）
```
+----------------------------------------------------------+
| エグゼクティブサマリ                                        |
+----------------------------------------------------------+
| 状況:  [2-3行で現状を簡潔に]                                |
| 課題:  [解決すべき問題]                                     |
| 提案:  [推奨アクション]                                     |
| 効果:  [期待される成果・KPI]                                 |
| Next:  [次のステップ・期限]                                  |
+----------------------------------------------------------+
```

#### D. Comparison / Matrix
```
+----------------------------------------------------------+
| [比較の結論]                                               |
+----------------------------------------------------------+
|         |  選択肢A  |  選択肢B  |  選択肢C  |              |
|  項目1  |    ○     |    △     |    ×     |              |
|  項目2  |    △     |    ○     |    ○     |              |
|  項目3  |    ○     |    ○     |    △     |              |
|  総合   |   推奨    |   代替    |   非推奨   |              |
+----------------------------------------------------------+
```


---

## 2. python-pptx 実装テクニック

### 2.1 プロフェッショナルなテーブル

```python
from pptx import Presentation
from pptx.util import Inches, Pt, Emu
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.oxml.ns import qn
from lxml import etree

def create_consultant_table(slide, rows, cols, data,
                             left=Inches(0.75), top=Inches(1.5),
                             width=Inches(12.0), height=Inches(4.5),
                             header_color=RGBColor(0x1F,0x49,0x7D)):
    """コンサルクオリティのテーブルを作成"""
    table_shape = slide.shapes.add_table(rows, cols, left, top, width, height)
    table = table_shape.table

    # --- 列幅の均等配分（必要に応じてカスタム）---
    col_width = int(width / cols)
    for i in range(cols):
        table.columns[i].width = col_width

    # --- ヘッダー行のスタイル ---
    for j in range(cols):
        cell = table.cell(0, j)
        cell.text = data[0][j]
        # 背景色（濃紺）
        _set_cell_color(cell, header_color)
        # テキストスタイル
        for para in cell.text_frame.paragraphs:
            para.font.size = Pt(11)
            para.font.bold = True
            para.font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)
            para.alignment = PP_ALIGN.CENTER
        cell.vertical_anchor = MSO_ANCHOR.MIDDLE

    # --- データ行 ---
    for i in range(1, rows):
        for j in range(cols):
            cell = table.cell(i, j)
            cell.text = data[i][j]
            # 交互色
            if i % 2 == 0:
                _set_cell_color(cell, RGBColor(0xF2, 0xF2, 0xF2))
            else:
                _set_cell_color(cell, RGBColor(0xFF, 0xFF, 0xFF))
            # テキストスタイル
            for para in cell.text_frame.paragraphs:
                para.font.size = Pt(10)
                para.font.color.rgb = RGBColor(0x33, 0x33, 0x33)
                para.alignment = PP_ALIGN.LEFT
            cell.vertical_anchor = MSO_ANCHOR.MIDDLE

    # --- 罫線を薄いグレーに ---
    _set_table_borders(table, RGBColor(0xD9, 0xD9, 0xD9))

    return table


def _set_cell_color(cell, color):
    """セル背景色を設定"""
    tcPr = cell._tc.get_or_add_tcPr()
    solidFill = etree.SubElement(tcPr, qn('a:solidFill'))
    srgbClr = etree.SubElement(solidFill, qn('a:srgbClr'))
    srgbClr.set('val', '%02X%02X%02X' % (color[0], color[1], color[2]))


def _set_cell_border(cell, border_pos, color, width=Pt(0.5)):
    """セルの罫線を設定（border_pos: 'top','bottom','left','right'）"""
    tc = cell._tc
    tcPr = tc.get_or_add_tcPr()

    border_map = {
        'top': 'a:lnT', 'bottom': 'a:lnB',
        'left': 'a:lnL', 'right': 'a:lnR'
    }
    ln = etree.SubElement(tcPr, qn(border_map[border_pos]))
    ln.set('w', str(int(width)))
    solidFill = etree.SubElement(ln, qn('a:solidFill'))
    srgbClr = etree.SubElement(solidFill, qn('a:srgbClr'))
    srgbClr.set('val', '%02X%02X%02X' % (color[0], color[1], color[2]))


def _set_table_borders(table, color):
    """テーブル全体の罫線色を統一"""
    for row_idx in range(len(table.rows)):
        for col_idx in range(len(table.columns)):
            cell = table.cell(row_idx, col_idx)
            for pos in ['top', 'bottom', 'left', 'right']:
                _set_cell_border(cell, pos, color)
```

#### テーブルの内部余白（padding）設定
```python
def set_cell_margins(cell, top=Emu(45720), bottom=Emu(45720),
                     left=Emu(91440), right=Emu(91440)):
    """セル内余白を設定（デフォルト: 上下0.05in, 左右0.1in）"""
    tc = cell._tc
    tcPr = tc.get_or_add_tcPr()
    tcPr.set('marT', str(top))
    tcPr.set('marB', str(bottom))
    tcPr.set('marL', str(left))
    tcPr.set('marR', str(right))
```

### 2.2 プロフェッショナルな図形・視覚要素

#### タイトルバー（アクセントライン付き）
```python
from pptx.enum.shapes import MSO_SHAPE

def add_title_bar(slide, text,
                  left=Inches(0.75), top=Inches(0.4),
                  width=Inches(12.0), height=Inches(0.65)):
    """コンサルスタイルのタイトルバーを追加"""
    # タイトルテキスト
    txBox = slide.shapes.add_textbox(left, top, width, height)
    tf = txBox.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    run = p.add_run()
    run.text = text
    run.font.size = Pt(20)
    run.font.bold = True
    run.font.color.rgb = RGBColor(0x1F, 0x49, 0x7D)

    # アクセントライン（タイトル下の細い線）
    line = slide.shapes.add_shape(
        MSO_SHAPE.RECTANGLE,
        left, top + height + Inches(0.05),
        width, Inches(0.03)
    )
    line.fill.solid()
    line.fill.fore_color.rgb = RGBColor(0x00, 0x78, 0xD4)
    line.line.fill.background()  # 枠線なし

    return txBox


def add_divider_line(slide, left=Inches(0.75), top=Inches(3.0),
                     width=Inches(12.0)):
    """水平区切り線"""
    line = slide.shapes.add_shape(
        MSO_SHAPE.RECTANGLE,
        left, top, width, Emu(12700)  # 1pt height
    )
    line.fill.solid()
    line.fill.fore_color.rgb = RGBColor(0xD9, 0xD9, 0xD9)
    line.line.fill.background()
    return line
```

#### KPI / メトリクスカード
```python
def add_kpi_card(slide, number_text, label_text,
                 left=Inches(1.0), top=Inches(2.0),
                 width=Inches(3.0), height=Inches(2.5),
                 accent_color=RGBColor(0x00,0x78,0xD4)):
    """大きな数値+ラベルのKPIカード"""
    # カード背景
    card = slide.shapes.add_shape(
        MSO_SHAPE.ROUNDED_RECTANGLE,
        left, top, width, height
    )
    card.fill.solid()
    card.fill.fore_color.rgb = RGBColor(0xF8, 0xF8, 0xF8)
    card.line.color.rgb = RGBColor(0xE0, 0xE0, 0xE0)
    card.line.width = Pt(1)

    # 数値（大きく）
    num_box = slide.shapes.add_textbox(
        left + Inches(0.2), top + Inches(0.3),
        width - Inches(0.4), Inches(1.2)
    )
    p = num_box.text_frame.paragraphs[0]
    p.alignment = PP_ALIGN.CENTER
    run = p.add_run()
    run.text = number_text
    run.font.size = Pt(36)
    run.font.bold = True
    run.font.color.rgb = accent_color

    # ラベル
    label_box = slide.shapes.add_textbox(
        left + Inches(0.2), top + Inches(1.5),
        width - Inches(0.4), Inches(0.6)
    )
    p = label_box.text_frame.paragraphs[0]
    p.alignment = PP_ALIGN.CENTER
    run = p.add_run()
    run.text = label_text
    run.font.size = Pt(11)
    run.font.color.rgb = RGBColor(0x66, 0x66, 0x66)

    return card


def add_kpi_row(slide, kpis, top=Inches(2.0)):
    """KPIカードを横一列に配置
    kpis: list of (number, label) tuples
    """
    n = len(kpis)
    total_width = Inches(12.0)
    card_gap = Inches(0.3)
    card_width = (total_width - card_gap * (n - 1)) / n

    for i, (number, label) in enumerate(kpis):
        left = Inches(0.75) + (card_width + card_gap) * i
        add_kpi_card(slide, number, label,
                     left=int(left), top=top,
                     width=int(card_width))
```

#### アイコン風の丸形+テキスト
```python
def add_icon_circle(slide, text, label,
                    left=Inches(2.0), top=Inches(2.0),
                    diameter=Inches(1.2),
                    fill_color=RGBColor(0x1F,0x49,0x7D)):
    """アイコン風の丸形バッジ + ラベル"""
    # 丸
    circle = slide.shapes.add_shape(
        MSO_SHAPE.OVAL,
        left, top, diameter, diameter
    )
    circle.fill.solid()
    circle.fill.fore_color.rgb = fill_color
    circle.line.fill.background()

    # 丸の中のテキスト
    tf = circle.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.alignment = PP_ALIGN.CENTER
    run = p.add_run()
    run.text = text
    run.font.size = Pt(14)
    run.font.bold = True
    run.font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)
    circle.text_frame.paragraphs[0].space_before = Pt(0)

    # ラベル（丸の下）
    lbl = slide.shapes.add_textbox(
        left - Inches(0.3), top + diameter + Inches(0.1),
        diameter + Inches(0.6), Inches(0.5)
    )
    p = lbl.text_frame.paragraphs[0]
    p.alignment = PP_ALIGN.CENTER
    run = p.add_run()
    run.text = label
    run.font.size = Pt(10)
    run.font.color.rgb = RGBColor(0x33, 0x33, 0x33)

    return circle
```

#### 矢印コネクタ（フロー表現）
```python
def add_arrow_right(slide, left, top, width=Inches(0.8), height=Inches(0.4)):
    """右向き矢印"""
    arrow = slide.shapes.add_shape(
        MSO_SHAPE.RIGHT_ARROW,
        left, top, width, height
    )
    arrow.fill.solid()
    arrow.fill.fore_color.rgb = RGBColor(0x1F, 0x49, 0x7D)
    arrow.line.fill.background()
    return arrow
```


### 2.3 テキストフォーマットと段落スペーシング

```python
from pptx.util import Pt, Emu
from pptx.enum.text import PP_ALIGN

def format_paragraph(para, font_size=Pt(11), bold=False,
                     color=RGBColor(0x33,0x33,0x33),
                     alignment=PP_ALIGN.LEFT,
                     space_before=Pt(3), space_after=Pt(3),
                     line_spacing=1.2):
    """段落の統一フォーマット"""
    para.alignment = alignment
    para.space_before = space_before
    para.space_after = space_after
    # 行間設定
    pPr = para._pPr
    if pPr is None:
        pPr = para._p.get_or_add_pPr()
    lnSpc = etree.SubElement(pPr, qn('a:lnSpc'))
    spcPct = etree.SubElement(lnSpc, qn('a:spcPct'))
    spcPct.set('val', str(int(line_spacing * 100000)))

    for run in para.runs:
        run.font.size = font_size
        run.font.bold = bold
        run.font.color.rgb = color


def add_bullet_list(text_frame, items,
                    font_size=Pt(11), color=RGBColor(0x33,0x33,0x33),
                    bullet_char='\u2022', indent_level=0):
    """箇条書きリストを追加"""
    for i, item in enumerate(items):
        if i == 0:
            p = text_frame.paragraphs[0]
        else:
            p = text_frame.add_paragraph()
        p.level = indent_level
        run = p.add_run()
        run.text = f"{bullet_char} {item}"
        run.font.size = font_size
        run.font.color.rgb = color
        p.space_before = Pt(4)
        p.space_after = Pt(2)
```

#### フォントを確実に統一する関数
```python
def set_font_recursive(shape, font_name='メイリオ', font_name_en='Segoe UI'):
    """shape内の全テキストのフォントを統一"""
    if shape.has_text_frame:
        for para in shape.text_frame.paragraphs:
            for run in para.runs:
                run.font.name = font_name_en
                # 東アジアフォント設定（XML直接操作）
                rPr = run._r.get_or_add_rPr()
                ea = rPr.find(qn('a:ea'))
                if ea is None:
                    ea = etree.SubElement(rPr, qn('a:ea'))
                ea.set('typeface', font_name)
    if shape.has_table:
        for row in shape.table.rows:
            for cell in row.cells:
                for para in cell.text_frame.paragraphs:
                    for run in para.runs:
                        run.font.name = font_name_en
                        rPr = run._r.get_or_add_rPr()
                        ea = rPr.find(qn('a:ea'))
                        if ea is None:
                            ea = etree.SubElement(rPr, qn('a:ea'))
                        ea.set('typeface', font_name)
```


### 2.4 スライドマスター/レイアウトの操作

```python
def setup_slide_master(prs):
    """スライドマスターのデフォルトフォントを設定"""
    master = prs.slide_masters[0]

    # 各レイアウトのplaceholderフォントを統一
    for layout in master.slide_layouts:
        for ph in layout.placeholders:
            if ph.has_text_frame:
                for para in ph.text_frame.paragraphs:
                    for run in para.runs:
                        run.font.name = 'Segoe UI'


def get_layout_by_name(prs, name):
    """レイアウトを名前で取得"""
    for layout in prs.slide_layouts:
        if layout.name == name:
            return layout
    return None


def add_slide_with_layout(prs, layout_name='Blank'):
    """指定レイアウトでスライド追加"""
    layout = get_layout_by_name(prs, layout_name)
    if layout is None:
        layout = prs.slide_layouts[6]  # fallback: Blank
    return prs.slides.add_slide(layout)
```

#### フッター（ページ番号 + 会社名）の追加
```python
def add_footer(slide, company_name, page_num, total_pages,
               confidential=False):
    """フッターを追加（ページ番号 + 会社ロゴ/名前 + 機密表示）"""
    slide_width = Inches(13.333)

    # ページ番号（右下）
    num_box = slide.shapes.add_textbox(
        slide_width - Inches(1.5), Inches(7.0),
        Inches(1.0), Inches(0.3)
    )
    p = num_box.text_frame.paragraphs[0]
    p.alignment = PP_ALIGN.RIGHT
    run = p.add_run()
    run.text = f"{page_num} / {total_pages}"
    run.font.size = Pt(8)
    run.font.color.rgb = RGBColor(0x99, 0x99, 0x99)

    # 会社名（左下）
    co_box = slide.shapes.add_textbox(
        Inches(0.5), Inches(7.0),
        Inches(3.0), Inches(0.3)
    )
    p = co_box.text_frame.paragraphs[0]
    run = p.add_run()
    run.text = f"(c) {company_name}"
    run.font.size = Pt(8)
    run.font.color.rgb = RGBColor(0x99, 0x99, 0x99)

    # 機密表示
    if confidential:
        conf_box = slide.shapes.add_textbox(
            Inches(5.0), Inches(7.0),
            Inches(3.0), Inches(0.3)
        )
        p = conf_box.text_frame.paragraphs[0]
        p.alignment = PP_ALIGN.CENTER
        run = p.add_run()
        run.text = "CONFIDENTIAL"
        run.font.size = Pt(8)
        run.font.bold = True
        run.font.color.rgb = RGBColor(0xC0, 0x00, 0x00)
```


### 2.5 チャート / データビジュアライゼーション

```python
from pptx.chart.data import CategoryChartData
from pptx.enum.chart import XL_CHART_TYPE, XL_LEGEND_POSITION

def add_bar_chart(slide, categories, series_data,
                  left=Inches(1.0), top=Inches(1.8),
                  width=Inches(10.0), height=Inches(5.0),
                  chart_colors=None):
    """コンサルスタイルの棒グラフ"""
    chart_data = CategoryChartData()
    chart_data.categories = categories

    for name, values in series_data.items():
        chart_data.add_series(name, values)

    chart_frame = slide.shapes.add_chart(
        XL_CHART_TYPE.COLUMN_CLUSTERED,
        left, top, width, height, chart_data
    )
    chart = chart_frame.chart

    # --- スタイル調整 ---
    chart.has_legend = len(series_data) > 1
    if chart.has_legend:
        chart.legend.position = XL_LEGEND_POSITION.BOTTOM
        chart.legend.include_in_layout = False
        chart.legend.font.size = Pt(9)

    # グリッドライン
    value_axis = chart.value_axis
    value_axis.has_major_gridlines = True
    value_axis.major_gridlines.format.line.color.rgb = RGBColor(0xE0,0xE0,0xE0)
    value_axis.major_gridlines.format.line.width = Pt(0.5)

    # 軸ラベル
    value_axis.tick_labels.font.size = Pt(9)
    value_axis.tick_labels.font.color.rgb = RGBColor(0x66,0x66,0x66)
    chart.category_axis.tick_labels.font.size = Pt(9)
    chart.category_axis.tick_labels.font.color.rgb = RGBColor(0x66,0x66,0x66)

    # 枠線を消す
    chart.category_axis.format.line.fill.background()
    value_axis.format.line.fill.background()

    # 色の設定
    if chart_colors is None:
        chart_colors = [
            RGBColor(0x1F,0x49,0x7D),
            RGBColor(0x2B,0x79,0xC1),
            RGBColor(0x7F,0xB3,0xDE),
            RGBColor(0xBF,0xD9,0xEF),
        ]

    plot = chart.plots[0]
    for i, series in enumerate(plot.series):
        fill = series.format.fill
        fill.solid()
        fill.fore_color.rgb = chart_colors[i % len(chart_colors)]
        series.format.line.fill.background()

    plot.gap_width = 100  # バー間隔

    return chart
```

#### ドーナツチャート（構成比表示）
```python
def add_donut_chart(slide, categories, values,
                    left=Inches(4.0), top=Inches(2.0),
                    width=Inches(5.0), height=Inches(4.5)):
    """構成比を見せるドーナツチャート"""
    chart_data = CategoryChartData()
    chart_data.categories = categories
    chart_data.add_series('', values)

    chart_frame = slide.shapes.add_chart(
        XL_CHART_TYPE.DOUGHNUT,
        left, top, width, height, chart_data
    )
    chart = chart_frame.chart
    chart.has_legend = True
    chart.legend.position = XL_LEGEND_POSITION.RIGHT
    chart.legend.font.size = Pt(9)

    # データラベル
    plot = chart.plots[0]
    plot.has_data_labels = True
    data_labels = plot.data_labels
    data_labels.font.size = Pt(10)
    data_labels.font.bold = True
    data_labels.number_format = '0%'

    return chart
```


---

## 3. スライド構造別テンプレート

### 3.1 表紙スライド

```python
def create_title_slide(prs, title, subtitle, date, company, client=None):
    """コンサルスタイルの表紙"""
    slide = add_slide_with_layout(prs, 'Blank')

    # 背景帯（上部1/3を濃紺に）
    bg_rect = slide.shapes.add_shape(
        MSO_SHAPE.RECTANGLE,
        0, 0, Inches(13.333), Inches(3.2)
    )
    bg_rect.fill.solid()
    bg_rect.fill.fore_color.rgb = RGBColor(0x1F, 0x49, 0x7D)
    bg_rect.line.fill.background()

    # メインタイトル（白文字、背景帯の中）
    title_box = slide.shapes.add_textbox(
        Inches(1.0), Inches(0.8),
        Inches(11.0), Inches(1.5)
    )
    p = title_box.text_frame.paragraphs[0]
    run = p.add_run()
    run.text = title
    run.font.size = Pt(28)
    run.font.bold = True
    run.font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)

    # サブタイトル
    sub_box = slide.shapes.add_textbox(
        Inches(1.0), Inches(2.3),
        Inches(11.0), Inches(0.6)
    )
    p = sub_box.text_frame.paragraphs[0]
    run = p.add_run()
    run.text = subtitle
    run.font.size = Pt(14)
    run.font.color.rgb = RGBColor(0xCC, 0xCC, 0xCC)

    # アクセントライン
    line = slide.shapes.add_shape(
        MSO_SHAPE.RECTANGLE,
        Inches(1.0), Inches(3.2),
        Inches(3.0), Inches(0.05)
    )
    line.fill.solid()
    line.fill.fore_color.rgb = RGBColor(0x00, 0x78, 0xD4)
    line.line.fill.background()

    # 日付
    date_box = slide.shapes.add_textbox(
        Inches(1.0), Inches(4.0),
        Inches(5.0), Inches(0.4)
    )
    p = date_box.text_frame.paragraphs[0]
    run = p.add_run()
    run.text = date
    run.font.size = Pt(12)
    run.font.color.rgb = RGBColor(0x66, 0x66, 0x66)

    # 会社名
    co_box = slide.shapes.add_textbox(
        Inches(1.0), Inches(4.5),
        Inches(5.0), Inches(0.4)
    )
    p = co_box.text_frame.paragraphs[0]
    run = p.add_run()
    run.text = company
    run.font.size = Pt(12)
    run.font.color.rgb = RGBColor(0x33, 0x33, 0x33)

    # クライアント名（あれば）
    if client:
        cl_box = slide.shapes.add_textbox(
            Inches(1.0), Inches(5.2),
            Inches(5.0), Inches(0.4)
        )
        p = cl_box.text_frame.paragraphs[0]
        run = p.add_run()
        run.text = f"For: {client}"
        run.font.size = Pt(14)
        run.font.bold = True
        run.font.color.rgb = RGBColor(0x33, 0x33, 0x33)

    # CONFIDENTIAL
    conf_box = slide.shapes.add_textbox(
        Inches(8.0), Inches(6.8),
        Inches(4.5), Inches(0.3)
    )
    p = conf_box.text_frame.paragraphs[0]
    p.alignment = PP_ALIGN.RIGHT
    run = p.add_run()
    run.text = "CONFIDENTIAL"
    run.font.size = Pt(9)
    run.font.bold = True
    run.font.color.rgb = RGBColor(0xC0, 0x00, 0x00)

    return slide
```

### 3.2 セクションヘッダー（中表紙）

```python
def create_section_slide(prs, section_title, section_number=None):
    """セクション区切りスライド"""
    slide = add_slide_with_layout(prs, 'Blank')

    # 全面濃紺背景
    bg = slide.shapes.add_shape(
        MSO_SHAPE.RECTANGLE,
        0, 0, Inches(13.333), Inches(7.5)
    )
    bg.fill.solid()
    bg.fill.fore_color.rgb = RGBColor(0x1F, 0x49, 0x7D)
    bg.line.fill.background()

    # セクション番号（大きく）
    if section_number:
        num_box = slide.shapes.add_textbox(
            Inches(1.0), Inches(2.0),
            Inches(2.0), Inches(1.5)
        )
        p = num_box.text_frame.paragraphs[0]
        run = p.add_run()
        run.text = f"{section_number:02d}"
        run.font.size = Pt(60)
        run.font.bold = True
        run.font.color.rgb = RGBColor(0x00, 0x78, 0xD4)

    # タイトル
    title_left = Inches(1.0) if not section_number else Inches(3.5)
    title_box = slide.shapes.add_textbox(
        title_left, Inches(2.5),
        Inches(8.0), Inches(2.0)
    )
    p = title_box.text_frame.paragraphs[0]
    run = p.add_run()
    run.text = section_title
    run.font.size = Pt(32)
    run.font.bold = True
    run.font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)

    # アクセントライン
    line = slide.shapes.add_shape(
        MSO_SHAPE.RECTANGLE,
        title_left, Inches(4.6),
        Inches(2.0), Inches(0.04)
    )
    line.fill.solid()
    line.fill.fore_color.rgb = RGBColor(0x00, 0x78, 0xD4)
    line.line.fill.background()

    return slide
```

### 3.3 エグゼクティブサマリ

```python
def create_exec_summary(prs, situation, challenge, proposal, impact, next_steps):
    """エグゼクティブサマリスライド"""
    slide = add_slide_with_layout(prs, 'Blank')
    add_title_bar(slide, "エグゼクティブサマリ")

    labels = [
        ("状況", situation, RGBColor(0x1F,0x49,0x7D)),
        ("課題", challenge, RGBColor(0xC0,0x00,0x00)),
        ("提案", proposal, RGBColor(0x00,0x78,0xD4)),
        ("効果", impact, RGBColor(0x2E,0x7D,0x32)),
        ("Next", next_steps, RGBColor(0x1F,0x49,0x7D)),
    ]

    y = Inches(1.6)
    for label, content, label_color in labels:
        # ラベル
        lbl_box = slide.shapes.add_textbox(
            Inches(0.75), y, Inches(1.2), Inches(0.5)
        )
        p = lbl_box.text_frame.paragraphs[0]
        run = p.add_run()
        run.text = label
        run.font.size = Pt(12)
        run.font.bold = True
        run.font.color.rgb = label_color

        # コンテンツ
        cnt_box = slide.shapes.add_textbox(
            Inches(2.2), y, Inches(10.3), Inches(0.9)
        )
        cnt_box.text_frame.word_wrap = True
        p = cnt_box.text_frame.paragraphs[0]
        run = p.add_run()
        run.text = content
        run.font.size = Pt(11)
        run.font.color.rgb = RGBColor(0x33, 0x33, 0x33)

        # 区切り線
        if label != "Next":
            add_divider_line(slide, Inches(0.75), y + Inches(0.95), Inches(12.0))

        y += Inches(1.05)

    return slide
```

### 3.4 比較マトリクス

```python
def create_comparison_slide(prs, title, options, criteria, scores,
                            recommendation_idx=0):
    """比較マトリクススライド
    options: ["FSx Windows", "FSx NetApp", "EFS"]
    criteria: ["コスト", "性能", "互換性", "運用負荷"]
    scores: [[3,2,1], [2,3,2], [3,1,3], [2,2,2]]  (criteria x options)
    recommendation_idx: 推奨する選択肢のインデックス
    """
    slide = add_slide_with_layout(prs, 'Blank')
    add_title_bar(slide, title)

    score_symbols = {3: '\u25CB', 2: '\u25B3', 1: '\u00D7', 0: '\u2015'}
    score_colors = {
        3: RGBColor(0x2E,0x7D,0x32),  # green
        2: RGBColor(0xED,0x6C,0x02),  # orange
        1: RGBColor(0xC0,0x00,0x00),  # red
        0: RGBColor(0x99,0x99,0x99),  # gray
    }

    rows = len(criteria) + 2  # header + criteria + total
    cols = len(options) + 1     # label col + options

    data = [[''] + options]
    for i, crit in enumerate(criteria):
        row = [crit]
        for j in range(len(options)):
            row.append(score_symbols.get(scores[i][j], ''))
        data.append(row)

    # 合計行
    totals = [sum(scores[i][j] for i in range(len(criteria)))
              for j in range(len(options))]
    total_row = ['総合'] + [str(t) for t in totals]
    data.append(total_row)

    table = create_consultant_table(
        slide, rows, cols, data,
        top=Inches(1.6), height=Inches(4.5)
    )

    # 推奨列をハイライト
    rec_col = recommendation_idx + 1
    for row_idx in range(1, rows):
        cell = table.cell(row_idx, rec_col)
        _set_cell_color(cell, RGBColor(0xE8, 0xF0, 0xFE))

    # 推奨ラベル
    rec_box = slide.shapes.add_textbox(
        Inches(0.75), Inches(6.3), Inches(3.0), Inches(0.4)
    )
    p = rec_box.text_frame.paragraphs[0]
    run = p.add_run()
    run.text = f"推奨: {options[recommendation_idx]}"
    run.font.size = Pt(14)
    run.font.bold = True
    run.font.color.rgb = RGBColor(0x00, 0x78, 0xD4)

    return slide
```

### 3.5 Next Steps / Call to Action

```python
def create_next_steps_slide(prs, steps):
    """Next Stepsスライド
    steps: list of (who, deadline, action) tuples
    """
    slide = add_slide_with_layout(prs, 'Blank')
    add_title_bar(slide, "Next Steps")

    rows = len(steps) + 1
    cols = 4
    data = [['#', '担当', '期限', 'アクション']]
    for i, (who, deadline, action) in enumerate(steps, 1):
        data.append([str(i), who, deadline, action])

    table = create_consultant_table(
        slide, rows, cols, data,
        top=Inches(1.6), height=Inches(0.5 + 0.5 * len(steps))
    )

    # 列幅の調整（#列を狭く、アクション列を広く）
    table.columns[0].width = Inches(0.6)
    table.columns[1].width = Inches(2.0)
    table.columns[2].width = Inches(2.0)
    table.columns[3].width = Inches(7.4)

    return slide
```


### 3.6 裏表紙

```python
def create_closing_slide(prs, company_name, contact_email=None,
                          closing_text="ご清聴ありがとうございました"):
    """裏表紙"""
    slide = add_slide_with_layout(prs, 'Blank')

    # 全面濃紺
    bg = slide.shapes.add_shape(
        MSO_SHAPE.RECTANGLE,
        0, 0, Inches(13.333), Inches(7.5)
    )
    bg.fill.solid()
    bg.fill.fore_color.rgb = RGBColor(0x1F, 0x49, 0x7D)
    bg.line.fill.background()

    # クロージングテキスト
    main_box = slide.shapes.add_textbox(
        Inches(2.0), Inches(2.5),
        Inches(9.0), Inches(1.5)
    )
    p = main_box.text_frame.paragraphs[0]
    p.alignment = PP_ALIGN.CENTER
    run = p.add_run()
    run.text = closing_text
    run.font.size = Pt(28)
    run.font.bold = True
    run.font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)

    # 会社名
    co_box = slide.shapes.add_textbox(
        Inches(2.0), Inches(4.5),
        Inches(9.0), Inches(0.6)
    )
    p = co_box.text_frame.paragraphs[0]
    p.alignment = PP_ALIGN.CENTER
    run = p.add_run()
    run.text = company_name
    run.font.size = Pt(16)
    run.font.color.rgb = RGBColor(0xCC, 0xCC, 0xCC)

    # 連絡先
    if contact_email:
        email_box = slide.shapes.add_textbox(
            Inches(2.0), Inches(5.2),
            Inches(9.0), Inches(0.4)
        )
        p = email_box.text_frame.paragraphs[0]
        p.alignment = PP_ALIGN.CENTER
        run = p.add_run()
        run.text = contact_email
        run.font.size = Pt(11)
        run.font.color.rgb = RGBColor(0x99, 0x99, 0x99)

    # 免責
    disc_box = slide.shapes.add_textbox(
        Inches(1.0), Inches(6.8),
        Inches(11.0), Inches(0.5)
    )
    p = disc_box.text_frame.paragraphs[0]
    p.alignment = PP_ALIGN.CENTER
    run = p.add_run()
    run.text = "本資料は社外秘です。弊社の書面による許可なく複製・転載を禁じます。"
    run.font.size = Pt(7)
    run.font.color.rgb = RGBColor(0x99, 0x99, 0x99)

    return slide
```


---

## 4. 高度なテクニック

### 4.1 テンプレートPPTXからの構築（推奨方式）

ゼロからBlankで構築するより、**テンプレートPPTX（.pptx）をベースに操作する**のがコンサル実務の標準。

```python
def build_from_template(template_path, output_path):
    """テンプレートPPTXをベースに構築"""
    prs = Presentation(template_path)

    # テンプレートのレイアウト一覧を確認
    for i, layout in enumerate(prs.slide_layouts):
        print(f"Layout {i}: {layout.name}")
        for ph in layout.placeholders:
            print(f"  PH {ph.placeholder_format.idx}: {ph.name} ({ph.placeholder_format.type})")

    # レイアウトを使ってスライド追加
    # layout[0] = タイトル, layout[1] = 目次, layout[5] = Blank 等
    slide = prs.slides.add_slide(prs.slide_layouts[0])

    # placeholderに値を設定
    slide.placeholders[0].text = "タイトル"
    slide.placeholders[1].text = "サブタイトル"

    prs.save(output_path)
```

### 4.2 既存スライドのコピー・複製

```python
import copy
from pptx.oxml.ns import qn

def duplicate_slide(prs, source_idx, insert_at=None):
    """既存スライドを複製"""
    template = prs.slides[source_idx]
    layout = template.slide_layout
    new_slide = prs.slides.add_slide(layout)

    # 全シェイプをコピー
    sp_tree = new_slide.shapes._spTree
    for child in list(sp_tree):
        sp_tree.remove(child)
    for child in template.shapes._spTree:
        sp_tree.append(copy.deepcopy(child))

    # 位置調整
    if insert_at is not None:
        move_slide(prs, len(prs.slides) - 1, insert_at)

    return new_slide


def move_slide(prs, from_idx, to_idx):
    """スライドの順番を変更"""
    sldIdLst = prs.slides._sldIdLst
    elem = sldIdLst[from_idx]
    sldIdLst.remove(elem)
    sldIdLst.insert(to_idx, elem)
```

### 4.3 画像の追加（ロゴ・スクリーンショット）

```python
def add_logo(slide, image_path,
             left=Inches(11.0), top=Inches(0.2),
             width=Inches(1.8)):
    """ロゴ画像を追加（右上配置）"""
    slide.shapes.add_picture(image_path, left, top, width=width)


def add_screenshot_with_border(slide, image_path,
                                left=Inches(1.0), top=Inches(2.0),
                                width=Inches(10.0)):
    """スクリーンショットを細いボーダー付きで追加"""
    pic = slide.shapes.add_picture(image_path, left, top, width=width)

    # ボーダー追加
    pic.line.color.rgb = RGBColor(0xD9, 0xD9, 0xD9)
    pic.line.width = Pt(1)

    return pic
```

### 4.4 プログレスバー / タイムライン

```python
def add_progress_bar(slide, current_step, total_steps, labels,
                     top=Inches(6.0)):
    """スライド下部にプログレスバーを追加"""
    bar_width = Inches(10.0)
    bar_left = Inches(1.5)
    step_width = bar_width / total_steps

    for i in range(total_steps):
        x = int(bar_left + step_width * i)

        # ステップの丸
        circle = slide.shapes.add_shape(
            MSO_SHAPE.OVAL,
            x + int(step_width / 2) - Inches(0.15),
            top, Inches(0.3), Inches(0.3)
        )

        if i < current_step:
            # 完了
            circle.fill.solid()
            circle.fill.fore_color.rgb = RGBColor(0x2E, 0x7D, 0x32)
        elif i == current_step:
            # 現在
            circle.fill.solid()
            circle.fill.fore_color.rgb = RGBColor(0x00, 0x78, 0xD4)
        else:
            # 未来
            circle.fill.solid()
            circle.fill.fore_color.rgb = RGBColor(0xD9, 0xD9, 0xD9)
        circle.line.fill.background()

        # ラベル
        if i < len(labels):
            lbl = slide.shapes.add_textbox(
                x, top + Inches(0.4),
                int(step_width), Inches(0.4)
            )
            p = lbl.text_frame.paragraphs[0]
            p.alignment = PP_ALIGN.CENTER
            run = p.add_run()
            run.text = labels[i]
            run.font.size = Pt(8)
            run.font.color.rgb = RGBColor(0x66, 0x66, 0x66)

        # 接続線
        if i < total_steps - 1:
            line = slide.shapes.add_shape(
                MSO_SHAPE.RECTANGLE,
                x + int(step_width / 2) + Inches(0.15),
                top + Inches(0.13),
                int(step_width) - Inches(0.3), Inches(0.04)
            )
            color = RGBColor(0x2E,0x7D,0x32) if i < current_step else RGBColor(0xD9,0xD9,0xD9)
            line.fill.solid()
            line.fill.fore_color.rgb = color
            line.line.fill.background()
```


---

## 5. コンサルPPT作成でやってはいけないこと

### 5.1 デザイン面

| NG | なぜダメか | 正しいやり方 |
|----|-----------|-------------|
| 3D効果、影、グラデーション背景 | 安っぽく見える。2010年代の遺物 | フラットデザイン。単色塗り |
| 5色以上の多色使い | 視線が散る。素人感が出る | 2-3色+グレー階調 |
| クリップアート / 無料素材感のあるイラスト | 信頼性が下がる | シンプルなアイコン or 写真 |
| WordArt / 装飾フォント | 読みにくい。ビジネスに不適 | メイリオ or Segoe UI |
| アニメーション / トランジション | 会議で邪魔。印刷時に消える | 一切不要 |
| 全面テキストの壁 | 読まれない。プレゼンの意味がない | 1スライド=1メッセージ |
| 真っ黒(#000000)のテキスト | コントラストが強すぎて疲れる | #333333 を使う |
| フォント混在（3種類以上） | 統一感がない | 和文1種+欧文1種 |

### 5.2 構造面

| NG | なぜダメか | 正しいやり方 |
|----|-----------|-------------|
| タイトルが名詞だけ（「コスト」） | 何を言いたいか不明 | 主張文にする（「コストは30%削減可能」） |
| 1スライドに複数メッセージ | 聞き手が混乱する | 1 slide = 1 message |
| 出典なし | 信頼性ゼロ | 必ず出典明記（右下にPt(8)で） |
| ページ番号なし | 議論時に参照できない | 必ず付ける |
| 「まとめ」がない | 最後に何をすべきか不明 | Next Stepsスライド必須 |
| スライド枚数が多すぎる | 30分で40枚は無理 | 1枚/2-3分が目安 |

### 5.3 python-pptx固有の落とし穴

| NG | 対策 |
|----|------|
| フォントが指定通りにならない | `run.font.name`だけでなく、XML直接操作で東アジアフォント(`a:ea`)も設定する |
| テーブルの罫線がデフォルトのまま | `_set_table_borders()`で明示的にグレーに変更する |
| テキストが枠からはみ出す | `text_frame.word_wrap = True` + `auto_size`の明示設定 |
| 日本語フォントが英語フォントに置き換わる | 東アジアフォント属性を必ず設定（`a:ea typeface='メイリオ'`） |
| Emu/Inches/Pt の混在で位置がズレる | 定数化して統一。Inches基準で設計 |
| スライドマスターとの競合 | Blankレイアウトをベースにし、全て手動配置が安全 |
| テーブルセル背景色が設定できない | python-pptxのAPIではなくXML直接操作(`tcPr > solidFill`) |
| チャートのスタイルが地味 | デフォルトは使わず、色・フォント・罫線を全て手動設定 |


---

## 6. 完全なワークフロー例

```python
from pptx import Presentation
from pptx.util import Inches, Pt

def build_consultant_deck(output_path):
    """コンサルクオリティのデッキを一括生成"""
    prs = Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)

    # 1. 表紙
    create_title_slide(prs,
        title="ファイルサーバ クラウド移行提案",
        subtitle="Amazon FSx for Windows File Server による最適構成のご提案",
        date="2026年3月10日",
        company="株式会社サーバーワークス",
        client="コメダ珈琲店様"
    )

    # 2. エグゼクティブサマリ
    create_exec_summary(prs,
        situation="既存ファイルサーバの保守期限が2027年3月に迫っている",
        challenge="21TB（最大50TB）のデータを安全にクラウド移行する必要がある",
        proposal="FSx for Windows File Server + DataSync による段階的移行を推奨",
        impact="年間運用コスト30%削減、可用性99.99%の実現",
        next_steps="3月中にNW方式を合意、4月からNW切替支援着手"
    )

    # 3. セクションヘッダー
    create_section_slide(prs, "現状分析と課題", section_number=1)

    # 4. コンテンツスライド（テーブル付き）
    slide = add_slide_with_layout(prs, 'Blank')
    add_title_bar(slide, "FSx for Windows は全要件を満たす最適解である")
    create_consultant_table(slide, 5, 4,
        [['項目', 'FSx Windows', 'FSx NetApp', 'EFS'],
         ['Windows互換', '\u25CB 完全対応', '\u25CB 対応', '\u00D7 非対応'],
         ['コスト (50TB)', '$X,XXX/月', '$X,XXX/月', '$X,XXX/月'],
         ['AD連携', '\u25CB ネイティブ', '\u25B3 要設定', '\u00D7 非対応'],
         ['運用負荷', '\u25CB マネージド', '\u25CB マネージド', '\u25B3 要設計']],
        top=Inches(1.6)
    )

    # 5. Next Steps
    create_next_steps_slide(prs, [
        ("両社", "2026/3/10", "NW接続方式（DX/VPN）を合意"),
        ("弊社", "2026/3末", "NW切替支援の見積提示"),
        ("コメダ様", "2026/4上旬", "NW切替支援の発注判断"),
        ("弊社", "2026/4-6", "NW切替設計・構築"),
        ("弊社", "2026/5-", "FSx環境設計開始"),
    ])

    # 6. 裏表紙
    create_closing_slide(prs, "株式会社サーバーワークス")

    # フォント統一（全スライド）
    for slide in prs.slides:
        for shape in slide.shapes:
            set_font_recursive(shape)

    # ページ番号追加
    total = len(prs.slides)
    for i, slide in enumerate(prs.slides):
        if i > 0 and i < total - 1:  # 表紙・裏表紙以外
            add_footer(slide, "サーバーワークス", i + 1, total)

    prs.save(output_path)
    print(f"Saved: {output_path} ({total} slides)")
```


---

## 7. 参考リソース（チェックリスト）

### スライド作成前チェックリスト
- [ ] 16:9のスライドサイズか
- [ ] カラーパレットを2-3色+グレーに限定したか
- [ ] フォントはメイリオ/Segoe UIに統一したか
- [ ] 各スライドのタイトルは「主張文」になっているか
- [ ] 1 slide = 1 message を守っているか
- [ ] 出典を全て記載したか
- [ ] ページ番号を付けたか
- [ ] Next Stepsスライドがあるか
- [ ] CONFIDENTIAL表記が必要な場合、入れたか
- [ ] アニメーション・3D効果を使っていないか

### python-pptx品質チェックリスト
- [ ] 東アジアフォント(a:ea)を設定したか
- [ ] テーブルの罫線色をグレーに変更したか
- [ ] テキスト色は#333333（真っ黒回避）か
- [ ] word_wrap = True を設定したか
- [ ] 定数（色・サイズ・位置）をファイル上部に集約したか
- [ ] EMU/Inches/Ptを統一的に使っているか
