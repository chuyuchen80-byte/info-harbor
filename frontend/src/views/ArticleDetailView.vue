<script setup lang="ts">
import { useRoute } from 'vue-router'

const route = useRoute()
</script>

<template>
  <section>
    <h1>文章详情</h1>
    <p class="muted">文章 ID：{{ route.params.id }}。骨架占位：摘要、评分雷达图、实体、相关文章。</p>
  </section>
</template>
