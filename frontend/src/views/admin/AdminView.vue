<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { NTabs, NTabPane, useMessage } from 'naive-ui'

import { useAuthStore } from '@/stores/auth'
import CrawlerOverviewPane from './components/CrawlerOverviewPane.vue'
import SourceManagePane from './components/SourceManagePane.vue'
import TaskMonitorPane from './components/TaskMonitorPane.vue'

const router = useRouter()
const message = useMessage()
const authStore = useAuthStore()

const activeTab = ref('crawler')

onMounted(() => {
  // 页面级 RBAC 兜底（服务端才是权威：管理接口已 require_roles('admin')）
  if (authStore.user && authStore.user.role !== 'admin') {
    message.error('该页面仅管理员可见')
    router.replace('/')
  }
})
</script>

<template>
  <div class="admin-page">
    <div class="page-head">
      <h1 class="page-title">管理后台</h1>
      <span class="page-desc">数据源接入 · 抓取任务编排与监控（M1）</span>
    </div>
    <NTabs v-model:value="activeTab" type="line" animated>
      <NTabPane name="crawler" tab="爬虫管理">
        <CrawlerOverviewPane />
      </NTabPane>
      <NTabPane name="sources" tab="源管理">
        <SourceManagePane />
      </NTabPane>
      <NTabPane name="tasks" tab="任务监控">
        <TaskMonitorPane />
      </NTabPane>
      <NTabPane name="scoring" tab="评分调试">
        <div class="pane-placeholder">LLM 评分管道 V2 接入后开放（权重滑条 / 评分雷达）</div>
      </NTabPane>
      <NTabPane name="rules" tab="筛选规则">
        <div class="pane-placeholder">规则初筛 V2 接入后开放（关键词黑白名单 / 阈值配置）</div>
      </NTabPane>
    </NTabs>
  </div>
</template>

<style scoped>
.admin-page { display: flex; flex-direction: column; gap: 8px; }
.page-head { display: flex; align-items: baseline; gap: 12px; }
.page-title { font-size: 20px; font-weight: 700; color: var(--text-1); }
.page-desc { font-size: 13px; color: var(--text-2); }
.pane-placeholder {
  padding: 48px 0;
  text-align: center;
  color: var(--text-3);
  font-size: 13px;
}
</style>
