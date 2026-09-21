/** Mock 数据源占位（M1 预览用）：infoq 走真实接口，其余为占位。 */
export interface MockSource {
  id: string
  name: string
  country: string
  type: string
  note: string
}

export const MOCK_SOURCES: MockSource[] = [
  { id: 'openai', name: 'OpenAI Blog', country: 'US', type: 'blog', note: 'OpenAI 官方 Blog 占位，等待适配器接入' },
  { id: 'google', name: 'Google AI Blog', country: 'US', type: 'blog', note: 'Google AI Blog 占位，等待适配器接入' },
  { id: 'eu', name: 'EU AI Act News', country: 'EU', type: 'news', note: '欧盟 AI 法案动态占位，等待适配器接入' },
  { id: 'jiqizhixin', name: '机器之心', country: 'CN', type: 'news', note: '机器之心占位，等待适配器接入' },
]