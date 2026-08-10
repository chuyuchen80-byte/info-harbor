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
    // TODO: 401 → 刷新 token；网络错误 → 重试
    return Promise.reject(err)
  },
)

export default http
