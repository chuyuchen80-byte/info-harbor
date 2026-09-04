<script setup lang="ts">
import { computed, onMounted } from 'vue'
import { NCard, NEmpty, NStatistic, NTag } from 'naive-ui'

import { useArticleStore } from '@/stores/article'
import { dateShort } from '@/utils/format'

const article = useArticleStore()

const enabledCount = computed(() => article.overview.filter((s) => s.enabled).length)
const totalArticles = computed(() =>
  article.overview.reduce((sum, s) => sum + s.article_count, 0),
)

const kindLabel: Record<string, string> = {
  media: '媒体',
  api: 'API',
  rss: 'RSS',
  arxiv: '学术',
  github: 'GitHub',
  hf: '模型社区',
  government: '政府',
  community: '社区',
  cn_media: '中文媒体',
}

onMounted(() => article.fetchOverview())
</script>

<template>
  <div class="source-page">
    <div class="stat-row">
      <NCard :bordered="false" class="stat-card">
        <NStatistic label="来源总数">
          <template #suffix> 个</template>
          {{ article.overview.length }}
        </NStatistic>
      </NCard>
      <NCard :bordered="false" class="stat-card">
        <NStatistic label="启用中" :value="enabledCount" />
      </NCard>
      <NCard :bordered="false" class="stat-card">
        <NStatistic label="停用" :value="article.overview.length - enabledCount" />
      </NCard>
      <NCard :bordered="false" class="stat-card">
        <NStatistic label="累计文章" :value="totalArticles">
          <template #suffix> 篇</template>
        </NStatistic>
      </NCard>
    </div>

    <NEmpty v-if="article.overview.length === 0" description="暂无来源（种子未加载？）" />
    <div v-else class="src-grid">
      <NCard v-for="s in article.overview" :key="s.id" :bordered="false" class="src-card">
        <div class="src-head">
          <span class="src-dot" :style="{ background: s.enabled ? '#22c55e' : 'var(--text-3)' }" />
          <span class="src-name">{{ s.name }}</span>
          <NTag size="small" :bordered="false" :type="s.enabled ? 'success' : 'default'">
            {{ s.enabled ? '运行中' : '已停用' }}
          </NTag>
        </div>
        <div class="src-sub">
          <NTag size="tiny" :bordered="false" type="default">{{ s.id }}</NTag>
          <NTag size="tiny" :bordered="false" type="info">{{ kindLabel[s.type] ?? s.type }}</NTag>
          <NTag v-if="s.country" size="tiny" :bordered="false" type="default">{{ s.country }}</NTag>
          <NTag size="tiny" :bordered="false" type="default">{{ s.adapter_key }}</NTag>
        </div>
        <div class="src-meta">
          <span class="meta-item"><b>{{ s.article_count }}</b> 文章</span>
          <span class="meta-item">最近发布 {{ dateShort(s.last_published_at) }}</span>
        </div>
      </NCard>
    </div>
  </div>
</template>

<style scoped>
.source-page { display: flex; flex-direction: column; gap: 16px; }
.stat-row {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 12px;
}
.stat-card { border-radius: 12px; }
.stat-card :deep(.n-card__content) { padding: 18px; }
.src-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 16px;
}
.src-card { border-radius: 12px; }
.src-head {
  display: flex;
  align-items: center;
  gap: 8px;
}
.src-dot {
  width: 9px;
  height: 9px;
  border-radius: 50%;
  flex-shrink: 0;
}
.src-name {
  flex: 1;
  font-weight: 600;
  font-size: 15px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.src-sub { display: flex; gap: 4px; margin-top: 12px; flex-wrap: wrap; }
.src-meta {
  display: flex;
  gap: 14px;
  flex-wrap: wrap;
  margin-top: 14px;
  font-size: 12px;
  color: var(--text-3);
}
.meta-item b { color: var(--text-1); font-weight: 600; }
</style>
