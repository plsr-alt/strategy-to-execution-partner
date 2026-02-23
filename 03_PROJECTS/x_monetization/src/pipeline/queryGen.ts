import { XaiClient } from '../xai/client';
import { CliArgs } from '../schemas/xrsSchema';

export async function generateQueries(client: XaiClient, args: CliArgs): Promise<string[]> {
    const prompt = `You are a social media research assistant. The user wants to search X (Twitter) for the topic: "${args.topic}".
  
Generate exactly 12 diverse search queries to effectively find high-quality, relevant posts.
Parameters:
- Mode: ${args.mode} (trending=focus on viral/recent, buzz=focus on high engagement/arguments, balanced=mix of both + deep insights)
- Language: ${args.lang}
${args.seed ? `- Seed terms to include/focus on: ${args.seed}\n` : ''}${args.must ? `- Must include terms: ${args.must}\n` : ''}

Output strictly as a JSON object with a single key "queries" containing an array of 12 string queries. Do not include markdown formatting outside the JSON.`;

    const messages = [
        { role: 'system' as const, content: 'You generate highly effective search queries for X (Twitter).' },
        { role: 'user' as const, content: prompt }
    ];

    try {
        const response = await client.callGrok(messages, 'grok-2-latest', true);
        if (response && Array.isArray(response.queries)) {
            return response.queries;
        }
        return [args.topic]; // Fallback
    } catch (e) {
        console.error("Query generation failed", e);
        return [args.topic]; // Fallback
    }
}
