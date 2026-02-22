import fs from 'fs/promises';
import path from 'path';
import { getDataDir } from './jobStore';

const JOB_TTL_DAYS = parseInt(process.env.JOB_TTL_DAYS || '7', 10);

let cleanupRan = false;

/**
 * DATA_DIR 配下の古いジョブディレクトリを削除する。
 * 初回呼び出し時のみ実行（プロセス起動後1回限り）。
 */
export async function cleanupOldJobsOnce(): Promise<void> {
  if (cleanupRan) return;
  cleanupRan = true;
  await cleanupOldJobs();
}

export async function cleanupOldJobs(): Promise<void> {
  const dataDir = getDataDir();
  const cutoffMs = Date.now() - JOB_TTL_DAYS * 24 * 60 * 60 * 1000;

  let entries: Awaited<ReturnType<typeof fs.readdir>>;
  try {
    entries = await fs.readdir(dataDir, { withFileTypes: true });
  } catch {
    // DATA_DIR がまだ存在しない場合はスキップ
    return;
  }

  for (const entry of entries) {
    if (!entry.isDirectory()) continue;

    const jobJsonPath = path.join(dataDir, entry.name, 'job.json');
    try {
      const stat = await fs.stat(jobJsonPath);
      if (stat.mtimeMs < cutoffMs) {
        await fs.rm(path.join(dataDir, entry.name), { recursive: true, force: true });
        console.log(`[cleanup] Removed old job: ${entry.name}`);
      }
    } catch {
      // job.json がないディレクトリはスキップ
    }
  }
}
