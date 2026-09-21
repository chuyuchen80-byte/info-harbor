<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useMessage } from 'naive-ui'

import http from '@/services/http'
import { useArticleStore } from '@/stores/article'
import { useAuthStore } from '@/stores/auth'
import type { CaptchaResponse } from '@/types/auth'

const authStore = useAuthStore()
const articleStore = useArticleStore()
const router = useRouter()
const route = useRoute()
const message = useMessage()

/** 登录 / 注册 双模式 */
const mode = ref<'login' | 'register'>('login')

const form = ref({
  account: '',
  username: '',
  email: '',
  password: '',
  confirmPassword: '',
  captcha_code: '',
})
const errors = ref<Record<string, string>>({})
const captchaId = ref('')
const captchaImg = ref('')
const submitting = ref(false)
const showPassword = ref(false)

function validate(): boolean {
  const e: Record<string, string> = {}
  if (mode.value === 'login') {
    if (!form.value.account.trim()) e.account = '请输入用户名或邮箱'
    if (form.value.password.length < 6) e.password = '密码至少 6 位'
  } else {
    if (form.value.username.trim().length < 2) e.username = '用户名至少 2 个字符'
    if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(form.value.email)) e.email = '请输入正确的邮箱'
    if (form.value.password.length < 6) e.password = '密码至少 6 位'
    if (form.value.confirmPassword !== form.value.password) e.confirmPassword = '两次输入的密码不一致'
  }
  if (!form.value.captcha_code.trim()) e.captcha_code = '请输入验证码'
  errors.value = e
  return Object.keys(e).length === 0
}

/** 获取验证码（首次 / 切换模式 / 提交失败后刷新） */
async function loadCaptcha() {
  try {
    const res = await http.get<CaptchaResponse>('/auth/captcha')
    captchaId.value = res.data.captcha_id
    captchaImg.value = `data:image/png;base64,${res.data.image_base64}`
    errors.value.captcha_code = ''
  } catch {
    captchaImg.value = ''
    message.error('验证码获取失败，请检查后端服务')
  }
}

function switchMode() {
  mode.value = mode.value === 'login' ? 'register' : 'login'
  errors.value = {}
  loadCaptcha()
}

function onForgot() {
  message.info('忘记密码功能暂未开放，请联系管理员处理')
}

async function handleSubmit() {
  if (!validate()) return

  submitting.value = true
  try {
    if (mode.value === 'login') {
      await authStore.login({
        account: form.value.account,
        password: form.value.password,
        captcha_id: captchaId.value,
        captcha_code: form.value.captcha_code,
      })
      message.success('登录成功')
      const redirect = typeof route.query.redirect === 'string' ? route.query.redirect : '/'
      router.push(redirect)
    } else {
      await authStore.register({
        username: form.value.username,
        email: form.value.email,
        password: form.value.password,
        captcha_id: captchaId.value,
        captcha_code: form.value.captcha_code,
      })
      message.success('注册成功，请登录')
      mode.value = 'login'
      loadCaptcha()
    }
  } catch (e) {
    // 提交失败刷新验证码（登录/注册都依赖一次性验证码）
    loadCaptcha()
    const detail = (e as { response?: { data?: { detail?: string } } })?.response?.data?.detail
    message.error(detail ?? '操作失败，请重试')
  } finally {
    submitting.value = false
  }
}

/** 左栏数据亮点：来自公开来源概况接口，失败时 store 静默置空、徽标隐藏（不影响登录）。 */
const stats = computed(() => {
  const rows = articleStore.overview
  const articles = rows.reduce((n, s) => n + s.article_count, 0)
  const countries = new Set(rows.map((s) => s.country).filter((c): c is string => !!c)).size
  return { sources: rows.length, articles, countries }
})
const hasStats = computed(() => stats.value.sources > 0)

onMounted(() => {
  loadCaptcha()
  if (articleStore.overview.length === 0) void articleStore.fetchOverview()
})
</script>

