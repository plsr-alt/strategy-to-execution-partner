import { XaiClient } from '../xai/client';
import { Post, ClusterSchema } from '../schemas/xrsSchema';
import { z } from 'zod';
import { executeSearch } from './search';

export async function enrichClusters(client: XaiClient, clusters: z.infer<typeof ClusterSchema>[], hours: number, lang: string): Promise<Post[]> {
    const additionalPosts: Post[] = [];

    for (const cluster of clusters) {
        if (!cluster.keywords || cluster.keywords.length === 0) continue;

        // Create highly specific queries from cluster keywords
        const topKeywords = cluster.keywords.slice(0, 3).join(' OR ');
        const query = `(${topKeywords}) min_faves:10`;
        console.log(`Enriching cluster "${cluster.clusterName}" with query: ${query}`);

        const enriched = await executeSearch(client, [query], hours, lang);
        additionalPosts.push(...enriched);
    }

    return additionalPosts;
}
