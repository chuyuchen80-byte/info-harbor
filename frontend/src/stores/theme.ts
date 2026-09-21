import { defineStore } from 'pinia'

import { THEME_SCHEMES, schemesForMode } from '@/config/themeSchemes'

const KEY = 'harbor_theme'
const SCHEME_KEY = 'harbor_scheme'
const BRIGHTNESS_KEY = 'harbor_brightness'

type Mode = 'light' | 'dark'

function initialMode(): Mode {
  const saved = localStorage.getItem(KEY)
  if (saved === 'light' || saved === 'dark') return saved
  return window.matchMedia?.('(prefers-color-scheme: dark)').matches ? 'dark' : 'light'
}

function initialBrightness(): number {
  const raw = localStorage.getItem(BRIGHTNESS_KEY)
  const saved = raw === null ? NaN : Number(raw)
  return Number.isFinite(saved) && saved >= 0 && saved <= 100 ? saved : 50
}

function initialScheme(mode: Mode): string {
  const saved = localStorage.getItem(SCHEME_KEY)
  if (THEME_SCHEMES.some((s) => s.key === saved)) return saved!
  // 默认取当前明暗的第一套，保证落地
  return schemesForMode(mode)[0]?.key ?? THEME_SCHEMES[0].key
}

/** 主题状态（纯前端）：明暗 + 配色方案，localStorage 持久化 + <html> class / inline 变量同步。 */
export const useThemeStore = defineStore('theme', {
  state: () => ({
    mode: initialMode(),
    scheme: '' as string,
    brightness: initialBrightness(),
  }),
  getters: {
    isDark: (state) => state.mode === 'dark',
    activeScheme(state) {
      return THEME_SCHEMES.find((s) => s.key === state.scheme) ?? null
    },
  },
  actions: {
    /** 应用启动时调用一次：把初始 mode / scheme / brightness 同步到 <html>。 */
    apply() {
      if (!this.scheme) this.scheme = initialScheme(this.mode)
      document.documentElement.classList.toggle('dark', this.isDark)
      this.applySchemeVars()
      this.applyBrightness()
    },
    applyBrightness() {
      document.documentElement.style.setProperty('--brightness', String(this.brightness / 100))
    },
    /** 设置亮度并持久化。 */
    setBrightness(n: number) {
      this.brightness = n
      localStorage.setItem(BRIGHTNESS_KEY, String(n))
      this.applyBrightness()
    },
    applySchemeVars() {
      const root = document.documentElement
      const vars = this.activeScheme?.vars ?? {}
      for (const [k, v] of Object.entries(vars)) root.style.setProperty(k, v)
    },
    /** 明暗切换：落到对应明暗的默认方案。 */
    toggle() {
      this.mode = this.isDark ? 'light' : 'dark'
      this.scheme = initialScheme(this.mode)
      localStorage.setItem(KEY, this.mode)
      localStorage.setItem(SCHEME_KEY, this.scheme)
      this.apply()
    },
    /** 选择具体配色方案（含明暗切换）。 */
    setScheme(key: string) {
      const scheme = THEME_SCHEMES.find((s) => s.key === key)
      if (!scheme) return
      this.mode = scheme.key.endsWith('-dark') ? 'dark' : 'light'
      this.scheme = scheme.key
      localStorage.setItem(KEY, this.mode)
      localStorage.setItem(SCHEME_KEY, this.scheme)
      this.apply()
    },
    /** 监听其他 tab 的主题变更（storage 事件只在其他 tab 触发）。 */
    initStorageSync() {
      window.addEventListener('storage', (e) => {
        if (e.key === KEY || e.key === SCHEME_KEY || e.key === BRIGHTNESS_KEY) {
          this.mode = initialMode()
          this.scheme = initialScheme(this.mode)
          this.brightness = initialBrightness()
          this.apply()
        }
      })
    },
  },
})
