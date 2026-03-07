# リサーチ結果

## 調査テーマ
2026年3月時点で無料で使えるAI画像生成ツール・モデルの最新情報（ローカル実行、クラウドサービス、キャラクター一貫性、動画変換、SNS連携を含む）

---

## 発見事項

| # | 事実 | ソース | 信頼度 |
|---|------|--------|--------|
| 1 | **FLUX.2 [dev]** 2025年11月25日リリース。32Bパラメータ、テキスト・画像編集対応。オープンソース（Apache 2.0ライセンス）。商用利用可（API経由でAPI費用発生）。ローカル実行可（ComfyUI対応、GPU 16-24GB推奨） | [VentureBeat](https://venturebeat.com/technology/black-forest-labs-launches-open-source-flux-2-klein-to-generate-ai-images-in), [Hugging Face](https://huggingface.co/black-forest-labs/FLUX.2-dev) | 高 |
| 2 | **FLUX.2 [klein]** 2026年1月15日リリース。4B・9B版あり。4Bバージョン完全商用利用可（Apache 2.0）。GPU 6-12GBで実行可。最高速0.5秒での生成 | [OpenSourceForYou](https://www.opensourceforu.com/2025/11/black-forest-labs-unveils-flux-2-vae-for-enterprise-ai-image-generation/), [ComfyUI](https://comfyui.org/en/flux2-klein-4b-fast-local-image-editing) | 高 |
| 3 | **FLUX.1 [schnell]** Apache 2.0ライセンス。モデル・生成画像とも商用利用可。fal.ai無料クレジット$1付与。Hugging Face無料配布 | [Trends CodeCamp](https://trends.codecamp.jp/blogs/media/flux-ai), [Bytech](https://bytech.jp/blog/flux1-commercial/) | 高 |
| 4 | **FLUX.1 [dev]** 研究・開発目的。生成画像商用利用可、モデル商用利用不可。無料で利用可（初回無料クレジット有） | [AI総合研究所](https://www.ai-souken.com/article/what-is-flux1) | 高 |
| 5 | **Stable Diffusion 3.5 Large Turbo** 2026年3月公開予定（2025年末～2026年初期）。商用利用無料の条件：年間売上100万ドル未満の個人・組織。Turboは4ステップで高速生成。API: 4クレジット/生成（1000クレジット=$10） | [Stability AI](https://stability.ai/news/introducing-stable-diffusion-3-5), [AI WAVE](https://ai-wave.jp/2025/03/07/stable-diffusion-35-large-turbo/) | 高 |
| 6 | **Stable Diffusion 3.5 Medium** Community License（非商用利用）。オープンソース。ローカル実行可 | [Civitai Education](https://education.civitai.com/getting-started-with-stable-diffusion-3-5/) | 高 |
| 7 | **Hunyuan Image 3.0** 2025年9月28日リリース。80Bパラメータ。オープンソース（Tencent Hunyuan Community License）。商用利用可（100M月次ユーザー超える場合はTencent申請必須）。ローカル実行可。GPU 24GB推奨 | [ComfyUI Wiki](https://comfyui-wiki.com/en/news/2025-09-27-tencent-open-source-hunyuan-image-3-0), [Hugging Face](https://huggingface.co/tencent/HunyuanImage-3.0) | 高 |
| 8 | **Hunyuan 3D 3.0** クラウドサービス。無料：1日20回生成。精度3倍、36億ボクセルUltra-HD | [CGWorld](https://cgworld.jp/flashnews/01-202509-Hunyuan3D-30.html), [Layer](https://www.layer.ai/models/tencent--hunyuan3d-3.0) | 高 |
| 9 | **Kolors** 2024年7月6日リリース。ChatGLM3ベースのテキストエンコーダ。無料利用可。2025年1月KOLORS 1.5で画像参照機能対応。商用利用は別途契約要 | [Hamaruki AI Labs](https://hamaruki.com/beginner-guide-to-amazing-image-generation-with-kolors/), [Zenn](https://zenn.dev/sunwood_ai_labs/articles/amazing-image-generation-with-kolors-beginner-gu) | 中 |
| 10 | **Google Colab 無料枠** T4 GPU 16GB VRAM無料。ただしStable Diffusion使用は Colab Pro($11.99/月)が実質必須。FLUX・SD3.5ローカル実行可 | [るんるんスケッチ](https://runrunsketch.net/stable-diffusion/), [romptn](https://romptn.com/article/5220) | 中 |
| 11 | **ChatGPT 無料版 画像生成** 1日2枚まで無料。2026年2月現在DALL-E 3からGPT Image 1.5に移行。Text-to-image、inpainting/outpainting対応。有料Go($8/月)・Plus($20/月)プランも提供開始 | [ITMedia](https://www.itmedia.co.jp/news/articles/2408/09/news083.html), [Tech & Transition Terrace](https://lib-erty.com/2024/07/04/chatgpt%E3%81%A7%E3%81%AE%E7%94%BB%E5%83%8F%E7%94%9F%E6%88%90dall-e-3%E3%81%AE%E3%81%9F%E3%82%81%E3%81%AE%E5%AE%8C%E5%85%A8%E3%82%AC%E3%82%A4%E3%83%89/) | 高 |
| 12 | **Microsoft Designer / Bing Image Creator** 無料。MAI-Image-1、GPT-4o、DALL-E3選択可。世界共通（ロシア・中国除外） | [Microsoft](https://www.microsoft.com/en-us/edge/features/image-creator), [BigSea](https://bigsea.co/articles/bing-image-creator/) | 高 |
| 13 | **Adobe Firefly** 無料枠：月25クレジット（10画像+2動画生成）。コンテンツ認証情報付与。限定プロモ2026年3月16日まで無制限生成。Standardプラン月680円で月100クレジット | [Adobe FAQ](https://helpx.adobe.com/creative-cloud/apps/generative-ai/generative-credits-faq.html), [Adobe Blog](https://blog.adobe.com/en/publish/2026/02/25/putting-ideas-in-motion-redefining-ai-video-with-adobe-firefly/) | 高 |
| 14 | **Leonardo.ai** 無料：1日150トークン（ほぼ150枚生成可）。商用利用可。無料版は他ユーザーに公開される。将来無料クレジット廃止の可能性 | [Optimization Life](https://optimization-life.com/leonardo-ai/), [Eesel AI](https://www.eesel.ai/blog/leonardo-ai-pricing) | 高 |
| 15 | **Ideogram** 無料：1日25回生成（4枚×25=100枚相当）または1日40枚スロークレジット。商用利用可。無料版は画質若干低下 | [Ideogram完全ガイド](https://media.buzzconne.jp/ideogram_complete_guide/), [Shift AI Times](https://shift-ai.co.jp/blog/6542/) | 高 |
| 16 | **PlaygroundAI v3** 2025年テスト版公開。無料：1000画像/日（実質無制限）。Pro($15/月)で2000画像/日。Image-to-image対応 | [AIBASE](https://www.aibase.com/news/11501), [AI Gallery](https://ai-gallery.jp/tools/playground-ai/) | 高 |
| 17 | **PixArt-δ (Delta)** オープンソース（Huawei・大連工業大学・HuggingFace共同）。0.5秒で1024×1024生成。ローカル実行可。商用利用ライセンス確認必要 | [ARCHETYP Staffing](https://staffing.archetyp.jp/magazine/pixart/) | 中 |
| 18 | **InstantID + IP-Adapter + ComfyUI** 完全無料オープンソース（GitHub・HuggingFace配布）。顔一貫性保持。GPU 12GB以上推奨 | [GitHub ComfyUI-InstantID](https://github.com/cubiq/ComfyUI_InstantID), [MyAIForce](https://myaiforce.com/comfyui-instantid-ipadapter/) | 高 |
| 19 | **LoRA学習 Google Colab** T4 GPU 16GB無料。初心者向けノートブック公開（必要：Googleアカウント、教師画像20-40枚）。2026年3月2日時点で最新版あり | [Colab](https://colab.research.google.com/github/ydaigo/colab-lora-ja/blob/main/colab_lora_ja.ipynb), [SAKASA AI](https://sakasaai.com/what-colablora/) | 高 |
| 20 | **Pika AI** 無料枠：最も太っ腹（詳細不明）。$8/月で追加。他との比較で無料枠が充実 | [Pinggy Blog](https://pinggy.io/blog/best_video_generation_ai_models/), [Pika Labs](https://pikaais.com/comparison/) | 中 |
| 21 | **Runway Gen-4** 無料：125クレジット（カード不要）。月間クレジット制。$10/月-$28/月の有料プラン | [AI速報](https://aisokuho.com/2025/02/18/airunway-pika-kling/), [Max Productive](https://max-productive.ai/ai-tools/runwayml/) | 高 |
| 22 | **KLING AI 2.6** 無料枠あり。$10/月で2分動画。Kuaishouの動画生成モデル。モーション物理演算が評判 | [AI速報](https://aisokuho.com/2025/02/18/airunway-pika-kling/) | 中 |
| 23 | **AnimateDiff** オープンソース（Apache License 2.0）。完全無料。Stable Diffusion拡張機能。ローカル実行可。テキスト→動画、画像→ループアニメ生成 | [AI島](https://ai-island-media.com/2023/09/01/stable-diffusion-animatediff/), [としあきwiki](https://wikiwiki.jp/sd_toshiaki/AnimateDiff) | 高 |
| 24 | **X (Twitter) API** 2026年2月7日から従量課金(Pay-Per-Use)に完全移行。無料枠廃止。フォアグッド(公共利益向け)のみ無料。$10バウチャー1回提供。単価$0.005(投稿読取)～$0.010(ユーザー読取) | [Qiita](https://qiita.com/neru-dev/items/64b0ec92402561e86816), [TechnoEdge](https://www.techno-edge.net/article/2023/03/30/1088.html) | 高 |
| 25 | **Instagram Graph API** ビジネス/クリエイターアカウント専用。詳細な2026年の無料制限情報は公開不十分。Meta Developer公式ドキュメント確認推奨 | [広告.jp](https://www.koukoku.jp/service/suketto/marketer/sns/) | 低 |
| 26 | **Civitai** モデル総数1000K以上。ただし2025年末から支払い処理困難・ポリシー不安定・安定性低下傾向 | [SeaArt Blog](https://www.seaart.ai/blog/civitai-alternative) | 中 |
| 27 | **SeaArt** 無料：1日無制限生成。月訪問22.71M。Civitaiアーカイブ内蔵。モデル数が豊富 | [SeaArt](https://www.seaart.ai/), [SeaArt Blog](https://www.seaart.ai/blog/seaart-vs-civitai) | 高 |
| 28 | **Tensor.Art** 無料：1日100画像（50クレジット日次リセット）。リアル・アニメ両対応。Pro月額有料で300クレジット | [Tensor.Art](https://tensor.art/), [Tooljunction](https://www.tooljunction.io/ai-tools/tensor-art) | 高 |
| 29 | **Canva AI画像生成** 無料：月50回生成（4枚×50=月200枚）。無料版は月200枚制限。Pro月1500円で月500回。生成後に画面閉じるとデータ消失 | [Canva](https://www.canva.com/ja_jp/ai-illust-generator/), [CAD研](https://cad-kenkyujo.com/seisei-ai-gazo/) | 高 |
| 30 | **品質ランキング（2025-2026）** 有料モデルトップはGPT-5.2(0.8285)、Gemini 3 Flash(0.8155)。無料ではFLUX.2・Hunyuan Image 3.0がトップティア。品質面で有料との差は20-30%程度に縮小 | [起業echo](https://sogyotecho.jp/generationai-recommendation/), [DX/AI研究所](https://ai-kenkyujo.com/software/generative-ai/gazo-seiseiai-osusume/) | 中 |

---

## 要点（3〜5個）

- **最強オープンソース**: FLUX.2 [klein](4B/9B、2026年1月)とHunyuan Image 3.0(80B、2025年9月)が無料ローカル実行可で商用利用対応。前者は高速・低VRAM、後者は圧倒的品質。
- **無料クラウド第1選**: ChatGPT無料版(1日2枚)、Bing Image Creator(無制限)、Playground AI(1000/日)。手軽さと品質のバランスではBing推奨。
- **キャラクター一貫性**: InstantID + IP-Adapter + ComfyUIで完全無料実装可。ComfyUI Whyteboardで即座に試行可。LoRA学習も Google Colab 無料枠で可能。
- **SNS連携は死活**: X API完全有料化(2026年2月)で個人開発難化。Instagram Graph APIは情報不足。Webhook/REST規模の自動投稿は個別ツール依存に。
- **動画生成**: Pika・Runway・KLINGは無料枠のみ。AnimateDiffはオープンソース完全無料(Apache 2.0)だがワークフロー複雑。予算無制限ならPika推奨。

---

## 未確認事項

- [推測] FLUX.2 [max]/[pro]の正確なライセンス・商用利用条件（おそらく有料API経由のみ）
- [推測] Hunyuan Image 3.0のコミュニティライセンスが日本適用か、EU/UK除外の詳細判定
- [推測] Instagram Graph APIの2026年3月時点の無料制限（Meta公式ドキュメント更新待機中）
- [推測] 各プラットフォームの今後の無料枠廃止ロードマップ（Leonardo.ai・Civitaiが廃止示唆）
- [推測] FLUX.2系とSD 3.5系の客観的な品質比較（公式ベンチマーク統一基準不在）

