<script setup lang="ts">
import { RouterLink } from 'vue-router'
import { NTag } from 'naive-ui'

import type { Article } from '@/types/article'
import { timeAgo } from '@/utils/format'

defineProps<{
  article: Article
  highlight?: boolean
}>()

/** 来源 id → 展示名（M1 单源场景直接映射，多源后走 overview 数据）。 */
const sourceNames: Record<string, string> = {
  infoq: 'InfoQ 中文站',
}
</script>

<template>
  <RouterLink
    :to="`/articles/${article.id}`"
    class="article-card"
    :class="{ 'is-new': highlight }"
  >
    <div class="card-body">
      <div class="card-head">
        <span class="card-title">{{ article.title }}</span>
      </div>
      <p v-if="article.summary" class="card-summary">{{ article.summary }}</p>
      <div class="card-meta">
        <NTag v-if="article.country" size="small" :bordered="false" class="meta-tag">
          {{ article.country }}
        </NTag>
        <span class="meta-source">{{ sourceNames[article.source_id] ?? article.source_id }}</span>
        <span v-if="article.author" class="meta-author">{{ article.author }}</span>
        <span class="meta-time">{{ timeAgo(article.published_at) }}</span>
        <span v-if="article.status !== 'ready'" class="meta-status">{{ article.status }}</span>
      </div>
      <div v-if="article.tags.length" class="card-tags">
        <NTag v-for="tag in article.tags" :key="tag" size="small" type="info" :bordered="false">
          {{ tag }}
        </NTag>
      </div>
    </div>
  </RouterLink>
</template>

<style scoped>
.article-card {
  display: block;
  text-decoration: none;
  color: inherit;
  background: var(--bg-card);
  border: 1px solid var(--border);
  border-radius: 10px;
  padding: 14px 16px;
  transition: box-shadow 0.2s, border-color 0.2s;
}
.article-card:hover {
  box-shadow: 0 4px 16px var(--brand-shadow);
  border-color: var(--brand-soft-border);
}
.article-card.is-new {
  border-color: var(--brand);
  animation: newFlash 1.4s ease-out;
}
@keyframes newFlash {
  0% { background: var(--bg-active); }
  100% { background: var(--bg-card); }
}
.card-head {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  justify-content: space-between;
}
.card-title {
  font-size: 15px;
  font-weight: 600;
  line-height: 1.45;
  color: var(--text-1);
}
.card-summary {
  margin-top: 6px;
  color: var(--text-2);
  font-size: 13px;
  line-height: 1.6;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
.card-meta {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-top: 10px;
  font-size: 12px;
  color: var(--text-3);
}
.meta-tag { border-radius: 4px; }
.meta-source { color: var(--text-2); }
.meta-author { color: var(--text-2); }
.meta-status { color: var(--warn); }
.card-tags {
  display: flex;
  gap: 6px;
  margin-top: 8px;
  flex-wrap: wrap;
}
</style>
