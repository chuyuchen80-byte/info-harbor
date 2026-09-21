<script setup lang="ts">
import { RouterLink, useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import ThemeDropdown from '@/components/ThemeDropdown.vue'

export interface NavItem {
  path: string
  label: string
  icon: string
}

defineProps<{ items: NavItem[] }>()

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()

function isActive(path: string): boolean {
  if (path === '/') return route.path === '/'
  return route.path.startsWith(path)
}

function logout() {
  authStore.logout()
  router.push('/login')
}
</script>

<template>
  <nav class="float-nav">
    <RouterLink
      v-for="item in items"
      :key="item.path"
      :to="item.path"
      class="float-link"
      :class="{ active: isActive(item.path) }"
    >
      <svg
        v-if="item.icon"
        class="float-icon"
        viewBox="0 0 24 24"
        width="17"
        height="17"
        fill="none"
        stroke="currentColor"
        stroke-width="2"
        stroke-linecap="round"
        stroke-linejoin="round"
      >
        <path v-for="(d, i) in item.icon.split('|')" :key="i" :d="d" />
      </svg>
      <span class="float-label">{{ item.label }}</span>
    </RouterLink>

    <span class="divider" />

    <ThemeDropdown />

    <template v-if="authStore.isAuthenticated">
      <span class="user-box">
        <span class="user-name">{{ authStore.user?.username }}</span>
        <a href="#" class="logout" @click.prevent="logout">退出</a>
      </span>
    </template>
    <RouterLink v-else to="/login" class="login-link">登录</RouterLink>
  </nav>
</template>

<style scoped>
.float-nav {
  position: sticky;
  top: 12px;
  z-index: 100;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 4px;
  width: max-content;
  max-width: 100%;
  margin: 0 auto 20px;
  padding: 8px 12px;
  background: var(--bg-card);
  border: 1px solid var(--border);
  border-radius: 999px;
  box-shadow: 0 8px 24px var(--brand-shadow);
  flex-wrap: wrap;
  box-sizing: border-box;
}
.divider {
  width: 1px;
  height: 18px;
  margin: 0 6px;
  background: var(--border-strong);
  flex-shrink: 0;
}
.float-link {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 7px 14px;
  border-radius: 999px;
  color: var(--text-2);
  text-decoration: none;
  font-size: 14px;
  white-space: nowrap;
  transition: background 0.2s, color 0.2s;
}
.float-link:hover {
  background: var(--bg-hover);
  color: var(--text-1);
}
.float-link.active {
  background: var(--bg-active);
  color: var(--brand);
  font-weight: 600;
}
.float-icon {
  flex-shrink: 0;
}
.user-box {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 0 6px 0 10px;
  font-size: 13px;
  white-space: nowrap;
}
.user-name {
  font-weight: 600;
  color: var(--text-1);
  max-width: 110px;
  overflow: hidden;
  text-overflow: ellipsis;
}
.logout {
  color: var(--danger-text);
  text-decoration: none;
}
.logout:hover {
  text-decoration: underline;
}
.login-link {
  color: var(--brand);
  text-decoration: none;
  font-size: 14px;
  padding: 7px 12px;
  border-radius: 999px;
  white-space: nowrap;
}
.login-link:hover {
  background: var(--bg-active);
}
</style>