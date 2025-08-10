// https://nuxt.com/docs/api/configuration/nuxt-config
export default defineNuxtConfig({
  modules: [
    '@nuxtjs/tailwindcss'
  ],
  css: ['~/assets/css/main.css'],
  runtimeConfig: {
    public: {
      apiBase: process.env.NUXT_PUBLIC_API_BASE || 'http://localhost:8000/api',
      basicAuthUsername: process.env.NUXT_PUBLIC_BASIC_AUTH_USERNAME || 'plant_user',
      basicAuthPassword: process.env.NUXT_PUBLIC_BASIC_AUTH_PASSWORD || 'plant_pass123'
    }
  },
  imports: {
    dirs: [
      'composables/**'
    ]
  },
  // SPAモードで動作
  ssr: false,
  // 動的ルーティング設定
  router: {
    options: {
      strict: false
    }
  },
  // カスタムルーティング設定
  routeRules: {
    // 特定のルートに対する設定
    '/records/**': { prerender: false },
    '/test/**': { prerender: false }
  },
  // DevToolsの設定（本番は無効化）
  devtools: {
    enabled: process.env.NODE_ENV !== 'production'
  },
  // 開発サーバーの設定
  devServer: {
    host: '0.0.0.0',
    port: 3000
  },
  // ビルド設定の最適化
  build: {
    transpile: ['chart.js']
  },
  // 開発環境での安定性向上
  vite: {
    server: {
      watch: {
        usePolling: true
      }
    }
  }
})