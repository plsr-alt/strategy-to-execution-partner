import { XaiClient } from '../xai/client';
import { Post, ClusterSchema } from '../schemas/xrsSchema';
import { z } from 'zod';

export async function clusterPosts(client: XaiClient, posts: Post[]): Promise<z.infer<typeof ClusterSchema>[]> {
    if (posts.length === 0) return [];

    const postTexts = posts.map(p => `[ID: ${p.id}] ${p.text.substring(0, 300)}`).join('\n---\n');

    const prompt = `You are a top-tier qualitative analyst. Below are recent posts from X (Twitter).
Your task is to extract repeating patterns, common phrases, unique perspectives, or recurring product names from these posts.
Group them into 3 to 5 distinct "Clusters" (themes/topics).
Do not create a cluster for a single isolated post.

Posts:
${postTexts}

Output strictly as a JSON object with a key "clusters". It should be an array of objects.
Each object must have:
- clusterName (string)
- description (string)
- keywords (array of 3-5 strings)
- representativeUrls (array of 1-2 string URLs from the provided posts)

Do not include markdown blocks outside the JSON.`;

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
