import OpenAI from 'openai';
import fs from 'fs/promises';
import path from 'path';
import { Cut } from './types';
import { getDataDir } from './jobStore';

const openai = new OpenAI({ apiKey: process.env.OPENAI_API_KEY });

const MAX_RETRIES = 2; // 計3回（初回 + 2リトライ）

// ============================================================
// リトライ時のプロンプト簡略化
// ============================================================
function buildPrompt(cut: Cut, attempt: number): string {
  const noText =
    'No text, no letters, no words, no numbers, no logos, no watermarks, no signs, no captions. Vertical 9:16 portrait format.';

  if (attempt === 0) {
    return `${cut.imagePrompt}`;
  }
  if (attempt === 1) {
    // プロンプトを最初の200文字に切り詰め + 必須サフィックス
    const base = cut.imagePrompt.substring(0, 200).trim().replace(/\.?\s*$/, '');
    return `${base}. ${noText}`;
  }
  // attempt 2: 最初の句だけ使用
  const firstClause = cut.imagePrompt.split(/[,.]/, 1)[0].trim();
  return `${firstClause}. Photorealistic photography, vertical portrait format. ${noText}`;
}

// ============================================================
// 画像ダウンロード（fetch は Node.js 20 でグローバル利用可）
// ============================================================
async function downloadImage(url: string, filepath: string): Promise<void> {
  const res = await fetch(url);
  if (!res.ok) throw new Error(`画像ダウンロード失敗: HTTP ${res.status}`);
  const buf = await res.arrayBuffer();
  await fs.writeFile(filepath, Buffer.from(buf));
}

// ============================================================
// 1カット分の画像生成（リトライ込み）
// ============================================================
export async function generateImage(cut: Cut, jobId: string): Promise<string> {
  const jobDir = path.join(getDataDir(), jobId);
  await fs.mkdir(jobDir, { recursive: true });

  const filename = `cut-${String(cut.cutNumber).padStart(3, '0')}.png`;
  const filepath = path.join(jobDir, filename);

  let lastError: Error = new Error('画像生成に失敗しました');

  for (let attempt = 0; attempt <= MAX_RETRIES; attempt++) {
    try {
      const prompt = buildPrompt(cut, attempt);

      if (attempt > 0) {
        console.log(`[imageGen] cut ${cut.cutNumber} retry ${attempt}/${MAX_RETRIES}`);
      }

      const response = await openai.images.generate({
        model: 'dall-e-3',
        prompt,
        size: '1024x1792', // 9:16 縦
        quality: 'standard',
        n: 1,
      });

      const imageUrl = response.data[0]?.url;
      if (!imageUrl) throw new Error('OpenAI から画像 URL が返りませんでした');

      await downloadImage(imageUrl, filepath);
      console.log(`[imageGen] cut ${cut.cutNumber} done`);
      return filename;
    } catch (err) {
      lastError = err instanceof Error ? err : new Error(String(err));
      console.error(`[imageGen] cut ${cut.cutNumber} attempt ${attempt} failed:`, lastError.message);

      if (attempt < MAX_RETRIES) {
        // 指数バックオフ: 2s, 4s
        await new Promise((r) => setTimeout(r, 2000 * Math.pow(2, attempt)));
      }
    }
  }

  throw lastError;
}
