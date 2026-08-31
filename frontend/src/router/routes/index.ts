import type { RouteRecordRaw } from 'vue-router'

import { adminRoutes } from './admin'
import { articleRoutes } from './articles'
import { authRoutes } from './auth'
import { countryRoutes } from './countries'
import { dashboardRoutes } from './dashboard'
import { searchRoutes } from './search'
import { sourceRoutes } from './sources'

// 页面路由配置文件化：新增页面 = 加一个路由文件 + 页面组件，不改主入口（§6.6）
export const routes: RouteRecordRaw[] = [
  ...authRoutes,
  ...dashboardRoutes,
  ...articleRoutes,
  ...countryRoutes,
  ...sourceRoutes,
  ...searchRoutes,
  ...adminRoutes,
]