<template>
  <div class="auth-split">
    <!-- 左：标语主视觉 + 真实数据统计卡 -->
    <aside class="brand-panel">
      <div class="brand-panel-bg" aria-hidden="true" />
      <div class="brand-content">
        <p class="brand-tagline">全球 AI 动态聚合，让前沿一目了然</p>
        <ul class="brand-points">
          <li>
            <span class="check">✓</span>
            <span>多源采集 · InfoQ 等全球渠道自动收录</span>
          </li>
          <li>
            <span class="check">✓</span>
            <span>AI 筛选 · LLM 评估，只留真正值得读的</span>
          </li>
          <li>
            <span class="check">✓</span>
            <span>地域视角 · 按国家 / 地区纵览世界 AI 进程</span>
          </li>
        </ul>
        <!-- 真实数据统计卡：后端可用时展示，否则整块隐藏 -->
        <div v-if="hasStats" class="brand-stats">
          <div class="stat-item">
            <span class="stat-num">{{ stats.sources }}</span>
            <span class="stat-label">接入来源</span>
          </div>
          <div class="stat-item">
            <span class="stat-num">{{ stats.articles }}</span>
            <span class="stat-label">库内文章</span>
          </div>
          <div class="stat-item">
            <span class="stat-num">{{ stats.countries }}</span>
            <span class="stat-label">覆盖国家</span>
          </div>
        </div>
      </div>
    </aside>

    <!-- 右：主题化表单卡片 -->
    <main class="form-panel">
      <form class="auth-form" novalidate @submit.prevent="handleSubmit">
        <h2 class="form-title">{{ mode === 'login' ? '欢迎回来' : '创建账号' }}</h2>
        <p class="form-sub">{{ mode === 'login' ? '登录后继续浏览全球 AI 动态' : '注册账号，开始你的 AI 资讯之旅' }}</p>

        <!-- 登录 / 注册 胶囊切换 -->
        <div class="mode-switch">
          <button
            type="button"
            class="mode-tab"
            :class="{ active: mode === 'login' }"
            @click="mode !== 'login' && switchMode()"
          >
            登录
          </button>
          <button
            type="button"
            class="mode-tab"
            :class="{ active: mode === 'register' }"
            @click="mode !== 'register' && switchMode()"
          >
            注册
          </button>
        </div>

        <!-- 登录字段 -->
        <template v-if="mode === 'login'">
          <div class="field">
            <div class="input-group" :class="{ invalid: errors.account }">
              <span class="input-icon">
                <svg viewBox="0 0 24 24" width="17" height="17" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="5" width="18" height="14" rx="3" /><path d="m3 7 9 6 9-6" /></svg>
              </span>
              <input
                v-model="form.account"
                class="input"
                type="text"
                placeholder="用户名或邮箱"
                autocomplete="username"
                @input="errors.account = ''"
              />
            </div>
            <p v-if="errors.account" class="field-error">{{ errors.account }}</p>
          </div>
          <div class="field">
            <div class="input-group" :class="{ invalid: errors.password }">
              <span class="input-icon">
                <svg viewBox="0 0 24 24" width="17" height="17" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="4" y="10" width="16" height="10" rx="2" /><path d="M8 10V7a4 4 0 0 1 8 0v3" /></svg>
              </span>
              <input
                v-model="form.password"
                class="input"
                :type="showPassword ? 'text' : 'password'"
                placeholder="密码"
                autocomplete="current-password"
                @input="errors.password = ''"
              />
              <button type="button" class="eye-btn" :title="showPassword ? '隐藏密码' : '显示密码'" @click="showPassword = !showPassword">
                <svg v-if="showPassword" viewBox="0 0 24 24" width="17" height="17" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M2 12s3.5-6 10-6 10 6 10 6-3.5 6-10 6-10-6-10-6z" /><circle cx="12" cy="12" r="2.5" /></svg>
                <svg v-else viewBox="0 0 24 24" width="17" height="17" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M3 3l18 18" /><path d="M10.6 5.1A9.8 9.8 0 0 1 12 5c6.5 0 10 7 10 7a17.9 17.9 0 0 1-3.1 3.9M6.6 6.6A17.9 17.9 0 0 0 2 12s3.5 7 10 7a9.7 9.7 0 0 0 4.3-1" /></svg>
              </button>
            </div>
            <p v-if="errors.password" class="field-error">{{ errors.password }}</p>
          </div>
        </template>

        <!-- 注册字段 -->
        <template v-else>
          <div class="field">
            <div class="input-group" :class="{ invalid: errors.username }">
              <span class="input-icon">
                <svg viewBox="0 0 24 24" width="17" height="17" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="8" r="4" /><path d="M4 21c0-4 3.6-6 8-6s8 2 8 6" /></svg>
              </span>
              <input
                v-model="form.username"
                class="input"
                type="text"
                placeholder="用户名"
                autocomplete="username"
                @input="errors.username = ''"
              />
            </div>
            <p v-if="errors.username" class="field-error">{{ errors.username }}</p>
          </div>
          <div class="field">
            <div class="input-group" :class="{ invalid: errors.email }">
              <span class="input-icon">
                <svg viewBox="0 0 24 24" width="17" height="17" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="5" width="18" height="14" rx="3" /><path d="m3 7 9 6 9-6" /></svg>
              </span>
              <input
                v-model="form.email"
                class="input"
                type="email"
                placeholder="邮箱"
                autocomplete="email"
                @input="errors.email = ''"
              />
            </div>
            <p v-if="errors.email" class="field-error">{{ errors.email }}</p>
          </div>
          <div class="field">
            <div class="input-group" :class="{ invalid: errors.password }">
              <span class="input-icon">
                <svg viewBox="0 0 24 24" width="17" height="17" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="4" y="10" width="16" height="10" rx="2" /><path d="M8 10V7a4 4 0 0 1 8 0v3" /></svg>
              </span>
              <input
                v-model="form.password"
                class="input"
                type="password"
                placeholder="密码（至少 6 位）"
                autocomplete="new-password"
                @input="errors.password = ''"
              />
            </div>
            <p v-if="errors.password" class="field-error">{{ errors.password }}</p>
          </div>
          <div class="field">
            <div class="input-group" :class="{ invalid: errors.confirmPassword }">
              <span class="input-icon">
                <svg viewBox="0 0 24 24" width="17" height="17" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="4" y="10" width="16" height="10" rx="2" /><path d="M8 10V7a4 4 0 0 1 8 0v3" /></svg>
              </span>
              <input
                v-model="form.confirmPassword"
                class="input"
                type="password"
                placeholder="确认密码"
                autocomplete="new-password"
                @input="errors.confirmPassword = ''"
              />
            </div>
            <p v-if="errors.confirmPassword" class="field-error">{{ errors.confirmPassword }}</p>
          </div>
        </template>

        <!-- 验证码：输入框 + 图片（放大显示，字符清晰可辨） -->
        <div class="field">
          <div class="captcha-row">
            <div class="input-group captcha-group" :class="{ invalid: errors.captcha_code }">
              <span class="input-icon">
                <svg viewBox="0 0 24 24" width="17" height="17" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 3l7 3v5c0 4.5-3 8-7 10-4-2-7-5.5-7-10V6z" /><path d="m9 12 2 2 4-4" /></svg>
              </span>
              <input
                v-model="form.captcha_code"
                class="input"
                type="text"
                placeholder="验证码"
                maxlength="6"
                autocomplete="off"
                @input="errors.captcha_code = ''"
              />
            </div>
            <img
              v-if="captchaImg"
              :src="captchaImg"
              class="captcha-img"
              title="点击刷新验证码"
              alt="验证码"
              @click="loadCaptcha"
            />
          </div>
          <p v-if="errors.captcha_code" class="field-error">{{ errors.captcha_code }}</p>
        </div>

        <!-- 记住我 / 忘记密码（仅登录模式） -->
        <div v-if="mode === 'login'" class="form-extra">
          <label class="remember">
            <input type="checkbox" />
            <span>记住我</span>
          </label>
          <a href="#" class="forgot" @click.prevent="onForgot">忘记密码？</a>
        </div>

        <button type="submit" class="submit-btn" :disabled="submitting">
          <span v-if="submitting" class="spinner" />
          {{ submitting ? '请稍候…' : mode === 'login' ? '登 录' : '注 册' }}
        </button>
      </form>
    </main>
  </div>
