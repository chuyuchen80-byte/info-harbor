import { defineStore } from 'pinia'

const KEY = 'harbor_theme'

function initial(): 'light' | 'dark' {
  const saved = localStorage.getItem(KEY)
  if (saved === 'light' || saved === 'dark') return saved
  return window.matchMedia?.('(prefers-color-scheme: dark)').matches ? 'dark' : 'light'
}

/** 主题状态（纯前端）：light/dark 切换 + localStorage 持久化 + <html> class 同步。 */
export const useThemeStore = defineStore('theme', {
  state: () => ({
    mode: initial(),
  }),
  getters: {
    isDark: (state) => state.mode === 'dark',
  },
  actions: {
    /** 应用启动时调用一次：把初始 mode 同步到 <html>。 */
    apply() {
      document.documentElement.classList.toggle('dark', this.isDark)
    },
    toggle() {
      this.mode = this.isDark ? 'light' : 'dark'
      localStorage.setItem(KEY, this.mode)
      this.apply()
    },
  },
})
