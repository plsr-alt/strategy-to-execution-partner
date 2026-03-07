# Groq 実行プロンプト：AIインフルエンサー市場調査

**実行環境**: WSL
**モデル**: llama-3.3-70b-versatile
**用途**: 調査結果の分析レポート生成（CrewAI report.json を受け取った後の2次処理）

---

## プロンプト

以下のプロンプトを Groq API に投入してください。

```
You are a strategic market research analyst specializing in social media influencer economy.

Analyze the AI virtual influencer market (2025-2026) and provide a comprehensive JSON-structured report covering:

1. **Top 10 Global AI Influencers**: List by follower count (Instagram, TikTok, YouTube). Include:
   - Name, platform, follower count
   - Concept/niche (e.g., beauty, finance, lifestyle, travel)
   - Revenue model (sponsorships, affiliate, merchandise, NFT)
   - AI generation tools used (Midjourney, Stable Diffusion, FLUX)
   - Success factors

2. **Japan Domestic AI/Virtual Influencers** (5+ cases):
   - Name, platform, follower count
   - Concept
   - Revenue status (verified earnings if available)
   - Success factors and challenges

3. **2025-2026 Trends**:
   - Regulatory landscape: AI disclosure requirements on Instagram, TikTok
   - Hot genres/niches (beauty, finance, lifestyle, travel)
   - Technology trends (LoRA, InstantID, video generation, real-time streaming)
   - Saturated genres vs. blue ocean opportunities

4. **Concept Viability Analysis** (Japanese market focus):
   - "Finance + AI Female": Market potential, risk factors, success examples
   - "Tech + Lifestyle": Target audience, monetization paths
   - "Travel + AI": Unique value proposition, monetization models
   - Other blue ocean concepts (emerging niches for Japan)

5. **Monetization Reality**:
   - Earnings per follower by tier (10K-100K, 100K-1M, 1M+)
   - Impact of AI disclosure on engagement rates and sponsorship rates
   - Verified monthly income examples (if available)
   - Average CPM/CPC for AI influencer sponsored posts

Output format: **Structured JSON with sources cited as URLs**

Format:
{
  "global_top_10": [...],
  "japan_cases": [...],
  "trends_2025_2026": {...},
  "concept_analysis": {...},
  "monetization": {...},
  "sources": ["URL1", "URL2", ...]
}

Be precise with data. Mark assumptions with [推測] prefix. Cite all sources.
```

---

## 実行方法（WSL）

```bash
source /home/crewai/.venv/bin/activate
python -c "
from groq import Groq

client = Groq()
response = client.chat.completions.create(
    model='llama-3.3-70b-versatile',
    messages=[{
        'role': 'user',
        'content': '''You are a strategic market research analyst specializing in social media influencer economy...
        [上記プロンプト全文を挿入]
        '''
    }],
    temperature=0.7,
    max_tokens=4000
)

print(response.choices[0].message.content)
" > /tmp/groq_output.txt

cat /tmp/groq_output.txt
```

---

## 出力ファイル配置

実行結果を以下に配置：
- **JSON出力**: `20_worker_outputs/groq_analysis.json`
- **テキスト出力**: `20_worker_outputs/groq_analysis.txt`

---

## 実行タイミング

- **CrewAI実行成功後** → Groq実行（追加分析が必要な場合）
- または
- **CrewAIの代替手段** として直接実行（Web検索が不要な場合）
