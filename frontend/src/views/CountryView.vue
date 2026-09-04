<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { NCard, NEmpty, NSpin, NTag } from 'naive-ui'

import { heatColor } from '@/components/WorldHeat'
import { useArticleStore } from '@/stores/article'
import type { Article } from '@/types/article'
import { timeAgo } from '@/utils/format'

const route = useRoute()
const router = useRouter()
const articleStore = useArticleStore()

const countryArticles = ref<Article[]>([])
const loading = ref(false)

/** 国家列表：来源概况按国家聚合。 */
const countries = computed(() => {
  const map = new Map<string, { code: string; count: number; sources: number }>()
  for (const s of articleStore.overview) {
    const code = s.country ?? '—'
    const entry = map.get(code) ?? { code, count: 0, sources: 0 }
    entry.count += s.article_count
    entry.sources += 1
    map.set(code, entry)
  }
  return [...map.values()].sort((a, b) => b.count - a.count)
})

const selectedCode = computed(() => {
  const c = String(route.query.c ?? '')
  if (c && countries.value.some((x) => x.code === c)) return c
  return countries.value[0]?.code ?? null
})
const selected = computed(() => countries.value.find((c) => c.code === selectedCode.value) ?? null)
const maxCount = computed(() => Math.max(...countries.value.map((c) => c.count), 1))

/** 该国来源贡献条形。 */
const countrySources = computed(() =>
  articleStore.overview.filter((s) => (s.country ?? '—') === selectedCode.value),
)
const maxSourceCount = computed(() => Math.max(...countrySources.value.map((s) => s.article_count), 1))
const sourceBars = computed(() =>
  countrySources.value.map((s) => ({
    ...s,
    bar: (s.article_count / maxSourceCount.value) * 100,
  })),
)

async function loadCountry() {
  if (!selectedCode.value) return
  loading.value = true
  const res = await fetch(
    `/api/v1/articles?country=${encodeURIComponent(selectedCode.value)}&page=1&page_size=8`,
  )
  const data = await res.json()
  countryArticles.value = data.items ?? []
  loading.value = false
}

function selectCountry(code: string) {
  void router.replace({ query: { c: code } })
}

watch(selectedCode, loadCountry)

onMounted(async () => {
  await articleStore.fetchOverview()
  await loadCountry()
})
</script>

<template>
  <div class="country-page">
    <div class="country-grid">
      <NCard class="country-nav" :bordered="false">
        <template #header><span class="nav-title">国家/地区</span></template>
        <NEmpty v-if="countries.length === 0" description="暂无来源数据" />
        <div v-else class="nav-list">
          <div
            v-for="c in countries"
            :key="c.code"
            class="nav-item"
            :class="{ active: c.code === selectedCode }"
            @click="selectCountry(c.code)"
          >
            <span class="nav-dot" :style="{ background: heatColor(c.count / maxCount) }" />
            <span class="nav-code">{{ c.code }}</span>
            <span class="nav-count">{{ c.count }}</span>
          </div>
        </div>
      </NCard>

      <div class="col-main">
        <template v-if="selected">
          <NCard :bordered="false" class="head-card">
            <div class="head-main">
              <h2 class="country-title">
                {{ selected.code }}
                <span class="country-sub">共 {{ selected.count }} 篇</span>
              </h2>
              <NTag size="small" :bordered="false" type="info">{{ selected.sources }} 个来源</NTag>
            </div>
          </NCard>

          <div class="two-col">
            <NCard title="热点文章" :bordered="false" class="hot-card">
              <NSpin :show="loading">
                <NEmpty v-if="!loading && countryArticles.length === 0" description="暂无文章" />
                <div v-else class="hot-list">
                  <RouterLink
                    v-for="(a, i) in countryArticles.slice(0, 8)"
                    :key="a.id"
                    :to="`/articles/${a.id}`"
                    class="hot-item"
                  >
                    <span class="hot-rank" :class="{ top: i < 3 }">{{ i + 1 }}</span>
                    <span class="hot-title">{{ a.title }}</span>
                    <span class="hot-time">{{ timeAgo(a.published_at) }}</span>
                  </RouterLink>
                </div>
              </NSpin>
            </NCard>

            <NCard title="来源贡献" :bordered="false" class="source-card">
              <NEmpty v-if="sourceBars.length === 0" description="该国家暂无接入来源" />
              <div v-else class="source-bars">
                <div v-for="s in sourceBars" :key="s.id" class="sbar-row">
                  <span class="sbar-name">{{ s.name }}</span>
                  <div class="sbar-track">
                    <div
                      class="sbar-fill"
                      :style="{ width: `${Math.max(4, s.bar)}%`, background: 'var(--brand)' }"
                    />
                  </div>
                  <span class="sbar-count">{{ s.article_count }}</span>
                </div>
              </div>
            </NCard>
          </div>
        </template>
        <NEmpty v-else description="暂无国家数据" />
      </div>
    </div>
  </div>
</template>

<style scoped>
.country-page { display: flex; flex-direction: column; gap: 16px; }
.country-grid {
  display: grid;
  grid-template-columns: 220px 1fr;
  gap: 16px;
  align-items: start;
}
.country-nav { border-radius: 12px; }
.nav-title { font-weight: 600; }
.nav-list { display: flex; flex-direction: column; gap: 4px; }
.nav-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 9px 10px;
  border-radius: 8px;
  cursor: pointer;
  transition: background 0.2s;
}
.nav-item:hover { background: var(--bg-hover); }
.nav-item.active { background: var(--bg-active); }
.nav-dot {
  width: 10px;
  height: 10px;
  border-radius: 4px;
  flex-shrink: 0;
}
.nav-code { font-weight: 700; color: var(--text-1); flex: 1; }
.nav-count { color: var(--text-3); font-size: 12px; }
.col-main { display: flex; flex-direction: column; gap: 16px; min-width: 0; }
.head-card { border-radius: 12px; }
.head-main {
  display: flex;
  align-items: center;
  gap: 12px;
}
.country-title { margin: 0; font-size: 22px; }
.country-sub {
  font-size: 13px;
  font-weight: 400;
  color: var(--text-3);
  margin-left: 8px;
}
.two-col {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
}
.hot-card, .source-card { border-radius: 12px; }
.hot-list { display: flex; flex-direction: column; }
.hot-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 9px 8px;
  border-radius: 8px;
  text-decoration: none;
  color: inherit;
  transition: background 0.2s;
}
.hot-item:hover { background: var(--bg-hover); }
.hot-rank {
  width: 22px;
  height: 22px;
  border-radius: 6px;
  background: var(--bg-soft);
  color: var(--text-2);
  font-size: 12px;
  font-weight: 700;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}
.hot-rank.top { background: var(--brand); color: var(--bg-card); }
.hot-title {
  flex: 1;
  font-size: 13px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.hot-time { color: var(--text-3); font-size: 12px; flex-shrink: 0; }
.source-bars { display: flex; flex-direction: column; gap: 10px; }
.sbar-row { display: flex; align-items: center; gap: 8px; font-size: 12px; }
.sbar-name {
  width: 96px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  color: var(--text-2);
  flex-shrink: 0;
}
.sbar-track { flex: 1; height: 10px; background: var(--bg-soft); border-radius: 5px; overflow: hidden; }
.sbar-fill { height: 100%; border-radius: 5px; transition: width 0.4s; }
.sbar-count { width: 40px; text-align: right; color: var(--text-3); }
</style>
