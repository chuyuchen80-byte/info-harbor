<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { NButton, NCard, NEmpty, NGrid, NGridItem, NSpin, NStatistic, NTag } from 'naive-ui'

import ArticleCard from '@/components/ArticleCard.vue'
import { heatColor } from '@/components/WorldHeat'
import { useArticleStore } from '@/stores/article'
import type { Article } from '@/types/article'
import { timeAgo } from '@/utils/format'

const router = useRouter()
const articleStore = useArticleStore()

const latest = ref<Article[]>([])
const loading = ref(true)

const todayCount = computed(() => countWithin(1))
const weekCount = computed(() => countWithin(7))

function countWithin(days: number): number {
  const since = Date.now() - days * 24 * 3600 * 1000
  return latest.value.filter((a) => {
    const t = a.published_at ? new Date(a.published_at).getTime() : 0
    return t >= since
  }).length
}

/** 国家维度聚合（来自来源概况，公开数据）。 */
const countryStats = computed(() => {
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
const maxCountryCount = computed(() => Math.max(...countryStats.value.map((c) => c.count), 1))

function goCountry(code: string) {
  void router.push({ path: '/countries', query: { c: code } })
}

onMounted(async () => {
  await Promise.all([articleStore.fetchOverview(), articleStore.fetchList()])
  latest.value = articleStore.articles
  loading.value = false
})
</script>

<template>
  <div class="dashboard">
    <NGrid :cols="4" :x-gap="16" :y-gap="16" responsive="screen">
      <NGridItem>
        <NCard class="metric-card">
          <NStatistic label="库内文章" :value="articleStore.total">
            <template #suffix> 篇</template>
          </NStatistic>
        </NCard>
      </NGridItem>
      <NGridItem>
        <NCard class="metric-card">
          <NStatistic label="本页今日发布" :value="todayCount">
            <template #suffix> 篇</template>
          </NStatistic>
        </NCard>
      </NGridItem>
      <NGridItem>
        <NCard class="metric-card">
          <NStatistic label="接入来源" :value="articleStore.overview.length">
            <template #suffix> 个</template>
          </NStatistic>
        </NCard>
      </NGridItem>
      <NGridItem>
        <NCard class="metric-card">
          <NStatistic label="本页近 7 天" :value="weekCount">
            <template #suffix> 篇</template>
          </NStatistic>
        </NCard>
      </NGridItem>
    </NGrid>

    <div class="row">
      <NCard title="最新动态" class="col-main">
        <template #header-extra>
          <NButton size="small" quaternary tag="a" href="/articles">查看全部</NButton>
        </template>
        <NSpin :show="loading">
          <NEmpty v-if="!loading && latest.length === 0" description="暂无数据——去管理页触发一次抓取" />
          <div v-else class="stream-list">
            <ArticleCard v-for="item in latest.slice(0, 12)" :key="item.id" :article="item" />
          </div>
        </NSpin>
      </NCard>

      <NCard title="国家/地区分布" class="col-side">
        <NEmpty v-if="countryStats.length === 0" description="暂无来源数据" />
        <div v-else class="heat-grid">
          <div
            v-for="c in countryStats"
            :key="c.code"
            class="heat-cell"
            :style="{ background: heatColor(c.count / maxCountryCount) }"
            @click="goCountry(c.code)"
          >
            <span class="heat-code">{{ c.code }}</span>
            <span class="heat-count">{{ c.count }} 篇</span>
            <span class="heat-hot">{{ c.sources }} 个来源</span>
          </div>
        </div>
      </NCard>
    </div>

    <div class="row">
      <NCard title="最近发布 TOP 8" class="col-main">
        <NEmpty v-if="latest.length === 0" description="暂无数据" />
        <div v-else class="top-list">
          <RouterLink
            v-for="(a, i) in latest.slice(0, 8)"
            :key="a.id"
            :to="`/articles/${a.id}`"
            class="top-item"
          >
            <span class="top-rank" :class="{ top: i < 3 }">{{ i + 1 }}</span>
            <span class="top-title">{{ a.title }}</span>
            <NTag size="small" :bordered="false" class="top-tag">{{ a.country ?? '—' }}</NTag>
            <span class="top-time">{{ timeAgo(a.published_at) }}</span>
          </RouterLink>
        </div>
      </NCard>

      <NCard title="精选速览" class="col-side">
        <NEmpty v-if="latest.length === 0" description="暂无数据" />
        <div v-else class="featured">
          <RouterLink
            v-for="a in latest.slice(0, 3)"
            :key="a.id"
            :to="`/articles/${a.id}`"
            class="featured-item"
          >
            <span class="featured-badge">NEW</span>
            <span class="featured-title">{{ a.title }}</span>
            <span class="featured-meta">
              {{ a.author ?? a.source_id }} · {{ timeAgo(a.published_at) }}
            </span>
          </RouterLink>
        </div>
      </NCard>
    </div>
  </div>
</template>

<style scoped>
.dashboard {
  display: flex;
  flex-direction: column;
  gap: 16px;
}
.metric-card :deep(.n-card__content) {
  padding: 20px;
}
.metric-card { border-radius: 12px; }
.row {
  display: grid;
  grid-template-columns: 1fr 340px;
  gap: 16px;
  align-items: start;
}
.row :deep(.n-card) { border-radius: 12px; }
.col-main { min-width: 0; }
.stream-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}
.heat-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 10px;
}
.heat-cell {
  border-radius: 10px;
  padding: 12px;
  cursor: pointer;
  display: flex;
  flex-direction: column;
  gap: 2px;
  transition: transform 0.15s, box-shadow 0.2s;
}
.heat-cell:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px var(--brand-shadow);
}
.heat-code {
  font-weight: 700;
  font-size: 16px;
  color: var(--text-1);
}
.heat-count { font-size: 12px; color: var(--text-2); }
.heat-hot { font-size: 11px; color: var(--text-3); }
.top-list {
  display: flex;
  flex-direction: column;
}
.top-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 9px 8px;
  border-radius: 8px;
  text-decoration: none;
  color: inherit;
  transition: background 0.2s;
}
.top-item:hover { background: var(--bg-hover); }
.top-rank {
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
.top-rank.top {
  background: var(--brand);
  color: var(--bg-card);
}
.top-title {
  flex: 1;
  font-size: 13px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.top-tag { flex-shrink: 0; }
.top-time {
  color: var(--text-3);
  font-size: 12px;
  flex-shrink: 0;
}
.featured {
  display: flex;
  flex-direction: column;
  gap: 12px;
}
.featured-item {
  display: block;
  text-decoration: none;
  color: inherit;
  border: 1px solid var(--border);
  border-radius: 10px;
  padding: 12px 14px;
  transition: border-color 0.2s, box-shadow 0.2s;
}
.featured-item:hover {
  border-color: var(--brand-soft-border);
  box-shadow: 0 4px 12px var(--brand-shadow);
}
.featured-badge {
  display: inline-block;
  background: linear-gradient(135deg, var(--brand), var(--brand-deep));
  color: var(--bg-card);
  font-size: 11px;
  font-weight: 700;
  padding: 2px 8px;
  border-radius: 4px;
  margin-bottom: 8px;
}
.featured-title {
  display: block;
  font-size: 14px;
  font-weight: 600;
  line-height: 1.5;
}
.featured-meta {
  display: block;
  margin-top: 6px;
  font-size: 12px;
  color: var(--text-3);
}
</style>
