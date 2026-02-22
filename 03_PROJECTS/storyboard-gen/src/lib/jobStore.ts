import fs from 'fs/promises';
import path from 'path';
import { Job } from './types';

const DATA_DIR = process.env.DATA_DIR || '/data';

export function getDataDir(): string {
  return DATA_DIR;
}

export function getJobDir(jobId: string): string {
  return path.join(DATA_DIR, jobId);
}

export function getJobJsonPath(jobId: string): string {
  return path.join(DATA_DIR, jobId, 'job.json');
}

/** ジョブを保存（新規 or 更新） */
export async function saveJob(job: Job): Promise<void> {
  const jobDir = getJobDir(job.id);
  await fs.mkdir(jobDir, { recursive: true });
  await fs.writeFile(getJobJsonPath(job.id), JSON.stringify(job, null, 2), 'utf-8');
}

/** ジョブを取得。存在しない場合は null */
export async function getJob(jobId: string): Promise<Job | null> {
  // 簡易バリデーション（パストラバーサル防止）
  if (!/^[0-9a-f-]{36}$/.test(jobId)) return null;
  try {
    const content = await fs.readFile(getJobJsonPath(jobId), 'utf-8');
    return JSON.parse(content) as Job;
  } catch {
    return null;
  }
}

/** ジョブの存在確認 */
export async function jobExists(jobId: string): Promise<boolean> {
  if (!/^[0-9a-f-]{36}$/.test(jobId)) return false;
  try {
    await fs.access(getJobJsonPath(jobId));
    return true;
  } catch {
    return false;
  }
}
