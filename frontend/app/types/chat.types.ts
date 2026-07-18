// 工具调用结果：用于展示调用参数、名称和返回值
export interface ToolCall {
  id: string
  name: string
  args: Record<string, unknown>
  result?: string
}

// 聊天消息：包含用户消息、AI 消息以及工具调用消息
export interface Message {
  id: string
  type: 'user' | 'ai' | 'tool'
  content: string
  toolCall?: {
    calls: ToolCall[]
  }
}

// 会话元信息：用于侧边栏列表和当前会话切换
export interface Session {
  threadId: string
  name: string
  lastUpdated: number
}

