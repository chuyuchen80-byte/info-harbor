import axios, { type AxiosInstance } from 'axios'

/** Axios 实例（§6.6）：拦截器工厂，token / 重试 / 去重 / SWR 缓存逐层扩展。 */
const http: AxiosInstance = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL ?? '/api/v1',
  timeout: 10_000,
})

http.interceptors.request.use((config) => {
  const token = localStorage.getItem('harbor_token')
  if (token) config.headers.Authorization = `Bearer ${token}`
  return config
})

http.interceptors.response.use(
  (res) => res,
  (err) => {
    // 401 → 凭证失效：清理本地 token 并回登录页（避免与 auth store 循环依赖，直接操作 localStorage）
    if (err.response?.status === 401) {
      localStorage.removeItem('harbor_token')
      if (window.location.pathname !== '/login') {
        window.location.href = '/login'
      }
    }
    // TODO: 网络错误 → 重试
    return Promise.reject(err)
  },
)

export default http
