/** 筛选器配置驱动（§6.6）：新增筛选维度只加配置项，筛选面板自动渲染。 */

export interface FilterOption {
  key: string
  label: string
  type: 'select' | 'date-range' | 'slider'
  options?: { label: string; value: string }[]
}

export const articleFilters: FilterOption[] = [
  { key: 'country', label: '国家/地区', type: 'select', options: [] },
  { key: 'source', label: '来源', type: 'select', options: [] },
  { key: 'time', label: '时间', type: 'date-range' },
  { key: 'minScore', label: '最低评分', type: 'slider' },
]