</template>

<style scoped>
/* ---- 分屏骨架：背景跟随主题变量，与全站一致 ---- */
.auth-split {
  display: grid;
  grid-template-columns: minmax(0, 1.06fr) minmax(0, 1fr);
  width: 100%;
  min-height: 100vh;
  background: var(--bg-page);
}

/* ---- 左：品牌区（标语主视觉 + 数据统计卡） ---- */
.brand-panel {
  position: relative;
  overflow: hidden;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 72px 64px;
  color: var(--text-1);
  background: transparent;
}
.brand-panel-bg {
  position: absolute;
  inset: 0;
  pointer-events: none;
  background:
    radial-gradient(560px 420px at 8% -10%, color-mix(in srgb, var(--brand) 7%, transparent), transparent 62%),
    radial-gradient(460px 360px at 108% 110%, color-mix(in srgb, var(--brand) 5%, transparent), transparent 60%);
}
.brand-content {
  position: relative;
  z-index: 1;
  max-width: 460px;
}
.brand-tagline {
  margin: 0;
  font-size: 28px;
  font-weight: 800;
  line-height: 1.5;
  letter-spacing: 0.01em;
  color: var(--text-1);
}

/* 卖点列表 */
.brand-points {
  margin: 24px 0 0;
  padding: 0;
  list-style: none;
  display: flex;
  flex-direction: column;
  gap: 14px;
}
.brand-points li {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  font-size: 14px;
  line-height: 1.7;
  color: var(--text-2);
}
.check {
  width: 22px;
  height: 22px;
  border-radius: 50%;
  background: var(--bg-active);
  color: var(--brand);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
  font-weight: 700;
  flex-shrink: 0;
  margin-top: 2px;
}

