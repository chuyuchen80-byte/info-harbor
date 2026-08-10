<script setup lang="ts">
import { onMounted } from 'vue'
import { storeToRefs } from 'pinia'

import { useArticleStore } from '@/stores/article'

const articleStore = useArticleStore()
const { articles, total, loading } = storeToRefs(articleStore)

onMounted(() => {
  articleStore.fetchArticles({ page: 1, pageSize: 20 })
})
</script>

<template>
  <section>
    <h1>文章列表</h1>
    <p class="muted">多维筛选（时间/国家/来源/评分/主题）+ 排序 + 虚拟滚动。骨架阶段返回空集。</p>
    <p v-if="loading" class="muted">加载中…</p>
    <p v-else-if="articles.length === 0" class="muted">暂无数据（total: {{ total }}）</p>
    <ul v-else>
      <li v-for="article in articles" :key="article.id">{{ article.title }}</li>
    </ul>
  </section>
</template>
