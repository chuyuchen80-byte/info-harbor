<script setup lang="ts">
import { computed, onMounted } from 'vue'
import { RouterLink, RouterView, useRoute, useRouter } from 'vue-router'
import {
  NConfigProvider,
  NMessageProvider,
  darkTheme,
  dateZhCN,
  zhCN,
} from 'naive-ui'

import { useAuthStore } from '@/stores/auth'
import { useThemeStore } from '@/stores/theme'

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()
const themeStore = useThemeStore()

const naiveTheme = computed(() => (themeStore.isDark ? darkTheme : null))

/** 导航项：管理入口仅 admin 渲染（服务端接口同样 require_roles('admin')，此处只是隐藏入口）。 */
const navItems = computed(() => {
  const items = [
    { path: '/', label: '总览' },
    { path: '/articles', label: '文章' },
    { path: '/countries', label: '国家/地区' },
    { path: '/sources', label: '来源' },
    { path: '/search', label: '搜索' },
  ]
  if (authStore.user?.role === 'admin') {
    items.push({ path: '/admin', label: '管理' })
  }
  return items
})

function isActive(path: string): boolean {
  if (path === '/') return route.path === '/'
  return route.path.startsWith(path)
}

function handleLogout() {
  authStore.logout()
  router.push('/login')
}

onMounted(() => {
  authStore.init()
})
</script>

<template>
  <NConfigProvider :locale="zhCN" :date-locale="dateZhCN" :theme="naiveTheme">
    <NMessageProvider>
      <div class="app-shell">
        <header class="app-header">
          <div class="header-inner">
            <RouterLink to="/" class="brand">
              <span class="brand-mark">
                <svg viewBox="0 0 24 24" width="18" height="18" fill="none">
                  <path
                    d="M12 2l2.4 7.6H22l-6.2 4.5 2.4 7.6L12 17.2l-6.2 4.5 2.4-7.6L2 9.6h7.6L12 2z"
                    fill="currentColor"
                  />
                </svg>
              </span>
              <span class="brand-text">
                <span class="brand-name">info-harbor</span>
                <span class="brand-sub">全球 AI 资讯聚合</span>
              </span>
            </RouterLink>
            <nav class="nav">
              <RouterLink
                v-for="item in navItems"
                :key="item.path"
                :to="item.path"
                class="nav-link"
                :class="{ active: isActive(item.path) }"
              >
                {{ item.label }}
              </RouterLink>
            </nav>
            <div class="theme-toggle" @click="themeStore.toggle()" title="切换深色/浅色">
              <svg v-if="themeStore.isDark" viewBox="0 0 24 24" width="16" height="16" fill="none">
                <circle cx="12" cy="12" r="4.5" fill="currentColor" />
                <path
                  d="M12 2.5v2.6M12 18.9v2.6M2.5 12h2.6M18.9 12h2.6M5.2 5.2l1.9 1.9M16.9 16.9l1.9 1.9M18.8 5.2l-1.9 1.9M7.1 16.9l-1.9 1.9"
                  stroke="currentColor" stroke-width="1.6" stroke-linecap="round"
                />
              </svg>
              <svg v-else viewBox="0 0 24 24" width="16" height="16" fill="none">
                <path
                  d="M20 13.2A8.2 8.2 0 0 1 10.8 4 8.4 8.4 0 1 0 20 13.2z"
                  fill="currentColor"
                />
              </svg>
            </div>
            <div class="auth-box">
              <template v-if="authStore.isAuthenticated">
                <span class="user-name">{{ authStore.user?.username }}</span>
                <a href="#" class="logout" @click.prevent="handleLogout">退出</a>
              </template>
              <RouterLink v-else to="/login" class="login-link">登录</RouterLink>
            </div>
          </div>
        </header>

        <main class="page-container">
          <RouterView />
        </main>

        <footer class="app-footer">info-harbor · 聚合全球多源 AI 动态</footer>
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
.app-header {
  position: sticky;
  top: 0;
  z-index: 100;
  background: var(--bg-card);
  border-bottom: 1px solid var(--border);
}
.header-inner {
  max-width: 1180px;
  margin: 0 auto;
  padding: 0 24px;
  height: 60px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 24px;
}
.brand {
  display: flex;
  align-items: center;
  gap: 10px;
  text-decoration: none;
  color: inherit;
  flex-shrink: 0;
}
.brand-mark {
  width: 32px;
  height: 32px;
  border-radius: 8px;
  background: linear-gradient(135deg, var(--brand), var(--brand-deep));
  color: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}
.brand-text {
  display: flex;
  flex-direction: column;
  line-height: 1.2;
}
.brand-name {
  font-size: 16px;
  font-weight: 700;
  color: var(--text-1);
}
.brand-sub {
  font-size: 11px;
  color: var(--text-3);
}
.nav {
  display: flex;
  align-items: center;
  gap: 4px;
}
.nav-link {
  padding: 7px 14px;
  border-radius: 8px;
  font-size: 14px;
  color: var(--text-2);
  text-decoration: none;
  transition: background 0.2s, color 0.2s;
}
.nav-link:hover {
  background: var(--bg-hover);
  color: var(--text-1);
}
.nav-link.active {
  background: var(--bg-active);
  color: var(--brand);
  font-weight: 600;
}
.theme-toggle {
  width: 32px;
  height: 32px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--text-2);
  cursor: pointer;
  transition: background 0.2s, color 0.2s;
  flex-shrink: 0;
}
.theme-toggle:hover {
  background: var(--bg-hover);
  color: var(--text-1);
}
.auth-box {
  display: flex;
  align-items: center;
  gap: 12px;
  font-size: 14px;
  flex-shrink: 0;
}
.user-name {
  color: var(--text-1);
  font-weight: 600;
}
.logout,
.login-link {
  color: var(--brand);
  text-decoration: none;
}
.logout {
  color: var(--danger);
}
.page-container {
  max-width: 1180px;
  margin: 0 auto;
  padding: 24px;
  width: 100%;
}
.app-footer {
  text-align: center;
  color: var(--text-faint);
  font-size: 12px;
  padding: 20px 0 28px;
}
</style>
