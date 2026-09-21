<script setup lang="ts">
import { onBeforeUnmount, onMounted, ref, watch, computed } from 'vue'

import type { Article } from '@/types/article'
import { timeAgo } from '@/utils/format'
import { useThemeStore } from '@/stores/theme'

const props = withDefaults(
  defineProps<{
    items: Article[]
    autoplay?: boolean
    interval?: number
  }>(),
  { autoplay: true, interval: 4000 },
)

const index = ref(0)
const paused = ref(false)

const len = () => props.items.length

function next() {
  if (len() === 0) return
  index.value = (index.value + 1) % len()
}
function prev() {
  if (len() === 0) return
  index.value = (index.value - 1 + len()) % len()
}

let timer: ReturnType<typeof setInterval> | null = null
function start() {
  if (!props.autoplay || len() < 2) return
  stop()
  timer = setInterval(next, props.interval)
}
function stop() {
  if (timer) clearInterval(timer)
  timer = null
}

onMounted(start)
onBeforeUnmount(stop)
watch(len, start)
watch(index, () => {
  if (paused.value) return
  start()
})

const themeStore = useThemeStore()

/** 每张卡不同配色轮换，避免无封面时的单调感。2/3 号保留原系列，1/4/5 号换奶油低饱和高级感配色。 */
const GRADS_LIGHT = [
  'linear-gradient(135deg, #d8c7b8, #b5a18c)',
  'linear-gradient(135deg, #0ea5e9, #22c55e)',
  'linear-gradient(135deg, #f59e0b, #ef4444)',
  'linear-gradient(135deg, #c7d6c3, #8fa898)',
  'linear-gradient(135deg, #cdb8c9, #a08aa0)',
]
/** 深色模式下原浅色渐变过亮扎眼，换低饱和深色版。 */
const GRADS_DARK = [
  'linear-gradient(135deg, #4a4137, #373029)',
  'linear-gradient(135deg, #0c5d7a, #19684a)',
  'linear-gradient(135deg, #95542a, #72291f)',
  'linear-gradient(135deg, #3e463d, #2d3731)',
  'linear-gradient(135deg, #44383f, #332a31)',
]
const GRADS = computed(() => (themeStore.isDark ? GRADS_DARK : GRADS_LIGHT))
</script>

<template>
  <div class="carousel" @mouseenter="paused = true; stop()" @mouseleave="paused = false; start()">
    <div class="stage">
      <a
        v-for="(item, i) in items"
        :key="item.id"
        :href="`/read/${item.id}`"
        target="_blank"
        rel="noopener"
        class="slide"
        :class="{ active: i === index }"
        :style="{ background: GRADS[i % GRADS.length] }"
      >
        <span class="slide-badge">{{ item.country ?? item.source_id }}</span>
        <h3 class="slide-title">{{ item.title }}</h3>
        <p class="slide-summary">{{ item.summary }}</p>
        <span class="slide-time">{{ timeAgo(item.published_at) }}</span>
      </a>
    </div>

    <button
      v-if="items.length > 1"
      class="nav-btn prev"
      type="button"
      title="上一张"
      @click="prev"
    >
      <svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="m15 18-6-6 6-6" /></svg>
    </button>
    <button
      v-if="items.length > 1"
      class="nav-btn next"
      type="button"
      title="下一张"
      @click="next"
    >
      <svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="m9 18 6-6-6-6" /></svg>
    </button>

    <div v-if="items.length > 1" class="dots">
      <button
        v-for="(_, i) in items"
        :key="i"
        class="dot"
        :class="{ active: i === index }"
        type="button"
        :title="`第 ${i + 1} 张`"
        @click="index = i"
      />
    </div>
  </div>
</template>

<style scoped>
.carousel {
  position: relative;
  --h: 190px;
}
.stage {
  position: relative;
  height: var(--h);
  overflow: hidden;
  border-radius: 14px;
}
.slide {
  position: absolute;
  inset: 0;
  border-radius: 14px;
  color: #fff;
  padding: 24px 28px;
  text-decoration: none;
  display: flex;
  flex-direction: column;
  justify-content: center;
  gap: 8px;
  box-shadow: 0 8px 24px var(--brand-shadow);
  opacity: 0;
  pointer-events: none;
  transition: opacity 0.9s ease;
  overflow: hidden;
}
.slide.active {
  opacity: 1;
  pointer-events: auto;
}
/* 装饰纹理：右上大圆 + 圆点阵 */
.slide::before {
  content: '';
  position: absolute;
  top: -70px;
  right: -50px;
  width: 220px;
  height: 220px;
  border-radius: 50%;
  background:
    radial-gradient(circle at 30% 30%, rgba(255, 255, 255, 0.28), rgba(255, 255, 255, 0) 60%),
    repeating-linear-gradient(
      45deg,
      rgba(255, 255, 255, 0.22) 0 2px,
      transparent 2px 12px
    );
  pointer-events: none;
}
/* 左下毛玻璃光圈 */
.slide::after {
  content: '';
  position: absolute;
  left: -40px;
  bottom: -70px;
  width: 200px;
  height: 200px;
  border-radius: 50%;
  background: radial-gradient(circle, rgba(255, 255, 255, 0.18), rgba(255, 255, 255, 0) 65%);
  pointer-events: none;
}
.slide-badge {
  position: relative;
  font-size: 12px;
  letter-spacing: 0.04em;
  opacity: 0.85;
}
.slide-title {
  position: relative;
  margin: 0;
  font-size: 19px;
  line-height: 1.45;
  font-weight: 700;
  max-width: 86%;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
.slide-summary {
  position: relative;
  margin: 0;
  font-size: 13px;
  line-height: 1.7;
  opacity: 0.9;
  max-width: 80%;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
.slide-time {
  position: relative;
  font-size: 12px;
  opacity: 0.75;
}

.nav-btn {
  position: absolute;
  top: 50%;
  transform: translateY(-50%);
  z-index: 20;
  width: 32px;
  height: 32px;
  border-radius: 50%;
  border: none;
  background: rgba(0, 0, 0, 0.3);
  color: #fff;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: background 0.2s;
  opacity: 0;
}
.carousel:hover .nav-btn {
  opacity: 1;
}
.nav-btn:hover {
  background: rgba(0, 0, 0, 0.5);
}
.nav-btn.prev { left: 12px; }
.nav-btn.next { right: 12px; }

.dots {
  position: absolute;
  bottom: 10px;
  left: 0;
  right: 0;
  display: flex;
  justify-content: center;
  gap: 6px;
  z-index: 20;
}
.dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  border: none;
  padding: 0;
  background: rgba(255, 255, 255, 0.45);
  cursor: pointer;
  transition: width 0.25s, background 0.25s;
}
.dot.active {
  width: 20px;
  border-radius: 4px;
  background: #fff;
}
</style>
