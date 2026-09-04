import { createPinia } from 'pinia'
import { createApp } from 'vue'

import App from './App.vue'
import router from './router'
import { useThemeStore } from './stores/theme'
import './styles/theme.css'

const app = createApp(App)
app.use(createPinia())

// 挂载前应用主题，避免首屏闪白（naive-ui 侧由 NConfigProvider 响应 store）
useThemeStore().apply()

app.use(router).mount('#app')
