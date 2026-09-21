<script setup lang="ts">
import { onBeforeUnmount, ref, computed } from 'vue'
import BrightnessSlider from '@/components/BrightnessSlider.vue'
import { useThemeStore } from '@/stores/theme'
import { schemesForMode } from '@/config/themeSchemes'

const theme = useThemeStore()
const open = ref(false)
const panelRef = ref<HTMLElement | null>(null)

const lightSchemes = computed(() => schemesForMode('light'))
const darkSchemes = computed(() => schemesForMode('dark'))

function pick(key: string) {
  theme.setScheme(key)
  open.value = false
}

function onClickOutside(e: MouseEvent) {
  if (open.value && panelRef.value && !panelRef.value.contains(e.target as Node)) {
    open.value = false
  }
}
document.addEventListener('click', onClickOutside)
onBeforeUnmount(() => document.removeEventListener('click', onClickOutside))
</script>

<template>
  <div ref="panelRef" class="theme-dropdown">
    <button class="td-toggle" type="button" :title="'背景配色'" @click.stop="open = !open">
      <svg viewBox="0 0 24 24" width="17" height="17" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
        <circle cx="13.5" cy="6.5" r="1.5" />
        <circle cx="17.5" cy="10.5" r="1.5" />
        <circle cx="8.5" cy="7.5" r="1.5" />
        <circle cx="6.5" cy="12.5" r="1.5" />
        <path d="M12 2C6.5 2 2 6.5 2 12s4.5 10 10 10c.9 0 1.5-.7 1.5-1.5 0-.4-.15-.8-.4-1.1-.25-.3-.35-.7-.25-1.1.15-.6.7-1 1.3-1H17c2.8 0 5-2.2 5-5 0-5.5-4.5-9.3-10-9.3z" />
      </svg>
    </button>
    <transition name="td-pop">
      <div v-if="open" class="td-panel">
        <div class="td-group">
          <div class="td-group-label">浅色</div>
          <button
            v-for="s in lightSchemes"
            :key="s.key"
            type="button"
            class="td-item"
            :class="{ active: theme.scheme === s.key }"
            @click="pick(s.key)"
          >
            <span class="td-swatch" :style="{ background: (s.vars as Record<string,string>)['--bg-page'] }" />
            <span>{{ s.label }}</span>
            <span v-if="theme.scheme === s.key" class="td-check">✓</span>
          </button>
        </div>
        <div class="td-divider" />
        <div class="td-group">
          <div class="td-group-label">深色</div>
          <button
            v-for="s in darkSchemes"
            :key="s.key"
            type="button"
            class="td-item"
            :class="{ active: theme.scheme === s.key }"
            @click="pick(s.key)"
          >
            <span class="td-swatch" :style="{ background: (s.vars as Record<string,string>)['--bg-page'] }" />
            <span>{{ s.label }}</span>
            <span v-if="theme.scheme === s.key" class="td-check">✓</span>
          </button>
        </div>
        <div class="td-divider" />
        <div class="td-group-label">亮度</div>
        <BrightnessSlider />
      </div>
    </transition>
  </div>
</template>

<style scoped>
.theme-dropdown {
  position: relative;
  display: flex;
}
.td-toggle {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 34px;
  height: 34px;
  padding: 0;
  border: none;
  background: transparent;
  border-radius: 999px;
  color: var(--text-2);
  cursor: pointer;
  transition: background 0.2s, color 0.2s;
}
.td-toggle:hover {
  background: var(--bg-hover);
  color: var(--text-1);
}
.td-panel {
  position: absolute;
  top: calc(100% + 8px);
  right: 0;
  min-width: 190px;
  padding: 6px;
  background: var(--bg-card);
  border: 1px solid var(--border-strong);
  border-radius: 12px;
  box-shadow: 0 12px 32px var(--brand-shadow);
  z-index: 400;
}
.td-pop-enter-active,
.td-pop-leave-active {
  transition: opacity 0.15s ease, transform 0.15s ease;
}
.td-pop-enter-from,
.td-pop-leave-to {
  opacity: 0;
  transform: translateY(-4px);
}
.td-group-label {
  font-size: 11px;
  color: var(--text-faint);
  padding: 4px 8px 2px;
  letter-spacing: 0.08em;
}
.td-item {
  display: flex;
  align-items: center;
  gap: 8px;
  width: 100%;
  padding: 7px 8px;
  border: none;
  background: transparent;
  border-radius: 8px;
  font-size: 13px;
  color: var(--text-2);
  cursor: pointer;
  text-align: left;
  transition: background 0.15s, color 0.15s;
}
.td-item:hover {
  background: var(--bg-hover);
  color: var(--text-1);
}
.td-item.active {
  color: var(--brand);
  font-weight: 600;
}
.td-swatch {
  width: 16px;
  height: 16px;
  border-radius: 5px;
  border: 1px solid var(--border-strong);
  flex-shrink: 0;
}
.td-check {
  margin-left: auto;
  font-size: 12px;
}
.td-divider {
  height: 1px;
  margin: 4px 6px;
  background: var(--border);
}
</style>