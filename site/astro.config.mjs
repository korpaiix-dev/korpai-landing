import { defineConfig } from 'astro/config';
import tailwind from '@astrojs/tailwind';

// https://astro.build/config
export default defineConfig({
  site: 'https://korpai.co',
  trailingSlash: 'never',
  integrations: [
    tailwind({ applyBaseStyles: false }),
  ],
  build: {
    assets: '_assets',
  },
  vite: {
    server: { hmr: { overlay: false } },
  },
});
