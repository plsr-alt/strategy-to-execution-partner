import { NextRequest, NextResponse } from 'next/server';
import fs from 'fs/promises';
import path from 'path';
import { getJobDir } from '@/lib/jobStore';

// 許可するファイル名パターン（パストラバーサル防止）
const SAFE_FILENAME = /^[\w-]+\.(png|jpg|jpeg|webp)$/i;
// UUID v4 形式
const UUID_PATTERN = /^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/i;

export async function GET(
  _request: NextRequest,
  { params }: { params: Promise<{ jobId: string; filename: string }> },
) {
  const { jobId, filename } = await params;

  if (!UUID_PATTERN.test(jobId)) {
    return NextResponse.json({ error: '無効な Job ID' }, { status: 400 });
  }
  if (!SAFE_FILENAME.test(filename)) {
    return NextResponse.json({ error: '無効なファイル名' }, { status: 400 });
  }

  const imagePath = path.join(getJobDir(jobId), filename);

  try {
    const data = await fs.readFile(imagePath);
    return new NextResponse(data, {
      headers: {
        'Content-Type':  'image/png',
        'Cache-Control': 'public, max-age=86400, immutable',
      },
    });
  } catch {
    return NextResponse.json({ error: '画像が見つかりません' }, { status: 404 });
  }
}
