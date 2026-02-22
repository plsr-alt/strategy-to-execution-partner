// ============================================================
// 型定義
// ============================================================

/** カットごとのテキスト余白位置 */
export type TextPosition = 'top' | 'bottom' | 'center-left' | 'center-right' | 'none';

/** ジョブ全体のステータス */
export type JobStatus = 'pending' | 'processing' | 'completed' | 'failed';

/** 各カットの生成ステータス */
export type CutStatus = 'pending' | 'generating' | 'done' | 'failed';

/** 台本から分解された1カット */
export interface Cut {
  cutNumber: number;
  /** シーンの日本語説明 */
  description: string;
  /** DALL-E 3 用の英語プロンプト（テキスト禁止・余白指示を含む） */
  imagePrompt: string;
  /** テキストオーバーレイを置く余白位置 */
  textPosition: TextPosition;
}

/** 各カットの生成結果 */
export interface CutResult {
  cutNumber: number;
  status: CutStatus;
  /** /data/{jobId}/ からの相対ファイル名 (例: cut-001.png) */
  imagePath?: string;
  error?: string;
  retryCount: number;
}

/** ジョブ全体（/data/{jobId}/job.json に保存） */
export interface Job {
  id: string;
  status: JobStatus;
  script: string;
  maxCuts: number;
  cuts: Cut[];
  results: CutResult[];
  createdAt: string;
  updatedAt: string;
  error?: string;
  totalCuts: number;
  completedCuts: number;
  failedCuts: number;
}

/** API レスポンス用（imageUrl を付与） */
export type JobWithUrls = Omit<Job, 'results'> & {
  results: (CutResult & { imageUrl?: string })[];
};

/** POST /api/jobs のリクエストボディ */
export interface CreateJobRequest {
  script: string;
  maxCuts?: number;
}
