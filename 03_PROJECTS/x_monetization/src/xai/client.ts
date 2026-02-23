import { getCachedResponse, setCachedResponse } from '../cache';

const XAI_API_URL = 'https://api.x.ai/v1/chat/completions'; // Using standard chat completions endpoint for Grok

export interface GrokMessage {
    role: 'system' | 'user' | 'assistant';
    content: string;
}

export class XaiClient {
    private apiKey: string;
    private useCache: boolean;

    constructor(apiKey: string, useCache: boolean = true) {
        this.apiKey = apiKey;
        this.useCache = useCache;
    }

    // Generic Grok API Call with Retry & Cache
    async callGrok(messages: GrokMessage[], model: string = 'grok-2-latest', responseFormat?: any): Promise<any> {
        const payload: any = {
            model,
            messages,
            temperature: 0.3,
        };

        if (responseFormat) {
            // If Grok supports structured output via json_object or tools, we append it here
            // For simplicity, we assume we request JSON in the prompt if responseFormat is not strictly enforced by API yet.
            // But we can add standard formatting flags if supported.
            payload.response_format = { type: 'json_object' };
        }

        if (this.useCache) {
            const cached = getCachedResponse<any>('grok_chat', payload);
            if (cached) return cached;
        }

        let attempt = 0;
        const maxRetries = 3;

        while (attempt < maxRetries) {
            try {
                const response = await fetch(XAI_API_URL, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'Authorization': `Bearer ${this.apiKey}`
                    },
                    body: JSON.stringify(payload)
                });

                if (!response.ok) {
                    const errText = await response.text();
                    throw new Error(`XAI API Error ${response.status}: ${errText}`);
                }

                const data = await response.json();
                const content = data.choices[0].message.content;

                let result = content;
                if (payload.response_format?.type === 'json_object') {
                    try {
                        // strip markdown formatting if any
                        const cleanStr = content.replace(/```json/g, '').replace(/```/g, '').trim();
                        result = JSON.parse(cleanStr);
                    } catch (e) {
                        console.error("Failed to parse JSON response:", content);
                        throw new Error("Invalid JSON response from Grok");
                    }
                }

                if (this.useCache) {
                    setCachedResponse('grok_chat', payload, result);
                }

                return result;

            } catch (err: any) {
                attempt++;
                console.warn(`Grok API call failed (Attempt ${attempt}/${maxRetries}): ${err.message}`);
                if (attempt >= maxRetries) throw err;
                await new Promise(r => setTimeout(r, 1000 * Math.pow(2, attempt))); // Exponential backoff
            }
        }
    }

    // Simulated "Search" using Grok. Since xAI Grok has real-time X access when used strictly,
    // we prompt it to perform a search and return recent matching posts.
    // Note: To truly use X Search API natively you'd use Twitter API v2. But the instruction says:
    // "xAI(Grok) API クライアント... “検索”をするための関数 searchX() を用意"
    // Assuming Grok model can fetch recent posts if instructed to search real-time.
    async searchX(query: string, limit: number, timeWindowHours: number, lang: string): Promise<any[]> {
        const systemPrompt = `You are a real-time web and X (Twitter) search agent. Your task is to find recent, highly relevant posts on X regarding the user's query from the last ${timeWindowHours} hours. Language preference: ${lang}. Return ONLY a valid JSON array of objects representing posts. Each object must have fields: 'id'(string), 'text'(string), 'url'(string), 'createdAt'(string), 'metrics'(object with likes, retweets, replies, views). Do not prepend or append any markdown or text outside the JSON array.`;

        const userPrompt = `Query: "${query}"\nPlease return up to ${limit} top or most relevant results. Avoid spam or unrelated posts.`;

        const messages: GrokMessage[] = [
            { role: 'system', content: systemPrompt },
            { role: 'user', content: userPrompt }
        ];

        try {
            const posts = await this.callGrok(messages, 'grok-2-latest', true);
            if (Array.isArray(posts)) {
                return posts;
            }
            if (posts && Array.isArray(posts.posts)) {
                return posts.posts;
            }
            return [];
        } catch (err) {
            console.error(`Search failed for query "${query}"`, err);
            return [];
        }
    }
}
