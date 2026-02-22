import OpenAI from 'openai';
import { Cut, TextPosition } from './types';

const openai = new OpenAI({ apiKey: process.env.OPENAI_API_KEY });

// ============================================================
// System Prompt（厳格な JSON スキーマ指定）
// ============================================================
const SYSTEM_PROMPT = `
You are a professional storyboard director specializing in vertical (9:16) short-form video content.
Analyze the provided Japanese script and decompose it into visual cuts suitable for a mobile video.

For each cut you must produce:
1. "cutNumber"    : integer starting from 1
2. "description"  : concise Japanese description of the visual scene (50 chars max)
3. "imagePrompt"  : detailed English prompt for DALL-E 3 image generation
4. "textPosition" : one of ["top","bottom","center-left","center-right","none"]

== imagePrompt rules ==
- English ONLY. No Japanese.
- Photorealistic, cinematic style. High detail.
- For textPosition "top"         : begin with "Cinematic portrait photo. The main subject occupies the lower 65% of the frame. The top 25% is clean, simple, uncluttered background (sky, wall, etc.) suitable for text overlay."
- For textPosition "bottom"      : begin with "Cinematic portrait photo. The main subject occupies the upper 65% of the frame. The bottom 25% is clean, simple, uncluttered background (floor, ground, etc.) suitable for text overlay."
- For textPosition "center-left" : begin with "Cinematic portrait photo. The main subject is positioned on the right 60% of the frame. The left 25% is a clean, blurred, simple background suitable for text overlay."
- For textPosition "center-right": begin with "Cinematic portrait photo. The main subject is positioned on the left 60% of the frame. The right 25% is a clean, blurred, simple background suitable for text overlay."
- For textPosition "none"        : begin with "Cinematic portrait photo."
- ALWAYS end imagePrompt with exactly: "No text, no letters, no words, no numbers, no logos, no watermarks, no signs, no captions. Vertical 9:16 portrait format."

== textPosition selection guide ==
- "top"          : subject in lower half (e.g., landscape, wide shot, person at bottom)
- "bottom"       : subject in upper half (e.g., sky scene, overhead view)
- "center-left"  : subject on the right (e.g., person facing left, right-aligned composition)
- "center-right" : subject on the left (e.g., person facing right, left-aligned composition)
- "none"         : full-bleed image, no overlay text needed

== Output format ==
Return ONLY a valid JSON object. No markdown fences. No explanation. No extra keys.
Exact schema:
{
  "cuts": [
    {
      "cutNumber": 1,
      "description": "シーンの日本語説明",
      "imagePrompt": "English DALL-E 3 prompt...",
      "textPosition": "top"
    }
  ]
}
`.trim();

// ============================================================
// 台本分解
// ============================================================
export async function parseScript(script: string, maxCuts: number): Promise<Cut[]> {
  const userPrompt =
    `以下の台本を最大${maxCuts}カットに分解してください。` +
    `台本の内容・流れを忠実に反映し、視覚的に魅力的なカット割りにしてください。\n\n` +
    `台本:\n${script}`;

  const response = await openai.chat.completions.create({
    model: 'gpt-4o',
    messages: [
      { role: 'system', content: SYSTEM_PROMPT },
      { role: 'user', content: userPrompt },
    ],
    response_format: { type: 'json_object' },
    temperature: 0.7,
    max_tokens: 4096,
  });

  const content = response.choices[0]?.message?.content;
  if (!content) throw new Error('GPT からのレスポンスが空です');

  let parsed: { cuts: unknown[] };
  try {
    parsed = JSON.parse(content);
  } catch {
    throw new Error('GPT レスポンスの JSON パースに失敗しました');
  }

  if (!Array.isArray(parsed.cuts) || parsed.cuts.length === 0) {
    throw new Error('GPT レスポンスに cuts 配列がありません');
  }

  const validPositions: TextPosition[] = ['top', 'bottom', 'center-left', 'center-right', 'none'];

  const cuts: Cut[] = parsed.cuts.slice(0, maxCuts).map((c: unknown, idx: number) => {
    const cut = c as Record<string, unknown>;
    return {
      cutNumber: typeof cut.cutNumber === 'number' ? cut.cutNumber : idx + 1,
      description: String(cut.description || `カット ${idx + 1}`),
      imagePrompt: String(cut.imagePrompt || 'Cinematic portrait photo. No text. Vertical 9:16 portrait format.'),
      textPosition: validPositions.includes(cut.textPosition as TextPosition)
        ? (cut.textPosition as TextPosition)
        : 'bottom',
    };
  });

  return cuts;
}
