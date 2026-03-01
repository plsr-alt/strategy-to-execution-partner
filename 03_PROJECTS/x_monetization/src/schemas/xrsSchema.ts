import { z } from 'zod';

// Zod schema for the CLI arguments
export const CliArgsSchema = z.object({
    topic: z.string(),
    hours: z.number().default(24),
    count: z.number().default(12),
    lang: z.enum(['ja', 'en']).default('ja'),
    mode: z.enum(['trending', 'buzz', 'balanced']).default('balanced'),
    seed: z.string().optional(),
    must: z.string().optional(),
    locale: z.string().optional(),
    cache: z.boolean().default(true),
    dryRun: z.boolean().default(false),
    out: z.string().optional()
});

export type CliArgs = z.infer<typeof CliArgsSchema>;

// Schema for a single Tweet/Post representation in our pipeline
export const PostSchema = z.object({
    id: z.string(),
    text: z.string(),
    url: z.string().optional(),
    createdAt: z.string(),
    metrics: z.object({
        likes: z.number().optional(),
        retweets: z.number().optional(),
        replies: z.number().optional(),
        views: z.number().optional()
    }).optional()
});

export type Post = z.infer<typeof PostSchema>;

// Schema for Query Generation output
export const GeneratedQueriesSchema = z.object({
    queries: z.array(z.string()).min(12)
});

// Schema for Clustering output
export const ClusterSchema = z.object({
    clusterName: z.string(),
    description: z.string(),
    keywords: z.array(z.string()),
    representativeUrls: z.array(z.string()).max(2),
    sourcePosts: z.array(PostSchema).optional()
});

export const ClustersOutputSchema = z.object({
    clusters: z.array(ClusterSchema).min(3).max(5)
});

// Schema for Final Output formatting
export const ContentIdeaSchema = z.object({
    url: z.string(),
    summary: z.string(),
    metrics: z.string(),
    successHypothesis: z.array(z.string()).max(3),
    postIdeaInvestor: z.string(),
    postIdeaEngineer: z.string(),
    hooks: z.array(z.string()).length(3),
    warning: z.string().optional()
});

export type ContentIdea = z.infer<typeof ContentIdeaSchema>;

export const FinalOutputSchema = z.object({
    clustersOverview: z.array(z.object({
        clusterName: z.string(),
        description: z.string(),
        urls: z.array(z.string())
    })),
    strategicThemes: z.array(z.string()),
    materials: z.array(ContentIdeaSchema)
});

export type FinalOutput = z.infer<typeof FinalOutputSchema>;
