import { XaiClient } from '../xai/client';
import { Post, ClusterSchema, FinalOutputSchema, ContentIdeaSchema } from '../schemas/xrsSchema';
import { z } from 'zod';
import { buildRenderPrompt } from '../templates/prompts';

export async function renderFinalOutput(client: XaiClient, clusters: z.infer<typeof ClusterSchema>[], allPosts: Post[], targetCount: number): Promise<string> {
    const postTexts = allPosts.slice(0, 50).map(p => `[ID: ${p.id}, URL: ${p.url}, Likes: ${p.metrics?.likes || 0}] ${p.text.substring(0, 200)}`).join('\n---\n');
    const clustersJson = JSON.stringify(clusters, null, 2);

    const prompt = buildRenderPrompt(postTexts, clustersJson, targetCount);

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
        data.materials.forEach((m: z.infer<typeof ContentIdeaSchema>, idx: number) => {
            md += `### ${idx + 1}. 素材ソース\n`;
            md += `- **URL**: ${m.url}\n`;
            md += `- **エンゲージ指標**: ${m.metrics}\n`;
            md += `- **要約**: ${m.summary}\n`;
            md += `- **なぜ伸びたか**: ${m.successHypothesis.join(', ')}\n`;
            md += `- **ネタ案 (投資家向け)**: ${m.postIdeaInvestor}\n`;
            md += `- **ネタ案 (エンジニア向け)**: ${m.postIdeaEngineer}\n`;
            md += `- **フック案**:\n`;
            m.hooks.forEach((h: string) => md += `  - ${h}\n`);
            if (m.warning) {
                md += `- **⚠️ 注意**: ${m.warning}\n`;
            }
            md += '\n';
        });

        md += `## 参照URL一覧\n\n`;
        data.materials.forEach((m: z.infer<typeof ContentIdeaSchema>) => {
            md += `- ${m.url}\n`;
        });

        return md;

    } catch (e) {
        console.error("Rendering failed", e);
        return `# Error generating report\n\nCheck logs for details.`;
    }
}
