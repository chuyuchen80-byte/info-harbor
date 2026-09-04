/** 国家分布色阶工具：热度比例 → 品牌蓝阶颜色（对齐原型）。 */

const STOPS = ['#e8f1ff', '#c7ddff', '#9cc2ff', '#5d97ff', '#165dff', '#0b3fb3']

/** ratio ∈ [0,1] → 颜色（0 为浅、1 为深）。 */
export function heatColor(ratio: number): string {
  const clamped = Math.max(0, Math.min(1, ratio))
  const idx = Math.round(clamped * (STOPS.length - 1))
  return STOPS[idx]
}
