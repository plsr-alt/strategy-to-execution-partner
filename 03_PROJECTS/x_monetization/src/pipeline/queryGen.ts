import { XaiClient } from '../xai/client';
import { CliArgs } from '../schemas/xrsSchema';
import { buildQueryGenPrompt } from '../templates/prompts';

export async function generateQueries(client: XaiClient, args: CliArgs): Promise<string[]> {
    const prompt = buildQueryGenPrompt(args.topic, args.mode, args.lang, args.seed, args.must);

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
