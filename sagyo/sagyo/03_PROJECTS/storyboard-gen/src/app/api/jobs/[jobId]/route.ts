import { NextRequest, NextResponse } from 'next/server';
import { getJob } from '@/lib/jobStore';
import { JobWithUrls } from '@/lib/types';

export async function GET(
  _request: NextRequest,
  { params }: { params: Promise<{ jobId: string }> },
) {
  const { jobId } = await params;

  const job = await getJob(jobId);
  if (!job) {
    return NextResponse.json({ error: 'ジョブが見つかりません' }, { status: 404 });
  }

  // クライアントに返す際に imageUrl を付与
  const jobWithUrls: JobWithUrls = {
    ...job,
    results: job.results.map((r) => ({
      ...r,
      imageUrl: r.imagePath
        ? `/api/jobs/${jobId}/images/${r.imagePath}`
        : undefined,
    })),
  };

  return NextResponse.json(jobWithUrls);
}
