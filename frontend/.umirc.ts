import { defineConfig } from 'umi';

export default defineConfig({
  nodeModulesTransform: {
    type: 'none',
  },
  history: { type: 'hash' },
  routes: [
    {
      exact: false, path: '/', component: '@/layouts/index',
      routes: [
        { path: '/', component: '@/pages/index' },
        { path: '/home/recommend', component: '@/pages/home/recommend' },
        { path: '/home/playlist', component: '@/pages/home/playlist' },
        { path: '/home/radio', component: '@/pages/home/radio' },
        { path: '/home/rank', component: '@/pages/home/rank' },
        { path: '/home/singer', component: '@/pages/home/singer' },
        { path: '/home/news', component: '@/pages/home/news' },

        { path: '/my/index', component: '@/pages/my/index' },
        { path: '/my/cloud', component: '@/pages/my/cloud' },
        { path: '/my/favorite', component: '@/pages/my/favorite' },
        { path: '/my/local', component: '@/pages/my/local' },
        { path: '/my/playlist', component: '@/pages/my/playlist' },
        { path: '/my/radio', component: '@/pages/my/radio' },
      ],
    }
  ],
  fastRefresh: {},
});