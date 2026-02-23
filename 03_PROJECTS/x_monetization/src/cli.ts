#!/usr/bin/env node
import { Command } from 'commander';
import * as dotenv from 'dotenv';
import * as fs from 'fs';
import { XaiClient } from './xai/client';
import { CliArgsSchema, Post } from './schemas/xrsSchema';
import { generateQueries } from './pipeline/queryGen';
import { executeSearch } from './pipeline/search';
import { clusterPosts } from './pipeline/cluster';
import { enrichClusters } from './pipeline/enrich';
import { renderFinalOutput } from './pipeline/render';

dotenv.config();

const program = new Command();

program
    .name('xrs')
    .description('CLI for automated X (Twitter) research using xAI API')
    .version('1.0.0');

program
    .command('run')
    .description('Run a research pipeline on a topic')
    .requiredOption('--topic <string>', 'Topic to research')
    .option('--hours <number>', 'Time window in hours', '24')
    .option('--count <number>', 'Number of material items to generate', '12')
    .option('--lang <string>', 'Language preference', 'ja')
    .option('--mode <string>', 'trending | buzz | balanced', 'balanced')
    .option('--seed <string>', 'Seed terms, comma separated')
    .option('--must <string>', 'Must-include words')
    .option('--locale <string>', 'Locale')
    .option('--no-cache', 'Disable cache')
    .option('--dry-run', 'Generate queries only without full execution')
    .option('--out <string>', 'Output markdown file path')
    .action(async (options) => {
        try {
            const args = CliArgsSchema.parse({
                ...options,
                hours: parseInt(options.hours, 10),
                count: parseInt(options.count, 10),
            });

            const apiKey = process.env.XAI_API_KEY;
            if (!apiKey) {
                console.error("ERROR: XAI_API_KEY environment variable is missing.");
                process.exit(1);
            }

            console.log(`Starting Research for: "${args.topic}"`);
            const client = new XaiClient(apiKey, args.cache);

            // STEP A: Query Generation
            console.log(`\n[STEP A] Generating Queries...`);
            const queries = await generateQueries(client, args);
            console.log(`Generated ${queries.length} queries.`);
            queries.slice(0, 3).forEach(q => console.log(`  - ${q}`));

            if (args.dryRun) {
                console.log(`\n[DRY RUN] Operation completed. Generated queries won't be executed.`);
                process.exit(0);
            }

            // STEP B: Initial Search
            console.log(`\n[STEP B] Searching X...`);
            const posts = await executeSearch(client, queries, args.hours, args.lang);
            console.log(`Found ${posts.length} unique posts.`);

            if (posts.length === 0) {
                console.warn("No posts found. Exiting.");
                process.exit(0);
            }

            // STEP C: Clustering
            console.log(`\n[STEP C] Extracting Clusters...`);
            const clusters = await clusterPosts(client, posts);
            console.log(`Identified ${clusters.length} clusters.`);
            clusters.forEach(c => console.log(`  - ${c.clusterName}`));

            // STEP D: Enrich via extra search
            console.log(`\n[STEP D] Enriching Clusters with focused search...`);
            const newPosts = await enrichClusters(client, clusters, args.hours, args.lang);
            console.log(`Found ${newPosts.length} additional posts for enrichment.`);

            const allPosts = [...posts, ...newPosts];
            const uniquePosts = Array.from(new Map(allPosts.map(item => [item.id, item])).values());
            console.log(`Total unique posts after enrichment: ${uniquePosts.length}`);

            // STEP E & F: Render Final Output
            console.log(`\n[STEP F] Generating Final Markdown Report...`);
            const markdown = await renderFinalOutput(client, clusters, uniquePosts, args.count);

            if (args.out) {
                fs.writeFileSync(args.out, markdown, 'utf8');
                console.log(`\n✅ Success! Report written to ${args.out}`);
            } else {
                console.log(`\n✅ Success! Report:\n`);
                console.log(markdown);
            }

        } catch (e: any) {
            console.error(`\n❌ Error: ${e.message}`);
            process.exit(1);
        }
    });

program.parse();
