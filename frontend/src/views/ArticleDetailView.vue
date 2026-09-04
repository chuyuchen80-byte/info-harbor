<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { useRoute } from 'vue-router'
import { NButton, NCard, NEmpty, NSpin, NTag } from 'naive-ui'

import { useArticleStore } from '@/stores/article'
import type { Article } from '@/types/article'
import { dateTime } from '@/utils/format'

const route = useRoute()
const articleStore = useArticleStore()

const article = ref<Article | null>(null)
const loading = ref(true)

/** 正文分段：trafilatura 提取的纯文本按空行分段渲染。 */
function paragraphs(content: string | null | undefined): string[] {
  if (!content) return []
  return content
    .split(/\n\s*\n/)
    .map((p) => p.trim())
    .filter(Boolean)
}

onMounted(async () => {
  article.value = await articleStore.fetchDetail(String(route.params.id))
  loading.value = false
})
</script>

<template>
  <div class="detail-page">
    <NSpin :show="loading">
      <NEmpty
        v-if="!loading && !article"
        description="文章不存在或已被删除"
        class="empty-block"
      >
        <template #extra>
          <NButton size="small" tag="a" href="/articles">返回列表</NButton>
        </template>
      </NEmpty>

      <template v-if="article">
        <div class="detail-grid">
          <div class="col-main">
            <NCard :bordered="false" class="head-card">
              <h1 class="detail-title">{{ article.title }}</h1>
              <div class="detail-meta">
                <NTag v-if="article.country" size="small" :bordered="false">
                  {{ article.country }}
                </NTag>
                <span class="meta-item">{{ article.author ?? '佚名' }}</span>
                <span class="meta-item">{{ dateTime(article.published_at) }}</span>
                <span class="meta-item mono">#{{ article.id.slice(0, 8) }}</span>
              </div>
            </NCard>

            <NCard :bordered="false" class="body-card" title="正文">
              <div v-if="paragraphs(article.content).length" class="content">
                <p v-for="(p, i) in paragraphs(article.content)" :key="i" class="para">
                  {{ p }}
                </p>
              </div>
              <NEmpty v-else description="正文抓取失败（可等下轮抓取重试）" />
            </NCard>
          </div>

          <div class="col-side">
            <NCard :bordered="false" class="side-card" title="摘要">
              <p class="summary">{{ article.summary ?? '暂无摘要' }}</p>
            </NCard>

            <NCard :bordered="false" class="side-card" title="标签">
              <div v-if="article.tags.length" class="tag-list">
                <NTag v-for="tag in article.tags" :key="tag" size="small" type="info" :bordered="false">
                  {{ tag }}
                </NTag>
              </div>
              <span v-else class="muted">暂无</span>
            </NCard>

            <NCard :bordered="false" class="side-card" title="信息">
              <div class="info-list">
                <div class="info-row">
                  <span class="info-label">来源</span>
                  <span class="info-value">{{ article.source_id }}</span>
                </div>
                <div class="info-row">
                  <span class="info-label">语言</span>
                  <span class="info-value">{{ article.detected_lang ?? '—' }}</span>
                </div>
                <div class="info-row">
                  <span class="info-label">状态</span>
                  <span class="info-value">{{ article.status }}</span>
                </div>
                <div class="info-row">
                  <span class="info-label">原文</span>
                  <a :href="article.url" target="_blank" rel="noopener" class="info-link">
                    前往 InfoQ
                  </a>
                </div>
              </div>
            </NCard>
          </div>
        </div>
      </template>
    </NSpin>
  </div>
</template>

<style scoped>
.detail-page {
  min-height: 300px;
}
.empty-block { padding: 80px 0; }
.detail-grid {
  display: grid;
  grid-template-columns: 1fr 320px;
  gap: 16px;
  align-items: start;
}
.col-main { min-width: 0; display: flex; flex-direction: column; gap: 16px; }
.col-side { display: flex; flex-direction: column; gap: 16px; }
.head-card, .body-card, .side-card { border-radius: 12px; }
.detail-title {
  margin: 0;
  font-size: 22px;
  line-height: 1.5;
  color: var(--text-1);
}
.detail-meta {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-top: 12px;
  flex-wrap: wrap;
  font-size: 13px;
  color: var(--text-3);
}
.meta-item { color: var(--text-2); }
.mono { font-family: ui-monospace, SFMono-Regular, Menlo, monospace; font-size: 12px; }
.content {
  max-width: 760px;
}
.para {
  font-size: 15px;
  line-height: 1.9;
  color: var(--text-1);
  margin: 0 0 16px;
  text-indent: 0;
}
.summary {
  font-size: 13px;
  line-height: 1.8;
  color: var(--text-2);
  margin: 0;
}
.tag-list { display: flex; gap: 6px; flex-wrap: wrap; }
.muted { color: var(--text-3); font-size: 13px; }
.info-list { display: flex; flex-direction: column; gap: 10px; }
.info-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  font-size: 13px;
}
.info-label { color: var(--text-3); }
.info-value { color: var(--text-1); }
.info-link { color: var(--brand); text-decoration: none; }
.info-link:hover { text-decoration: underline; }
</style>
