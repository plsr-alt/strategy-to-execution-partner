import type { Metadata } from 'next';
import './globals.css';

export const metadata: Metadata = {
  title: '台本→動画カット生成',
  description: '日本語台本から動画カット割りと縦長(9:16)画像を自動生成するツール',
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="ja">
      <body>
        <header className="header">
          <svg
            width="20"
            height="20"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            strokeWidth="2"
            strokeLinecap="round"
            strokeLinejoin="round"
          >
            <rect x="2" y="3" width="20" height="14" rx="2" />
            <line x1="8" y1="21" x2="16" y2="21" />
            <line x1="12" y1="17" x2="12" y2="21" />
          </svg>
          <h1>台本→動画カット生成</h1>
        </header>
        {children}
      </body>
    </html>
  );
}
