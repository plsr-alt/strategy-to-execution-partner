import { NextRequest, NextResponse } from 'next/server';
import { createJob, processJob } from '@/lib/jobProcessor';

const MAX_SCRIPT_LENGTH = parseInt(process.env.MAX_SCRIPT_LENGTH ?? '5000', 10);
const MIN_SCRIPT_LENGTH = 20;
const DEFAULT_MAX_CUTS  = parseInt(process.env.DEFAULT_MAX_CUTS ?? '15', 10);
const MAX_CUTS_LIMIT    = parseInt(process.env.MAX_CUTS_LIMIT ?? '30', 10);

export async function POST(request: NextRequest) {
  let body: unknown;
  try {
    body = await request.json();
  } catch {
    return NextResponse.json({ error: 'リクエストが不正です' }, { status: 400 });
  }

  const { script, maxCuts: rawMaxCuts } = body as Record<string, unknown>;

  // バリデーション
  if (typeof script !== 'string' || script.trim().length === 0) {
    return NextResponse.json({ error: '台本を入力してください' }, { status: 400 });
  }
  if (script.length < MIN_SCRIPT_LENGTH) {
    return NextResponse.json(
      { error: `台本は${MIN_SCRIPT_LENGTH}文字以上入力してください` },
      { status: 400 },
    );
  }
  if (script.length > MAX_SCRIPT_LENGTH) {
    return NextResponse.json(
      { error: `台本は${MAX_SCRIPT_LENGTH}文字以内にしてください` },
      { status: 400 },
    );
  }

  const maxCuts = Math.min(
    MAX_CUTS_LIMIT,
    Math.max(3, parseInt(String(rawMaxCuts ?? DEFAULT_MAX_CUTS), 10) || DEFAULT_MAX_CUTS),
  );

  // ジョブ作成
  const job = await createJob(script.trim(), maxCuts);

  // バックグラウンドで処理開始（EC2の永続プロセスなので安全）
  void processJob(job.id);

  return NextResponse.json({ jobId: job.id }, { status: 201 });
}
