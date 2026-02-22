import { NextRequest, NextResponse } from 'next/server';
import { getJob, getJobDir } from '@/lib/jobStore';
import archiver from 'archiver';
import fs from 'fs';
import path from 'path';

export async function GET(
  _request: NextRequest,
  { params }: { params: Promise<{ jobId: string }> },
) {
  const { jobId } = await params;

  const job = await getJob(jobId);
  if (!job) {
    return NextResponse.json({ error: 'ジョブが見つかりません' }, { status: 404 });
  }
  if (job.status !== 'completed') {
    return NextResponse.json(
      { error: `ジョブはまだ完了していません (status: ${job.status})` },
      { status: 400 },
    );
  }

  const jobDir = getJobDir(jobId);

  // アーカイブをメモリ上に構築
  const buffer = await new Promise<Buffer>((resolve, reject) => {
    const archive = archiver('zip', { zlib: { level: 6 } });
    const chunks: Buffer[] = [];

    archive.on('data', (chunk: Buffer) => chunks.push(chunk));
    archive.on('end', () => resolve(Buffer.concat(chunks)));
    archive.on('error', reject);

    // 生成済み画像を追加
    for (const result of job.results) {
      if (result.status === 'done' && result.imagePath) {
        const filepath = path.join(jobDir, result.imagePath);
        if (fs.existsSync(filepath)) {
          archive.file(filepath, { name: result.imagePath });
        }
      }
    }

    // カットメタデータを JSON で追加
    const metadata = JSON.stringify(
      job.cuts.map((cut) => {
        const result = job.results.find((r) => r.cutNumber === cut.cutNumber);
        return {
          cutNumber:   cut.cutNumber,
          description: cut.description,
          imagePrompt: cut.imagePrompt,
          textPosition:cut.textPosition,
          imageFile:   result?.imagePath ?? null,
          status:      result?.status ?? 'unknown',
        };
      }),
      null,
      2,
    );
    archive.append(metadata, { name: 'cuts.json' });

    archive.finalize();
  });

  const filename = `storyboard-${jobId.slice(0, 8)}.zip`;

  return new NextResponse(buffer, {
    headers: {
      'Content-Type':        'application/zip',
      'Content-Disposition': `attachment; filename="${filename}"`,
      'Content-Length':      String(buffer.length),
    },
  });
}