/* 真实数据统计卡：呼应首页统计卡语言 */
.brand-stats {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 12px;
  margin-top: 28px;
}
.stat-item {
  background: var(--bg-card);
  border: 1px solid var(--border);
  border-radius: 12px;
  padding: 16px 12px;
  text-align: center;
  box-shadow: 0 8px 20px var(--brand-shadow);
}
.stat-num {
  display: block;
  font-size: 24px;
  font-weight: 800;
  line-height: 1.2;
  color: var(--brand);
}
.stat-label {
  display: block;
  margin-top: 6px;
  font-size: 12.5px;
  color: var(--text-2);
}

/* ---- 右：主题化表单卡片 ---- */
.form-panel {
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 48px 64px;
}
.auth-form {
  position: relative;
  z-index: 1;
  width: 100%;
  max-width: 420px;
  background: var(--bg-card);
  border: 1px solid var(--border);
  border-radius: 16px;
  padding: 38px 34px 32px;
  box-shadow: 0 12px 32px var(--brand-shadow);
}
.form-title {
  margin: 0;
  font-size: 24px;
  font-weight: 700;
  color: var(--text-1);
}
.form-sub {
  margin: 8px 0 0;
  font-size: 13.5px;
  color: var(--text-2);
}

/* 登录 / 注册切换：激活态对齐悬浮导航 */
.mode-switch {
  display: flex;
  gap: 10px;
  margin: 26px 0 24px;
}
.mode-tab {
  flex: 1;
  padding: 11px 0;
  border: 1px solid var(--border-strong);
  border-radius: 10px;
  background: transparent;
  color: var(--text-2);
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: color 0.2s, border-color 0.2s, background 0.2s, box-shadow 0.2s;
}
.mode-tab:hover {
  color: var(--text-1);
  border-color: var(--text-3);
}
.mode-tab.active {
  border-color: transparent;
  background: var(--bg-active);
  color: var(--brand);
  box-shadow: 0 4px 12px var(--brand-shadow);
}

