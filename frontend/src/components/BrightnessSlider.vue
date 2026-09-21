<script setup lang="ts">
import { useThemeStore } from '@/stores/theme'

const theme = useThemeStore()
</script>

<template>
  <div class="brightness-slider" title="亮度">
    <svg viewBox="0 0 24 24" width="15" height="15" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" class="sun">
      <circle cx="12" cy="12" r="4" />
      <path d="M12 2v2M12 20v2M4.9 4.9l1.4 1.4M17.7 17.7l1.4 1.4M2 12h2M20 12h2M4.9 19.1l1.4-1.4M17.7 6.3l1.4-1.4" />
    </svg>
    <input
      type="range"
      min="0"
      max="100"
      :value="theme.brightness"
      @input="theme.setBrightness(Number(($event.target as HTMLInputElement).value))"
      aria-label="屏幕亮度"
    />
  </div>
</template>

<style scoped>
.brightness-slider {
  display: flex;
  align-items: center;
  gap: 8px;
  width: 100%;
  padding: 8px 10px;
  color: var(--text-2);
}
.sun {
  flex-shrink: 0;
}
input[type='range'] {
  flex: 1;
  min-width: 0;
  accent-color: var(--brand);
  cursor: pointer;
}
</style>
