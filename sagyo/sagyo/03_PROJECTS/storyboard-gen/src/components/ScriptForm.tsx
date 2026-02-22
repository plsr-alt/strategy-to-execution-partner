'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';

const MAX_SCRIPT_LENGTH = parseInt(process.env.NEXT_PUBLIC_MAX_SCRIPT_LENGTH || '5000', 10);
const MIN_SCRIPT_LENGTH = 20;
const MAX_CUTS_LIMIT = 30;

export default function ScriptForm() {
  const router = useRouter();
  const [script, setScript] = useState('');
  const [maxCuts, setMaxCuts] = useState(15);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const overLimit = script.length > MAX_SCRIPT_LENGTH;
  const canSubmit = script.length >= MIN_SCRIPT_LENGTH && !overLimit && !loading;

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!canSubmit) return;
    setLoading(true);
    setError(null);

    try {
      const res = await fetch('/api/jobs', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ script, maxCuts }),
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.error ?? '送信に失敗しました');
      router.push(`/jobs/${data.jobId}`);
    } catch (err) {
      setError(err instanceof Error ? err.message : '予期しないエラーが発生しました');
      setLoading(false);
    }
  }

  const estimatedMinutes = Math.ceil((maxCuts * 25) / 60);

  return (
    <form onSubmit={handleSubmit}>
      {error && <div className="error-box">{error}</div>}

      {/* 台本入力 */}
      <div className="form-group">
        <label htmlFor="script">
          台本テキスト（動画のナレーション・シナリオ）
        </label>
        <textarea
          id="script"
          rows={14}
          value={script}
          onChange={(e) => setScript(e.target.value)}
          disabled={loading}
          placeholder={[
            '例:',
            '',
            '【オープニング】',
            '朝の通勤ラッシュ。満員電車の中で主人公が眠そうにスマホを見ている。',
            '',
            '【本題】',
            '突然、スマホの画面に謎のメッセージが届く。',
            '「あなたの人生、変わりますか？」',
            '',
            '【展開】',
            '主人公は半信半疑でリンクをタップする...',
          ].join('\n')}
        />
        <div className={`char-count${overLimit ? ' over' : ''}`}>
          {script.length.toLocaleString()} / {MAX_SCRIPT_LENGTH.toLocaleString()} 文字
        </div>
      </div>

      {/* 最大カット数 */}
      <div className="form-group">
        <label htmlFor="maxCuts">
          最大カット数（3〜{MAX_CUTS_LIMIT}、デフォルト 15）
        </label>
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
          <input
            type="number"
            id="maxCuts"
            min={3}
            max={MAX_CUTS_LIMIT}
            value={maxCuts}
            onChange={(e) => {
              const v = parseInt(e.target.value, 10);
              if (!isNaN(v)) setMaxCuts(Math.min(MAX_CUTS_LIMIT, Math.max(3, v)));
            }}
            disabled={loading}
            style={{ width: '100px' }}
          />
          <span style={{ color: 'var(--muted)', fontSize: '13px' }}>
            枚 ≈ 最大 {estimatedMinutes} 分
          </span>
        </div>
      </div>

      {/* 送信 */}
      <button type="submit" className="btn btn-primary" disabled={!canSubmit}>
        {loading ? (
          <>
            <span className="spinner" />
            送信中...
          </>
        ) : (
          '生成開始'
        )}
      </button>

      <p style={{ marginTop: '14px', fontSize: '12px', color: 'var(--muted)', lineHeight: '1.7' }}>
        ※ 台本解析に数秒、画像生成は1枚あたり約15〜30秒かかります。
        <br />
        ※ 生成中に画面を閉じてもジョブは継続されます。URLを保存しておくと再確認できます。
      </p>
    </form>
  );
}
