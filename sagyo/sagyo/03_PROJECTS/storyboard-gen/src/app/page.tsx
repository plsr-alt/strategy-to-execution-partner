import ScriptForm from '@/components/ScriptForm';

export default function HomePage() {
  return (
    <main className="container" style={{ maxWidth: '720px' }}>
      <h2 style={{ fontSize: '20px', fontWeight: '700', marginBottom: '6px' }}>
        台本をカット分解して画像を一括生成
      </h2>
      <p style={{ color: 'var(--muted)', marginBottom: '28px', lineHeight: '1.7' }}>
        日本語の台本を入力するとAIがカット割りを行い、
        各カットの縦長（9:16）画像を自動生成します。
        完了後はZIPでまとめてダウンロードできます。
      </p>
      <ScriptForm />
    </main>
  );
}
