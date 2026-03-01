export const buildQueryGenPrompt = (topic: string, mode: string, lang: string, seed?: string, must?: string) => `You are a social media research assistant. The user wants to search X (Twitter) for the topic: "${topic}".

Generate exactly 12 diverse search queries to effectively find high-quality, relevant posts.
Parameters:
- Mode: ${mode} (trending=focus on viral/recent, buzz=focus on high engagement/arguments, balanced=mix of both + deep insights)
- Language: ${lang}
${seed ? `- Seed terms to include/focus on: ${seed}\n` : ''}${must ? `- Must include terms: ${must}\n` : ''}

Output strictly as a JSON object with a single key "queries" containing an array of 12 string queries. Do not include markdown formatting outside the JSON.`;

export const buildClusterPrompt = (postTexts: string) => `You are a top-tier qualitative analyst. Below are recent posts from X (Twitter).
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

export const buildRenderPrompt = (postTexts: string, clustersJson: string, targetCount: number) => `You are a professional content strategist for X (Twitter).
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
