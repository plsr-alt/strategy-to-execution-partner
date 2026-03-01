import { XaiClient } from '../xai/client';
import { Post, ClusterSchema } from '../schemas/xrsSchema';
import { z } from 'zod';
import { buildClusterPrompt } from '../templates/prompts';

export async function clusterPosts(client: XaiClient, posts: Post[]): Promise<z.infer<typeof ClusterSchema>[]> {
    if (posts.length === 0) return [];

    const postTexts = posts.map(p => `[ID: ${p.id}] ${p.text.substring(0, 300)}`).join('\n---\n');

    const prompt = buildClusterPrompt(postTexts);

    const messages = [
        { role: 'system' as const, content: 'You cluster social media posts into distinct themes and return valid JSON.' },
        { role: 'user' as const, content: prompt }
    ];

    try {
        const response = await client.callGrok(messages, 'grok-2-latest', true);
        if (response && Array.isArray(response.clusters)) {
            return response.clusters;
        }
        return [];
    } catch (e) {
        console.error("Clustering failed", e);
        return [];
    }
}
