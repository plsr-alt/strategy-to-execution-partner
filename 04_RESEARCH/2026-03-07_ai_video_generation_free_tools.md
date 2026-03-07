# リサーチ結果

## 調査テーマ
2026年3月時点で無料で使える AI動画生成・画像→動画変換ツールの最新情報

## 発見事項

| # | 事実 | ソース | 信頼度 |
|---|------|--------|--------|
| 1 | **Runway Gen-3** 無料枠：125クレジット付与。Gen-3 Alpha Turboで1秒5クレジット消費→合計25秒まで生成可能。10秒制限あり。透かし・解像度上限あり。商用利用不可。 | [Runway Gen-3 料金・使い方解説](https://workup-ai.com/runway-gen3-price/) | 高 |
| 2 | **Pika 1.5** 無料枠：月80〜150クレジット（情報源により差異）。毎月リセット。追加購入不可（次月まで待機）。透かし付き。商用利用不可。 | [Pika 無料会員できること](https://fragments.co.jp/blog/pika-muryo/) | 中 |
| 3 | **Kling AI** 無料枠：毎日66クレジット付与（翌日繰越不可）。最大10秒、720p、Standard品質のみ。生成時間が長い。透かし付き。商用利用不可。 | [Kling AI 無料枠制限 2026年](https://videobeginners.com/kling-ai-free/) | 高 |
| 4 | **Luma Dream Machine** 無料枠：月500クレジット。月8回まで無料生成（Ray 3.14 Draftモード）。1日10回・月30回生成可能。5秒（120フレーム）まで。透かし付き。商用利用不可。 | [Luma AI Dream Machine 2026年版](https://design-offset.com/luma-ai-dream-machine-free-plan/) | 高 |
| 5 | **Hailuo AI（MiniMax開発）** 無料枠：毎日ログインボーナスクレジット。正確な月数未公表。最新モデル Hailuo 2.3 は1080p、1分以内で生成。テキスト→動画、画像→動画対応。 | [Hailuo AI 無料トライアル](https://shift-ai.co.jp/blog/10567/) | 中 |
| 6 | **Vidu AI（2026年2月最新）** 無料枠：Text/Image→Video 6回、Reference→Video 2回、計8回無料。Off-Peak Mode では無制限無料生成。月80クレジット。Vidu Q3（2026年2月リリース）は16秒、音声付き、1080p対応。透かし付き。商用利用不可。 | [Vidu.aiとは 2026年最新](https://tohma-style.com/what-is-vidu-ai/) | 高 |
| 7 | **OpenAI Sora 2** 無料枠：ChatGPT Free 非対応。ChatGPT Plus（$20/月）で無制限480p生成、ChatGPT Pro（$200/月）で10,000クレジット上限1080p。API価格：$0.10/秒（720p）、$0.30-0.50/秒（1024p）。Sora 1 は2026年3月13日で廃止予定。15-25秒生成対応。 | [OpenAI Sora 2 Complete Guide 2026](https://wavespeed.ai/blog/posts/openai-sora-2-complete-guide-2026/) | 高 |
| 8 | **Google Veo 3** Gemini API 統合。4K出力対応。リアルな物理表現・音声同期。無料枠の詳細は公式ドキュメント参照（2026年3月時点で API提供中）。 | [Google Veo 3 on Gemini API](https://ai.google.dev/gemini-api/docs/video) | 中 |
| 9 | **CogVideoX（清華大学×Zhipu AI）** オープンソース。2B・5B版。6秒→10秒720pに拡張（最新版）。モーション改良。最小要件VRAM 16GB。Apache 2.0ライセンス（商用OK）。ComfyUI 統合。 | [CogVideoX テキスト→動画](https://www.runcomfy.com/ja/comfyui-workflows/cogvideox5b-text-to-video-model-available-in-comfyui) | 高 |
| 10 | **Stable Video Diffusion（SVD）** オープンソース（Stability AI）。SVD-XT：25フレーム、SV4D 2.0：48フレーム（576×576）。231,198月間ダウンロード（2025年時点）。Google Colab 対応。Apache 2.0相当（商用検証要）。 | [Stable Video Diffusion Statistics 2026](https://www.quantumrun.com/consulting/stable-video-diffusion-statistics/) | 高 |
| 11 | **AnimateDiff** オープンソース。Stable Diffusion 1.5/1.4/SDXL 統合。モーション追加（ズーム・パン・回転）。8-12GB VRAM で動作。Google Colab で数分で生成。ByteDance 蒸留版で高速化。 | [AnimateDiff Google Colab](https://note.com/npaka/n/n3af415daa362) | 高 |
| 12 | **Wan 2.1-VACE（Alibaba）** 2025年5月公開のオープンソース。14B・1.3B版をHugging Face/GitHub で無料ダウンロード。VBench スコア 86.22%（Sora 84.28% より上）。テキスト・画像・動画入力対応。1.3B版は VRAM 8.19GB で動作。 | [Alibaba Wan2.1 Open-Source on ComfyUI Wiki](https://comfyui-wiki.com/en/news/2025-02-25-alibaba-wanx-2-1-video-model-open-source) | 高 |
| 13 | **Wan 2.6（Alibaba最新）** 多シーン 1080p 生成。ネイティブ音声同期。キャラ安定性向上。API 版で低コスト提供。 | [Kie.ai Wan 2.6 API](https://kie.ai/wan-2-6) | 中 |
| 14 | **Ken Burns 効果** FFmpeg 実装：`ffmpeg -i in.jpg -filter_complex "zoompan=z='zoom+0.002':d=25*4:s=1280x800" out.mp4`。Python MoviePy：`clip.resize(lambda t: 1 + 0.1*t)`。3D Ken Burns（PyTorch）：GitHub でリファレンス実装公開。Colab Notebook 版あり。 | [Ken Burns FFmpeg Bannerbear](https://www.bannerbear.com/blog/how-to-do-a-ken-burns-style-effect-with-ffmpeg/) | 高 |
| 15 | **OpenAI Whisper** オープンソース。日本語含む80言語対応。5 モデルサイズ（tiny-large）。ローカル実行無料。SRT 字幕形式出力対応。Python 実装例多数。自動字幕・文字起こし用途で 2025年以降も現役。 | [Whisper Qiita 使い方ガイド](https://qiita.com/automation2025/items/a2a21cc7d41279c495be) | 高 |
| 16 | **FFmpeg 自動化スクリプト** 画像シーケンス→タイムラプス、音声+静止画→動画、一括エンコード。Bash/Python ループ処理で複数ファイル対応。`</dev/null` 指定で Bash ループ内実行可能。 | [FFmpeg 動画生成自動化 DevelopersIO](https://dev.classmethod.jp/articles/ffmpeg-image-audio) | 高 |
| 17 | **Google Colab 無料枠** GPU T4（VRAM 15GB）。SVD・AnimateDiff・3D Ken Burns 実行可能。毎日一定時間制限あり。オープンソースモデルならほぼ全て動作。 | [ComfyUI on Google Colab](https://comfyui-wiki.com/en/install/install-comfyui/run-comfyui-colab) | 高 |

## 要点（3〜5個）

- **無料サービス** 上位5選（無料枠 月間総秒数目安）：**Vidu（月8回無料）> Luma Dream Machine（月8回）> Kling AI（毎日66クレジット）> Runway Gen-3（月25秒）> Pika 1.5（月80-150クレジット）**。全て透かし・商用利用不可。

- **オープンソースモデル最強構成** ：**Alibaba Wan 2.1（1.3B版・VRAM 8GB）+ Google Colab 無料 GPU** →品質（VBench 86%）と手軽さの両立。商用利用可（ライセンス確認要）。

- **Ken Burns 効果 + Whisper 自動字幕** ：FFmpeg/MoviePy で Ken Burns エフェクト、Whisper でAI文字起こし→業務自動化可能。全て無料・オープンソース。

- **2026年の分岐** ：有料契約なし → Vidu Q3（月8回無料）・ローカルオープンソース推奨。ChatGPT Plus 加入可 → Sora 2 480p 無制限。ローカル環境構築可 → Wan 2.1/CogVideoX 推奨。

- **新興プレイヤー** Hailuo AI（中国発）は毎日無料クレジット配布、1080p 対応。Vidu Q3（2026年2月新機能：音声同期 16秒生成）は Pika・Runway を上回る無料試用価値。

## 未確認事項

- [推測] Hailuo AI の無料枠「毎日ログインボーナス」の正確な月間クレジット総数。公式ドキュメントでは「毎日付与」と記載されるが、月上限の明記がない。

- [推測] Google Veo 3 の無料 API 枠。Gemini API ドキュメントでは動画生成が統合されたが、月間回数・クレジット制限の詳細が公開されていない（2026年3月時点）。

- [推測] Alibaba Wan 2.1 のクリエイティブ・商用利用時の法的リスク。オープンソース（Apache 2.0）だが、学習データの出所（中国政府規制）に関する明示がない。

- [推測] OpenAI Sora 2 API 利用時、日本からのアクセス制限の有無。ChatGPT Plus は日本対応が確認されたが、API 版の国別制限未確認。

- [推測] Stable Video Diffusion の最新版（SV4D 2.0）がローカル・Colab で安定実行するまでの推奨 VRAM。公式スペック 16GB だが、実測値の報告が少ない。
