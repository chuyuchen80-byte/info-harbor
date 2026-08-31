<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import {
  NButton,
  NForm,
  NFormItem,
  NInput,
  useMessage,
  type FormInst,
  type FormRules,
} from 'naive-ui'

import http from '@/services/http'
import { useAuthStore } from '@/stores/auth'
import type { CaptchaResponse } from '@/types/auth'

const authStore = useAuthStore()
const router = useRouter()
const route = useRoute()
const message = useMessage()

/** 登录 / 注册 双模式 */
const mode = ref<'login' | 'register'>('login')

const formRef = ref<FormInst | null>(null)
const form = ref({
  account: '',
  username: '',
  email: '',
  password: '',
  confirmPassword: '',
  captcha_code: '',
})
const captchaId = ref('')
const captchaImg = ref('')
const submitting = ref(false)

const rules: FormRules = {
  account: { required: true, message: '请输入用户名或邮箱', trigger: ['blur', 'input'] },
  username: { required: true, message: '请输入用户名', trigger: ['blur', 'input'] },
  email: {
    required: true,
    type: 'email',
    message: '请输入正确的邮箱',
    trigger: ['blur', 'input'],
  },
  password: { required: true, min: 6, message: '密码至少 6 位', trigger: ['blur', 'input'] },
  confirmPassword: {
    required: true,
    validator: (_rule, value) => {
      return value === form.value.password || new Error('两次输入的密码不一致')
    },
    trigger: ['blur', 'input'],
  },
  captcha_code: { required: true, message: '请输入验证码', trigger: ['blur', 'input'] },
}

/** 获取验证码（首次 / 切换模式 / 提交失败后刷新） */
async function loadCaptcha() {
  try {
    const res = await http.get<CaptchaResponse>('/auth/captcha')
    captchaId.value = res.data.captcha_id
    captchaImg.value = `data:image/png;base64,${res.data.image_base64}`
  } catch {
    captchaImg.value = ''
    message.error('验证码获取失败，请检查后端服务')
  }
}

function switchMode() {
  mode.value = mode.value === 'login' ? 'register' : 'login'
  loadCaptcha()
}

async function handleSubmit() {
  try {
    await formRef.value?.validate()
  } catch {
    return
  }

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

onMounted(loadCaptcha)
</script>

<template>
  <section class="auth-wrap">
    <div class="auth-card">
      <h1 class="auth-title">{{ mode === 'login' ? '登录' : '注册' }} · info-harbor</h1>
      <NForm ref="formRef" :model="form" :rules="rules" label-placement="top">
        <NFormItem v-if="mode === 'login'" label="用户名 / 邮箱" path="account">
          <NInput v-model:value="form.account" placeholder="用户名或邮箱" @keydown.enter="handleSubmit" />
        </NFormItem>

        <template v-else>
          <NFormItem label="用户名" path="username">
            <NInput v-model:value="form.username" placeholder="2-64 个字符" />
          </NFormItem>
          <NFormItem label="邮箱" path="email">
            <NInput v-model:value="form.email" placeholder="you@example.com" />
          </NFormItem>
        </template>

        <NFormItem label="密码" path="password">
          <NInput
            v-model:value="form.password"
            type="password"
            show-password-on="click"
            placeholder="至少 6 位"
            @keydown.enter="handleSubmit"
          />
        </NFormItem>

        <NFormItem v-if="mode === 'register'" label="确认密码" path="confirmPassword">
          <NInput
            v-model:value="form.confirmPassword"
            type="password"
            show-password-on="click"
            placeholder="再次输入密码"
            @keydown.enter="handleSubmit"
          />
        </NFormItem>

        <NFormItem label="验证码" path="captcha_code">
          <div class="captcha-row">
            <NInput
              v-model:value="form.captcha_code"
              placeholder="请输入图中字符"
              maxlength="6"
              @keydown.enter="handleSubmit"
            />
            <img
              v-if="captchaImg"
              :src="captchaImg"
              class="captcha-img"
              title="点击刷新验证码"
              alt="验证码"
              @click="loadCaptcha"
            />
          </div>
        </NFormItem>

        <NButton type="primary" block :loading="submitting" @click="handleSubmit">
          {{ mode === 'login' ? '登录' : '注册' }}
        </NButton>
      </NForm>

      <p class="auth-switch">
        {{ mode === 'login' ? '还没有账号？' : '已有账号？' }}
        <a href="#" @click.prevent="switchMode">{{ mode === 'login' ? '去注册' : '去登录' }}</a>
      </p>
    </div>
  </section>
</template>

<style scoped>
.auth-wrap {
  display: flex;
  justify-content: center;
  padding-top: 8vh;
}
.auth-card {
  width: 360px;
  padding: 28px 32px 20px;
  background: #fff;
  border: 1px solid #e5e6eb;
  border-radius: 8px;
}
.auth-title {
  margin-bottom: 20px;
  font-size: 20px;
  text-align: center;
}
.captcha-row {
  display: flex;
  gap: 10px;
  width: 100%;
  align-items: center;
}
.captcha-img {
  height: 34px;
  width: 92px;
  border: 1px solid #e5e6eb;
  border-radius: 4px;
  cursor: pointer;
  flex-shrink: 0;
}
.auth-switch {
  margin-top: 16px;
  font-size: 13px;
  color: #4e5969;
  text-align: center;
}
.auth-switch a {
  color: #165dff;
  text-decoration: none;
}
</style>
