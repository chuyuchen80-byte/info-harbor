<script setup lang="ts">
import { nextTick, onBeforeUnmount, onMounted, ref, watch } from 'vue'

const props = defineProps<{ options: { key: string; label: string }[]; modelValue: string }>()
const emit = defineEmits<{ 'update:modelValue': [string] }>()

const activeKey = ref(props.modelValue)
watch(() => props.modelValue, (v) => { activeKey.value = v })

const barEl = ref<HTMLElement | null>(null)
const indicator = ref({ left: 0, width: 0 })

function slide() {
  const bar = barEl.value
  if (!bar) return
  const i = props.options.findIndex((o) => o.key === activeKey.value)
  const btn = bar.children[i] as HTMLElement | undefined
  if (btn) indicator.value = { left: btn.offsetLeft, width: btn.offsetWidth }
}

onMounted(async () => {
  slide()
  window.addEventListener('resize', slide)
})
onBeforeUnmount(() => window.removeEventListener('resize', slide))
watch(activeKey, () => nextTick(slide))
</script>

<template>
  <div class="slider-tabs" ref="barEl">
    <button
      v-for="o in options"
      :key="o.key"
      class="tab"
      :class="{ active: o.key === activeKey }"
      type="button"
      @click="emit('update:modelValue', o.key)"
    >
      {{ o.label }}
    </button>
    <span class="indicator" :style="{ left: indicator.left + 'px', width: indicator.width + 'px' }" />
  </div>
</template>

<style scoped>
.slider-tabs {
  position: relative;
  display: flex;
  gap: 28px;
  width: max-content;
  max-width: 100%;
  overflow-x: auto;
}
.tab {
  border: none;
  background: transparent;
  padding: 6px 0;
  font-family: ui-monospace, SFMono-Regular, Menlo, monospace;
  font-size: 13px;
  color: var(--text-3);
  cursor: pointer;
  transition: color 0.2s;
  white-space: nowrap;
}
.tab:hover { color: var(--text-2); }
.tab.active { color: var(--text-1); font-weight: 700; }
.indicator {
  position: absolute;
  bottom: 0;
  height: 2px;
  border-radius: 2px;
  background: var(--brand);
  transition: left 0.25s ease, width 0.25s ease;
}
</style>