/* 输入框：图标 + 圆角浅底 */
.field {
  margin-bottom: 16px;
}
.input-group {
  display: flex;
  align-items: center;
  gap: 10px;
  height: 50px;
  padding: 0 14px;
  background: var(--bg-soft);
  border: 1.5px solid var(--border);
  border-radius: 10px;
  transition: border-color 0.2s, background 0.2s, box-shadow 0.2s;
}
.input-group:focus-within {
  background: var(--bg-card);
  border-color: var(--brand);
  box-shadow: 0 0 0 3px var(--brand-soft-border);
}
.input-group.invalid {
  border-color: var(--danger);
}
.input-icon {
  display: flex;
  color: var(--text-3);
  flex-shrink: 0;
}
.input {
  flex: 1;
  min-width: 0;
  border: none;
  outline: none;
  background: transparent;
  font-size: 14.5px;
  color: var(--text-1);
}
.input::placeholder {
  color: var(--text-faint);
}
.eye-btn {
  display: flex;
  padding: 4px;
  border: none;
  background: transparent;
  color: var(--text-3);
  cursor: pointer;
  flex-shrink: 0;
}
.eye-btn:hover {
  color: var(--text-2);
}

/* 验证码：输入框 + 大图 */
.captcha-row {
  display: flex;
  gap: 12px;
  align-items: stretch;
}
.captcha-group {
  flex: 1;
  min-width: 0;
}
.captcha-img {
  height: 50px;
  width: 148px;
  border: 1px solid var(--border);
  border-radius: 10px;
  background: var(--bg-card);
  cursor: pointer;
  flex-shrink: 0;
  transition: border-color 0.2s;
}
.captcha-img:hover {
  border-color: var(--brand);
}

.field-error {
  margin: 7px 0 0;
  font-size: 12.5px;
  color: var(--danger-text);
}

/* 记住我 / 忘记密码 */
.form-extra {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin: 4px 0 22px;
  font-size: 13.5px;
}
.remember {
  display: flex;
  align-items: center;
  gap: 7px;
  color: var(--text-2);
  cursor: pointer;
  user-select: none;
}
.remember input {
  width: 16px;
  height: 16px;
  accent-color: var(--brand);
  cursor: pointer;
}
.forgot {
  color: var(--brand);
  text-decoration: none;
  font-weight: 600;
}
.forgot:hover {
  text-decoration: underline;
}

/* 主按钮：品牌渐变，与主页 featured 徽标同款 */
.submit-btn {
  width: 100%;
  height: 52px;
  border: none;
  border-radius: 10px;
  background: linear-gradient(135deg, var(--brand), var(--brand-deep));
  /* 按钮文字固定白色：深色主题下 --bg-card 为深色，白字保证两种模式可读 */
  color: #fff;
  font-size: 15.5px;
  font-weight: 700;
  letter-spacing: 0.3em;
  text-indent: 0.3em;
  cursor: pointer;
  box-shadow: 0 12px 26px var(--brand-shadow);
  transition: transform 0.15s, box-shadow 0.2s, opacity 0.2s;
}
.submit-btn:hover:not(:disabled) {
  transform: translateY(-1px);
  box-shadow: 0 14px 30px var(--brand-shadow);
}
.submit-btn:disabled {
  opacity: 0.65;
  cursor: not-allowed;
}
.spinner {
  display: inline-block;
  width: 16px;
  height: 16px;
  margin-right: 8px;
  vertical-align: -2px;
  border: 2px solid color-mix(in srgb, var(--brand) 35%, transparent);
  border-top-color: var(--brand);
  border-radius: 50%;
  animation: spin 0.7s linear infinite;
}
@keyframes spin {
  to { transform: rotate(360deg); }
}

@media (max-width: 900px) {
  .auth-split {
    grid-template-columns: 1fr;
  }
  .brand-panel {
    display: none;
  }
  .form-panel {
    padding: 40px 20px;
  }
  .auth-form {
    padding: 32px 24px;
  }
}
</style>
