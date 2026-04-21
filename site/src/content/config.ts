import { defineCollection, z } from 'astro:content';

const blog = defineCollection({
  type: 'content',
  schema: z.object({
    title: z.string(),
    description: z.string(),
    pubDate: z.coerce.date(),
    updatedDate: z.coerce.date().optional(),
    heroImage: z.string().optional(),
    category: z.enum(['AI Chatbot', 'Automation', 'Dashboard', 'LLM / RAG', 'SME Strategy']),
    tags: z.array(z.string()).default([]),
    readingMinutes: z.number().int().positive().default(5),
    draft: z.boolean().default(false),
    author: z.string().default('ทีม KORP AI'),
  }),
});

export const collections = { blog };
