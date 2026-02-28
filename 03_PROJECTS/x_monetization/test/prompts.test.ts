import { describe, it, expect } from 'vitest';
import { buildQueryGenPrompt, buildClusterPrompt, buildRenderPrompt } from '../src/templates/prompts';

describe('Prompt Templates', () => {
    it('buildQueryGenPrompt generates the expected prompt string', () => {
        const prompt = buildQueryGenPrompt('web3 infra', 'balanced', 'ja', 'Agent Teams', 'blockchain');

        expect(prompt).toContain('The user wants to search X (Twitter) for the topic: "web3 infra"');
        expect(prompt).toContain('Mode: balanced');
        expect(prompt).toContain('Language: ja');
        expect(prompt).toContain('- Seed terms to include/focus on: Agent Teams');
        expect(prompt).toContain('- Must include terms: blockchain');
    });

    it('buildClusterPrompt includes the posts payload', () => {
        const posts = '[ID: 1] test post';
        const prompt = buildClusterPrompt(posts);

        expect(prompt).toContain(posts);
        expect(prompt).toContain('Output strictly as a JSON object with a key "clusters"');
    });

    it('buildRenderPrompt includes posts, clusters, and target count', () => {
        const prompt = buildRenderPrompt('[ID: 1]', '{"clusters":[]}', 5);

        expect(prompt).toContain('generate exactly 5 content material ideas');
        expect(prompt).toContain('Posts sample:\n[ID: 1]');
        expect(prompt).toContain('Clusters identified:\n{"clusters":[]}');
    });
});
