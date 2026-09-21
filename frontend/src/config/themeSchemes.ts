export interface ThemeScheme {
  key: string
  label: string
  vars: Record<string, string>
}

export const THEME_SCHEMES: ThemeScheme[] = [
  {
    key: 'harbor-light',
    label: '米白·暖',
    vars: {
      '--bg-page': '#faf6ef',
      '--bg-card': '#fffdf8',
      '--bg-hover': '#f3ecdd',
      '--bg-active': '#efe6d2',
      '--bg-soft': '#f5efe2',
      '--bg-stat': '#f9f4ea',
      '--border': '#ece3d2',
      '--border-strong': '#ddd0b8',
      '--text-1': '#26222a',
      '--text-2': '#5a5046',
      '--text-3': '#94897a',
      '--text-faint': '#b4a998',
      '--brand-shadow': 'rgba(151, 120, 66, 0.10)',
    },
  },
  {
    key: 'milk-light',
    label: '纯奶·亮',
    vars: {
      '--bg-page': '#ffffff',
      '--bg-card': '#ffffff',
      '--bg-hover': '#f5f5f4',
      '--bg-active': '#ececea',
      '--bg-soft': '#fafafa',
      '--bg-stat': '#f7f7f5',
      '--border': '#e5e5e0',
      '--border-strong': '#d4d4cc',
      '--text-1': '#1f1f1f',
      '--text-2': '#55554d',
      '--text-3': '#8f8f86',
      '--text-faint': '#b3b3a8',
      '--brand-shadow': 'rgba(0, 0, 0, 0.06)',
    },
  },
  {
    key: 'cream-light',
    label: '奶油·中',
    vars: {
      '--bg-page': '#f7f1e3',
      '--bg-card': '#fffdf8',
      '--bg-hover': '#f1e7d0',
      '--bg-active': '#eadfc3',
      '--bg-soft': '#f4ecda',
      '--bg-stat': '#faf5ea',
      '--border': '#ebdfc7',
      '--border-strong': '#d8c8a6',
      '--text-1': '#2b241a',
      '--text-2': '#67583f',
      '--text-3': '#a08d6a',
      '--text-faint': '#bead8d',
      '--brand-shadow': 'rgba(161, 130, 72, 0.12)',
    },
  },
  {
    key: 'latte-light',
    label: '拿铁·深',
    vars: {
      '--bg-page': '#f3ead8',
      '--bg-card': '#fbf6ea',
      '--bg-hover': '#ecdfc6',
      '--bg-active': '#e2d0ab',
      '--bg-soft': '#f2e9d5',
      '--bg-stat': '#f8f1e2',
      '--border': '#e7d8b8',
      '--border-strong': '#d2bd92',
      '--text-1': '#2f2516',
      '--text-2': '#6d5a3a',
      '--text-3': '#a99268',
      '--text-faint': '#c0ab85',
      '--brand-shadow': 'rgba(168, 133, 70, 0.14)',
    },
  },
  {
    key: 'coffee-dark',
    label: '咖啡·暖',
    vars: {
      '--bg-page': '#1c1a18',
      '--bg-card': '#2a2622',
      '--bg-hover': '#36312b',
      '--bg-active': '#3d352c',
      '--bg-soft': '#332e28',
      '--bg-stat': '#2c2824',
      '--border': '#3a332c',
      '--border-strong': '#4a4036',
      '--text-1': '#ece4d6',
      '--text-2': '#c0b3a1',
      '--text-3': '#8f8170',
      '--text-faint': '#6b6054',
      '--brand-shadow': 'rgba(0, 0, 0, 0.45)',
    },
  },
  {
    key: 'choco-dark',
    label: '巧克力·深',
    vars: {
      '--bg-page': '#241f1b',
      '--bg-card': '#332b24',
      '--bg-hover': '#40362c',
      '--bg-active': '#4a3d2f',
      '--bg-soft': '#3b3229',
      '--bg-stat': '#332c25',
      '--border': '#463a30',
      '--border-strong': '#594a3b',
      '--text-1': '#f0e6d3',
      '--text-2': '#cbbaa3',
      '--text-3': '#98876f',
      '--text-faint': '#726455',
      '--brand-shadow': 'rgba(0, 0, 0, 0.5)',
    },
  },
]

/** 按明暗筛出可用方案。 */
export function schemesForMode(mode: 'light' | 'dark'): ThemeScheme[] {
  return THEME_SCHEMES.filter((s) => s.key.endsWith(`-${mode}`))
}