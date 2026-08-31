<script setup lang="ts">
import { onMounted } from 'vue'
import { RouterLink, RouterView, useRouter } from 'vue-router'
import { NConfigProvider, NMessageProvider, zhCN } from 'naive-ui'

import { useAuthStore } from '@/stores/auth'

const authStore = useAuthStore()
const router = useRouter()

onMounted(() => {
  authStore.init()
})

function handleLogout() {
  authStore.logout()
  router.push('/login')
}
</script>

<template>
  <NConfigProvider :locale="zhCN">
    <NMessageProvider>
      <div class="layout">
        <header class="layout-header">
          <RouterLink to="/" class="brand">info-harbor</RouterLink>
          <nav class="nav">
            <RouterLink to="/">总览</RouterLink>
            <RouterLink to="/articles">文章</RouterLink>
            <RouterLink to="/countries">国家/地区</RouterLink>
            <RouterLink to="/sources">来源</RouterLink>
            <RouterLink to="/search">搜索</RouterLink>
            <RouterLink v-if="authStore.isAuthenticated" to="/admin">管理</RouterLink>
          </nav>
          <div class="auth-actions">
            <template v-if="authStore.isAuthenticated">
              <span class="user-name">{{ authStore.user?.username }}</span>
              <a href="#" class="logout" @click.prevent="handleLogout">退出</a>
            </template>
            <RouterLink v-else to="/login" class="login-link">登录</RouterLink>
          </div>
        </header>
        <main class="layout-main">
          <RouterView />
        </main>
      </div>
    </NMessageProvider>
  </NConfigProvider>
</template>

<style>
/* 骨架阶段先用轻量样式，后续迁移设计系统 */
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}
body {
  font-family: system-ui, -apple-system, 'Segoe UI', sans-serif;
  background: #f5f6f8;
  color: #1f2329;
}
.layout {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}
.layout-header {
  display: flex;
  align-items: center;
  gap: 24px;
  padding: 0 24px;
  height: 56px;
  background: #fff;
  border-bottom: 1px solid #e5e6eb;
}
.brand {
  font-weight: 700;
  color: #165dff;
  text-decoration: none;
  font-size: 18px;
}
.nav {
  display: flex;
  gap: 16px;
}
.nav a {
  color: #4e5969;
  text-decoration: none;
  font-size: 14px;
}
.nav a.router-link-active {
  color: #165dff;
  font-weight: 600;
}
.auth-actions {
  margin-left: auto;
  display: flex;
  align-items: center;
  gap: 12px;
  font-size: 14px;
}
.user-name {
  color: #1f2329;
}
.logout,
.login-link {
  color: #165dff;
  text-decoration: none;
}
.logout {
  color: #f53f3f;
}
.layout-main {
  flex: 1;
  padding: 24px;
}
</style>
