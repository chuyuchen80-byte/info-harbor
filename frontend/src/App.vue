<script setup lang="ts">
import { computed, onMounted } from 'vue'
import { RouterView, useRoute } from 'vue-router'
import { NConfigProvider, NMessageProvider, darkTheme, dateZhCN, zhCN } from 'naive-ui'

import FloatingNav from '@/components/nav/FloatingNav.vue'
import { useAuthStore } from '@/stores/auth'
import { useThemeStore } from '@/stores/theme'

const route = useRoute()
const authStore = useAuthStore()
const themeStore = useThemeStore()

const naiveTheme = computed(() => (themeStore.isDark ? darkTheme : null))

/** 登录页为独立分屏页，脱离全局壳（不渲染悬浮导航与页脚）。 */
const isFullscreen = computed(() => !!route.meta.fullscreen)

/** 导航项：管理入口仅 admin 渲染（服务端接口同样 require_roles('admin')，此处只是隐藏入口）。 */
const navItems = computed(() => {
  const items = [
    { path: '/', label: '总览', icon: 'M3 10.5 12 3l9 7.5|M5 9.5V21h14V9.5' },
    { path: '/articles', label: '文章', icon: 'M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z|M14 2v6h6' },
    { path: '/countries', label: '国家/地区', icon: 'M12 22s8-4 8-10a8 8 0 1 0-16 0c0 6 8 10 8 10z|M12 14a2 2 0 1 0 0-4 2 2 0 0 0 0 4z' },
    { path: '/sources', label: '来源', icon: 'M22 12h-4l-3 9L9 3l-3 9H2' },
    { path: '/search', label: '搜索', icon: 'M11 19a8 8 0 1 0 0-16 8 8 0 0 0 0 16z|M21 21l-4.35-4.35' },
  ]
  if (authStore.user?.role === 'admin') {
    items.push({ path: '/admin', label: '管理', icon: 'M3 3h7v7H3z|M14 3h7v7h-7z|M3 14h7v7H3z|M14 14h7v7h-7z' })
  }
  return items
})

onMounted(() => {
  authStore.init()
})
</script>

<template>
  <NConfigProvider :locale="zhCN" :date-locale="dateZhCN" :theme="naiveTheme">
    <NMessageProvider>
      <div class="app-shell" :class="{ fullscreen: isFullscreen }">
        <FloatingNav v-if="!isFullscreen" :items="navItems" />
        <main class="page-container" :class="{ fullscreen: isFullscreen }">
          <RouterView />
        </main>
        <footer v-if="!isFullscreen" class="app-footer">info-harbor · 聚合全球多源 AI 动态</footer>
        <div class="brightness-overlay" />
      </div>
    </NMessageProvider>
  </NConfigProvider>
</template>

<style>
* {
  box-sizing: border-box;
}
html,
body,
#app {
  margin: 0;
  padding: 0;
  min-height: 100%;
}
body {
  background: var(--bg-page);
  color: var(--text-1);
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'PingFang SC',
    'Hiragino Sans GB', 'Microsoft YaHei', sans-serif;
  font-size: 14px;
}
</style>

<style scoped>
.app-shell {
  display: flex;
  flex-direction: column;
  min-height: 100vh;
}
.page-container {
  max-width: 1180px;
  margin: 0 auto;
  padding: 24px;
  width: 100%;
  flex: 1;
}
/* 登录等全屏页：撑满视口、无内边距，布局由页面组件自管 */
.page-container.fullscreen {
  max-width: none;
  padding: 0;
  display: flex;
}
.app-shell.fullscreen {
  min-height: 100vh;
}
.app-footer {
  text-align: center;
  color: var(--text-faint);
  font-size: 12px;
  padding: 20px 0 28px;
}
</style>