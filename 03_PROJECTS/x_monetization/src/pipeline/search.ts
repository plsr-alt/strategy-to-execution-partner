import { XaiClient } from '../xai/client';
import { Post } from '../schemas/xrsSchema';

export async function executeSearch(client: XaiClient, queries: string[], hours: number, lang: string): Promise<Post[]> {
    const allPosts: Post[] = [];
    const seenIds = new Set<string>();

    // Fetch sequentially to avoid rate limits
    for (const q of queries) {
        if (!q) continue;
        console.log(`Searching for: "${q}"...`);
        const posts = await client.searchX(q, 10, hours, lang); // get up to 10 posts per query

        for (const p of posts) {
            if (p && p.id && !seenIds.has(p.id)) {
                seenIds.add(p.id);
                allPosts.push({
                    id: p.id,
                    text: p.text || '',
                    url: p.url || `https://x.com/user/status/${p.id}`,
                    createdAt: p.createdAt || new Date().toISOString(),
                    metrics: p.metrics || {}
                });
            }
        }

        // Slight delay to be polite to the API
        await new Promise(r => setTimeout(r, 1000));
    }

    return allPosts;
}
