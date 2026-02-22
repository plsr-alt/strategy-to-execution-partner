'use client';

import { useCallback, useEffect, useState } from 'react';
import { useParams } from 'next/navigation';
import Link from 'next/link';
import { JobWithUrls, CutStatus, JobStatus } from '@/lib/types';

// ============================================================
// ラベル定義
// ============================================================
const JOB_STATUS_LABEL: Record<JobStatus, string> = {
  pending:    '待機中',
  processing: '処理中',
  completed:  '完了',
  failed:     '失敗',
};

const CUT_STATUS_LABEL: Record<CutStatus, string> = {
  pending:    '待機',
  generating: '生成中',
  done:       '完了',
  failed:     '失敗',
};

const POSITION_LABEL: Record<string, string> = {
  top:           '上余白',
  bottom:        '下余白',
  'center-left': '左余白',
  'center-right':'右余白',
  none:          '余白なし',
};

// ============================================================
// ページ
// ============================================================
export default function JobPage() {
  const { jobId } = useParams<{ jobId: string }>();

  const [job, setJob]           = useState<JobWithUrls | null>(null);
  const [fetchError, setFetchError] = useState<string | null>(null);
  const [polling, setPolling]   = useState(true);

  const fetchJob = useCallback(async () => {
    try {
      const res = await fetch(`/api/jobs/${jobId}`);
      if (res.status === 404) {
        setFetchError('ジョブが見つかりません');
        setPolling(false);
        return;
      }
      if (!res.ok) {
        setFetchError('取得中にエラーが発生しました');
        return;
      }
      const data: JobWithUrls = await res.json();
      setJob(data);
      if (data.status === 'completed' || data.status === 'failed') {
        setPolling(false);
      }
    } catch {
      setFetchError('ネットワークエラーが発生しました');
    }
  }, [jobId]);

  // ポーリング
  useEffect(() => {
    if (!polling) return;
    fetchJob();
    const timer = setInterval(fetchJob, 3000);
    return () => clearInterval(timer);
  }, [fetchJob, polling]);

  // ============================================================
  // ローディング / エラー
  // ============================================================
  if (fetchError) {
    return (
      <main className="container">
        <div className="error-box">{fetchError}</div>
        <Link href="/" className="back-link">← 新しいジョブを作成</Link>
      </main>
    );
  }

  if (!job) {
    return (
      <main className="container">
        <div style={{ display: 'flex', alignItems: 'center', gap: '10px', paddingTop: '20px' }}>
          <span className="spinner" />
          <span style={{ color: 'var(--muted)' }}>読み込み中...</span>
        </div>
      </main>
    );
  }

  // ============================================================
  // 進捗計算
  // ============================================================
  const done     = job.results.filter((r) => r.status === 'done').length;
  const failed   = job.results.filter((r) => r.status === 'failed').length;
  const total    = job.totalCuts;
  const progress = total > 0 ? Math.round(((done + failed) / total) * 100) : 0;

  // ============================================================
  // 描画
  // ============================================================
  return (
    <main className="container">
      <Link href="/" className="back-link">← 新しいジョブを作成</Link>

      {/* ステータスカード */}
      <div className="card">
        <div className="status-header">
          <span className="status-title">Job: {jobId.slice(0, 8)}…</span>
          <span className={`badge badge-${job.status}`}>
            {JOB_STATUS_LABEL[job.status]}
          </span>
          {polling && <span className="spinner" />}
        </div>

        {/* プログレスバー（processing 時） */}
        {(job.status === 'processing' || job.status === 'completed') && total > 0 && (
          <>
            <div className="progress-bar">
              <div className="progress-fill" style={{ width: `${progress}%` }} />
            </div>
            <p className="status-meta">
              {done + failed} / {total} カット処理済み
              {done > 0   && <span style={{ color: 'var(--success)', marginLeft: 8 }}> ✓ {done}件完了</span>}
              {failed > 0 && <span style={{ color: 'var(--error)',   marginLeft: 8 }}> ✗ {failed}件失敗</span>}
            </p>
          </>
        )}

        {job.status === 'pending' && (
          <p className="status-meta">処理キューに追加されました。しばらくお待ちください...</p>
        )}

        {job.status === 'processing' && total === 0 && (
          <p className="status-meta">台本を解析中...</p>
        )}

        {job.error && (
          <div className="error-box" style={{ marginTop: '12px' }}>{job.error}</div>
        )}
      </div>

      {/* ダウンロードボタン */}
      {job.status === 'completed' && (
        <div className="download-bar">
          <a
            href={`/api/jobs/${jobId}/zip`}
            download
            className="btn btn-download"
          >
            <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="7 10 12 15 17 10"/><line x1="12" y1="15" x2="12" y2="3"/>
            </svg>
            ZIP ダウンロード（{done} 枚）
          </a>
          {failed > 0 && (
            <span style={{ color: 'var(--muted)', fontSize: '13px' }}>
              ※ {failed} 枚の生成に失敗しました
            </span>
          )}
        </div>
      )}

      {/* カット一覧 */}
      {job.cuts.length > 0 && (
        <>
          <div className="section-title">
            カット一覧
            <span style={{ color: 'var(--muted)', fontSize: '13px', fontWeight: 400 }}>
              ({job.cuts.length} カット)
            </span>
          </div>

          <div className="cut-grid">
            {job.cuts.map((cut) => {
              const result = job.results.find((r) => r.cutNumber === cut.cutNumber);
              const status = result?.status ?? 'pending';

              return (
                <div key={cut.cutNumber} className="cut-card">
                  {/* サムネイル */}
                  {result?.imageUrl ? (
                    // eslint-disable-next-line @next/next/no-img-element
                    <img
                      src={result.imageUrl}
                      alt={`カット ${cut.cutNumber}`}
                      className="cut-thumb"
                      loading="lazy"
                    />
                  ) : (
                    <div className="cut-thumb-placeholder">
                      {status === 'generating' ? (
                        <>
                          <span className="spinner" />
                          <span>生成中...</span>
                        </>
                      ) : status === 'failed' ? (
                        <span style={{ color: 'var(--error)' }}>生成失敗</span>
                      ) : (
                        <span>待機中</span>
                      )}
                    </div>
                  )}

                  {/* 情報 */}
                  <div className="cut-info">
                    <div className="cut-number">
                      #{cut.cutNumber}
                      <span className={`badge badge-${status}`} style={{ fontSize: '10px' }}>
                        {CUT_STATUS_LABEL[status]}
                      </span>
                    </div>
                    <div className="cut-description">{cut.description}</div>
                    <div className="cut-position">
                      {POSITION_LABEL[cut.textPosition] ?? cut.textPosition}
                    </div>
                    {result?.error && (
                      <div style={{ fontSize: '10px', color: 'var(--error)', marginTop: '4px' }}>
                        {result.error}
                      </div>
                    )}
                  </div>
                </div>
              );
            })}
          </div>
        </>
      )}
    </main>
  );
}
