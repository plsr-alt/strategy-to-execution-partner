import { v4 as uuidv4 } from 'uuid';
import { Job, CutResult, JobStatus } from './types';
import { saveJob, getJob } from './jobStore';
import { parseScript } from './scriptParser';
import { generateImage } from './imageGenerator';
import { cleanupOldJobsOnce } from './cleanup';

// ============================================================
// ジョブ作成
// ============================================================
export async function createJob(script: string, maxCuts: number): Promise<Job> {
  // 初回のみ古いジョブをクリーンアップ（非同期、待たない）
  void cleanupOldJobsOnce();

  const id = uuidv4();
  const now = new Date().toISOString();

  const job: Job = {
    id,
    status: 'pending',
    script,
    maxCuts,
    cuts: [],
    results: [],
    createdAt: now,
    updatedAt: now,
    totalCuts: 0,
    completedCuts: 0,
    failedCuts: 0,
  };

  await saveJob(job);
  return job;
}

// ============================================================
// ジョブ処理（バックグラウンドで実行）
// POST /api/jobs から void processJob(id) で呼ぶ
// ============================================================
export async function processJob(jobId: string): Promise<void> {
  let job = await getJob(jobId);
  if (!job) {
    console.error(`[processor] Job ${jobId} not found`);
    return;
  }

  console.log(`[processor] Starting job ${jobId}`);

  // --- processing へ遷移 ---
  job = { ...job, status: 'processing', updatedAt: ts() };
  await saveJob(job);

  try {
    // ---- Step 1: 台本分解 ----
    console.log(`[processor] Parsing script (maxCuts=${job.maxCuts})`);
    const cuts = await parseScript(job.script, job.maxCuts);

    const results: CutResult[] = cuts.map((cut) => ({
      cutNumber: cut.cutNumber,
      status: 'pending',
      retryCount: 0,
    }));

    job = { ...job, cuts, results, totalCuts: cuts.length, updatedAt: ts() };
    await saveJob(job);
    console.log(`[processor] Script parsed into ${cuts.length} cuts`);

    // ---- Step 2: 画像生成（逐次） ----
    for (let i = 0; i < cuts.length; i++) {
      const cut = cuts[i];

      // generating へ
      results[i] = { ...results[i], status: 'generating' };
      job = { ...job, results: [...results], updatedAt: ts() };
      await saveJob(job);

      try {
        const imagePath = await generateImage(cut, jobId);
        results[i] = { ...results[i], status: 'done', imagePath };
      } catch (err) {
        results[i] = {
          ...results[i],
          status: 'failed',
          error: err instanceof Error ? err.message : '生成失敗',
        };
      }

      // カウント更新
      const completedCuts = results.filter((r) => r.status === 'done').length;
      const failedCuts = results.filter((r) => r.status === 'failed').length;
      job = { ...job, results: [...results], completedCuts, failedCuts, updatedAt: ts() };
      await saveJob(job);
    }

    // ---- 最終ステータス判定 ----
    const allFailed = results.every((r) => r.status === 'failed');
    const finalStatus: JobStatus = allFailed ? 'failed' : 'completed';
    job = {
      ...job,
      status: finalStatus,
      error: allFailed ? 'すべての画像生成に失敗しました' : undefined,
      updatedAt: ts(),
    };
    await saveJob(job);
    console.log(`[processor] Job ${jobId} finished: ${finalStatus}`);
  } catch (err) {
    // 台本解析などで致命的エラー
    const error = err instanceof Error ? err.message : '処理中にエラーが発生しました';
    console.error(`[processor] Job ${jobId} fatal error:`, error);
    await saveJob({ ...job, status: 'failed', error, updatedAt: ts() });
  }
}

function ts(): string {
  return new Date().toISOString();
}
