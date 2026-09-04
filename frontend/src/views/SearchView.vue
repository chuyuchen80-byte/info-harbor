<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { NButton, NCard, NEmpty, NInput, NSelect, NTag } from 'naive-ui'

import { useArticleStore } from '@/stores/article'
import type { Article } from '@/types/article'
import { timeAgo } from '@/utils/format'

const article = useArticleStore()

const keyword = ref('')
const scope = ref<'title' | 'summary' | 'all'>('title')
const scopeOptions = [
  { label: '标题', value: 'title' },
  { label: '摘要', value: 'summary' },
  { label: '标题 + 摘要', value: 'all' },
]

const pool = ref<Article[]>([])
const searched = ref(false)
const searching = ref(false)

const results = computed(() => {
  const kw = keyword.value.trim().toLowerCase()
  if (!kw) return []
  return pool.value.filter((a) => {
    const title = (a.title ?? '').toLowerCase()
    const summary = (a.summary ?? '').toLowerCase()
    if (scope.value === 'title') return title.includes(kw)
    if (scope.value === 'summary') return summary.includes(kw)
    return title.includes(kw) || summary.includes(kw)
  })
})

/** 300ms 防抖搜索。 */
let timer: number | undefined
function onInput() {
  window.clearTimeout(timer)
  timer = window.setTimeout(() => doSearch(), 300)
}

async function doSearch() {
  searching.value = true
  searched.value = true
  await article.fetchList() // 刷新池（分页内检索，V3 换后端全文/语义检索）
  pool.value = article.articles
  searching.value = false
}

onMounted(async () => {
  await article.fetchList()
  pool.value = article.articles
})
</script>

<template>
  <div class="search-page">
    <NCard :bordered="false" class="search-card">
      <div class="search-row">
        <NInput
          v-model:value="keyword"
          size="large"
          round
          placeholder="搜索 AI 动态…（当前在最新一页内检索）"
          @input="onInput"
          @keyup.enter="doSearch"
        />
        <NSelect
          v-model:value="scope"
          :options="scopeOptions"
          style="width: 140px"
          @update:value="onInput"
        />
        <NButton size="large" type="primary" :loading="searching" @click="doSearch">搜索</NButton>
      </div>
    </NCard>

    <NCard :bordered="false" class="result-card">
      <template #header>
        <div class="result-head">
          <span class="result-title">检索结果</span>
          <NTag v-if="searched && keyword" size="small" :bordered="false" type="info">
            {{ results.length }} 条
          </NTag>
        </div>
      </template>

      <NEmpty
        v-if="!searched || !keyword.trim()"
        description="输入关键词开始检索；全文/语义检索将在 V3 上线"
      />
      <NEmpty v-else-if="results.length === 0" :description="`没有包含「${keyword}」的结果`" />
      <div v-else class="result-list">
        <RouterLink
          v-for="a in results"
          :key="a.id"
          :to="`/articles/${a.id}`"
          class="result-item"
        >
          <span class="result-title-text">{{ a.title }}</span>
          <span class="result-meta">{{ a.source_id }} · {{ timeAgo(a.published_at) }}</span>
        </RouterLink>
      </div>
    </NCard>
  </div>
</template>

<style scoped>
.search-page {
  display: flex;
  flex-direction: column;
  gap: 16px;
}
.search-card, .result-card { border-radius: 12px; }
.search-row {
  display: flex;
  gap: 12px;
}
.result-head {
  display: flex;
  align-items: center;
  gap: 10px;
}
.result-title { font-weight: 600; font-size: 15px; }
.result-list { display: flex; flex-direction: column; }
.result-item {
  display: flex;
  align-items: center;
  gap: 14px;
  padding: 10px 8px;
  border-radius: 8px;
  text-decoration: none;
  color: inherit;
  transition: background 0.2s;
}
.result-item:hover { background: var(--bg-hover); }
.result-title-text {
  flex: 1;
  font-size: 14px;
  color: var(--text-1);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.result-meta { font-size: 12px; color: var(--text-3); flex-shrink: 0; }
</style>
