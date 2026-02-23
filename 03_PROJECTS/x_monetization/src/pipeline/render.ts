import { XaiClient } from '../xai/client';
import { Post, ClusterSchema, FinalOutputSchema } from '../schemas/xrsSchema';
import { z } from 'zod';

export async function renderFinalOutput(client: XaiClient, clusters: z.infer<typeof ClusterSchema>[], allPosts: Post[], targetCount: number): Promise<string> {
    const postTexts = allPosts.slice(0, 50).map(p => `[ID: ${p.id}, URL: ${p.url}, Likes: ${p.metrics?.likes || 0}] ${p.text.substring(0, 200)}`).join('\n---\n');
    const clustersJson = JSON.stringify(clusters, null, 2);

    const prompt = `You are a professional content strategist for X (Twitter).
Based on the provided Clusters and a sample of Posts, generate exactly ${targetCount} content material ideas.
Do NOT directly quote long texts. Use short summaries or paraphrasing.
ABSOLUTELY NO financial advice, buy/sell recommendations, or price targets. Instead, provide a 1-line warning/disclaimer if the topic borders on investing.

Posts sample:
${postTexts}

Clusters identified:
${clustersJson}

Output MUST be a valid JSON object matching this structure:
{
  "clustersOverview": [
    { "clusterName": "Name", "description": "Brief desc", "urls": ["url1", "url2"] }
  ],
  "strategicThemes": [ "Theme 1", "Theme 2", "Theme 3" ],
  "materials": [
    {
      "url": "source url",
      "summary": "1-2 line summary in your own words",
      "metrics": "Likes: 100, Repos: 10 (or unknown)",
      "successHypothesis": ["Reason 1", "Reason 2"],
      "postIdeaInvestor": "Idea tailored for investors (neutral tone)",
      "postIdeaEngineer": "Idea tailored for engineers",
      "hooks": ["Hook 1", "Hook 2", "Hook 3"],
      "warning": "Disclaimer if needed"
    }
  ]
}
Ensure there are exactly ${targetCount} items in "materials".
Strictly output ONLY valid JSON without any surrounding markdown formatting (\`\`\`json).`;

    const messages = [
        { role: 'system' as const, content: 'You are an expert X/Twitter content strategist. You strictly format output as valid JSON without markdown tags.' },
        { role: 'user' as const, content: prompt }
    ];

    try {
        const response = await client.callGrok(messages, 'grok-2-latest', true);

        // Parse response
        const data = FinalOutputSchema.parse(response);

        // Convert to Markdown
        let md = `# X Research Skills (xrs) Report\n\n`;

        md += `## タイムラインの空気（論点のクラスター）\n\n`;
        for (const c of data.clustersOverview) {
            md += `### ${c.clusterName}\n`;
            md += `${c.description}\n`;
            md += `代表ポスト:\n`;
            for (const u of c.urls) {
                md += `- ${u}\n`;
            }
            md += '\n';
        }

        md += `## 今日の結論（狙うべきテーマ）\n\n`;
        for (const t of data.strategicThemes) {
            md += `- ${t}\n`;
        }
        md += '\n';

        md += `## 素材一覧 (${data.materials.length}件)\n\n`;
        data.materials.forEach((m, idx) => {
            md += `### ${idx + 1}. 素材ソース\n`;
            md += `- **URL**: ${m.url}\n`;
            md += `- **エンゲージ指標**: ${m.metrics}\n`;
            md += `- **要約**: ${m.summary}\n`;
            md += `- **なぜ伸びたか**: ${m.successHypothesis.join(', ')}\n`;
            md += `- **ネタ案 (投資家向け)**: ${m.postIdeaInvestor}\n`;
            md += `- **ネタ案 (エンジニア向け)**: ${m.postIdeaEngineer}\n`;
            md += `- **フック案**:\n`;
            m.hooks.forEach(h => md += `  - ${h}\n`);
            if (m.warning) {
                md += `- **⚠️ 注意**: ${m.warning}\n`;
            }
            md += '\n';
        });

        md += `## 参照URL一覧\n\n`;
        data.materials.forEach((m) => {
            md += `- ${m.url}\n`;
        });

        return md;

    } catch (e) {
        console.error("Rendering failed", e);
        return `# Error generating report\n\nCheck logs for details.`;
    }
}
