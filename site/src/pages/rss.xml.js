import rss from '@astrojs/rss';
import { getCollection } from 'astro:content';

export async function GET(context) {
  const posts = await getCollection('blog', ({ data }) => !data.draft);

  return rss({
    title: 'KORP AI AUTOMATION — Blog',
    description: 'AI Chatbot, Automation, Dashboard สำหรับ SME ไทย — บทความรายวันจากทีม KORP AI',
    site: context.site ?? 'https://korpai.co',
    items: posts
      .sort((a, b) => b.data.pubDate.valueOf() - a.data.pubDate.valueOf())
      .map((post) => ({
        title: post.data.title,
        pubDate: post.data.pubDate,
        description: post.data.description,
        link: `/blog/${post.slug}/`,
        categories: [post.data.category, ...post.data.tags],
        author: 'KORP AI Automation',
      })),
    customData: `<language>th-TH</language><image><url>https://korpai.co/assets/logo-icon.png</url><title>KORP AI AUTOMATION</title><link>https://korpai.co</link></image>`,
    stylesheet: false,
  });
}
