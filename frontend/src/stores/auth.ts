import { defineStore } from 'pinia'

import http from '@/services/http'
import type {
  LoginPayload,
  RegisterPayload,
  TokenResponse,
  User,
} from '@/types/auth'

const TOKEN_KEY = 'harbor_token'

/** 认证状态（§6.6）：token 持久化到 localStorage，user 启动时经 /auth/me 回填。 */
export const useAuthStore = defineStore('auth', {
  state: () => ({
    token: null as string | null,
    user: null as User | null,
    loading: false,
  }),
  getters: {
    isAuthenticated: (state) => !!state.token,
  },
  actions: {
    /** 应用启动时调用：本地有 token 则回填状态并拉取用户信息。 */
    async init() {
      const token = localStorage.getItem(TOKEN_KEY)
      if (!token) return
      this.token = token
      try {
        await this.fetchMe()
      } catch {
        // token 失效（401）时 http 拦截器已清理，这里同步状态
        this.token = null
        this.user = null
      }
    },
    async login(payload: LoginPayload) {
      const res = await http.post<TokenResponse>('/auth/login', payload)
      this.token = res.data.access_token
      localStorage.setItem(TOKEN_KEY, this.token)
      await this.fetchMe()
    },
    async register(payload: RegisterPayload) {
      const res = await http.post<User>('/auth/register', payload)
      return res.data
    },
    async fetchMe() {
      const res = await http.get<User>('/auth/me')
      this.user = res.data
    },
    logout() {
      this.token = null
      this.user = null
      localStorage.removeItem(TOKEN_KEY)
    },
  },
})
