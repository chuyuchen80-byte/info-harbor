<script setup lang="ts">
import { computed, onMounted } from 'vue'
import {
  NButton,
  NCard,
  NEmpty,
  NPagination,
  NSelect,
  NSkeleton,
  NSpin,
  NTag,
} from 'naive-ui'

import ArticleCard from '@/components/ArticleCard.vue'
import { useArticleStore } from '@/stores/article'

const article = useArticleStore()

const sortOptions = [
  { label: '发布时间', value: 'published_at' },
  { label: '入库时间', value: 'created_at' },
]

/** 筛选维度来自来源概况（国家/来源），公开数据无需登录。 */
const countryOptions = computed(() => {
  const codes = [...new Set(article.overview.map((s) => s.country).filter((c): c is string => !!c))]
  return codes.map((c) => ({ label: c, value: c }))
})
const sourceOptions = computed(() =>
  article.overview.map((s) => ({ label: s.name, value: s.id })),
)

onMounted(async () => {
  await article.fetchOverview()
  await article.fetchList()
})
</script>

<template>
  <div class="article-list-page">
    <NCard class="filter-card" :bordered="false">
      <div class="filter-row">
        <div class="filter-field">
          <span class="filter-label">国家/地区</span>
          <NSelect
            :value="article.filters.country"
            placeholder="全部"
            clearable
            :options="countryOptions"
            style="width: 140px"
            @update:value="article.setFilter('country', $event)"
          />
        </div>
        <div class="filter-field">
          <span class="filter-label">来源</span>
          <NSelect
            :value="article.filters.sourceId"
            placeholder="全部"
            clearable
            :options="sourceOptions"
            style="width: 180px"
            @update:value="article.setFilter('sourceId', $event)"
          />
        </div>
        <div class="filter-field">
          <span class="filter-label">排序</span>
          <NSelect
            :value="article.sort"
            :options="sortOptions"
            style="width: 130px"
            @update:value="article.setSort($event)"
          />
        </div>
        <NButton class="reset-btn" quaternary size="small" @click="article.resetFilters()">
          重置筛选
        </NButton>
      </div>
    </NCard>

    <NCard class="list-card" :bordered="false">
      <template #header>
        <div class="list-head">
          <span class="list-title">文章列表</span>
          <NTag v-if="article.total" size="small" :bordered="false" type="info">
            共 {{ article.total }} 篇
          </NTag>
        </div>
      </template>

      <NSpin :show="article.loading">
        <template v-if="article.loading">
          <div class="skeleton-list">
            <NSkeleton v-for="i in 6" :key="i" text :repeat="3" style="margin-bottom: 18px" />
          </div>
        </template>
        <template v-else>
          <NEmpty v-if="article.articles.length === 0" description="没有匹配的文章" />
          <div v-else class="card-list">
            <ArticleCard v-for="item in article.articles" :key="item.id" :article="item" />
          </div>
        </template>
      </NSpin>

      <div v-if="article.total > article.pageSize" class="pagination">
        <NPagination
          :page="article.page"
          :page-size="article.pageSize"
          :item-count="article.total"
          :on-update:page="article.setPage"
        />
      </div>
    </NCard>
  </div>
</template>

<style scoped>
.article-list-page {
  display: flex;
  flex-direction: column;
  gap: 16px;
}
.filter-card { border-radius: 12px; }
.filter-row {
  display: flex;
  align-items: center;
  gap: 18px;
  flex-wrap: wrap;
}
.filter-field {
  display: flex;
  align-items: center;
  gap: 8px;
}
.filter-label {
  font-size: 13px;
  color: var(--text-2);
  white-space: nowrap;
}
.reset-btn { margin-left: auto; }
.list-card { border-radius: 12px; }
.list-head {
  display: flex;
  align-items: center;
  gap: 10px;
}
.list-title { font-weight: 600; font-size: 15px; }
.card-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}
.skeleton-list { padding: 4px 0; }
.pagination {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
}
</style>
