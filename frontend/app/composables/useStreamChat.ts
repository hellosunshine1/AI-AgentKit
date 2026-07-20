// 【链路 ③】SSE 流式聊天：fetch 后端 /chat/stream，解析 token/message/end 事件

import type { Ref } from 'vue'
import { message } from 'ant-design-vue'
import type { Message, ToolCall } from '~/types/chat.types'

interface UseStreamChatOptions {
  currentThreadId: Ref<string>
  agentId: Ref<string>
  messages: Ref<Message[]>
  isStreaming: Ref<boolean>
}

export function useStreamChat({
  currentThreadId,
  agentId,
  messages,
  isStreaming,
}: UseStreamChatOptions) {
  const config = useRuntimeConfig() // 读取 nuxt.config 里的 apiBaseUrl（默认 http://localhost:8000）

  /**
   * 【链路回程】处理 SSE type=message 事件
   * - AI 带 tool_calls → 写入最后一条消息的 toolCall.calls（MessageBubble 折叠面板）
   * - tool 类型 → 把 DB 查询结果填到对应 tool call 的 result
   * - AI 带 content → 更新完整文本
   */
  function handleMessageData(content: {
    type: string
    content?: string
    tool_calls?: ToolCall[]
    tool_call_id?: string
  }) {
    if (content.type === 'ai' && content.tool_calls && content.tool_calls.length > 0) {
      const lastMsg = messages.value[messages.value.length - 1]
      const calls = lastMsg?.toolCall?.calls || []
      const toolCalls = content.tool_calls
      let addCalls: ToolCall[] = []

      if (calls.length === 0) {
        addCalls = toolCalls
      } else {
        for (const call of calls) {
          for (const toolCall of toolCalls) {
            if (call.id !== toolCall.id) {
              if (!addCalls.find((c) => c.id === toolCall.id)) {
                addCalls.push(toolCall)
              }
            }
          }
        }
      }

      messages.value = messages.value.map((msg, i) =>
        i === messages.value.length - 1
          ? {
              ...msg,
              toolCall: {
                ...msg.toolCall,
                calls: [...(msg.toolCall?.calls || []), ...addCalls],
              },
            }
          : msg,
      )
    } else if (content.type === 'ai' && content.content) {
      messages.value = messages.value.map((msg, i) =>
        i === messages.value.length - 1 ? { ...msg, content: content.content! } : msg,
      )
    }

    if (content.type === 'tool' && content.tool_call_id) {
      // 工具执行完毕（如 get_user_info 查完 database.db），结果写入 call.result
      messages.value = messages.value.map((msg, i) => {
        if (i !== messages.value.length - 1 || !msg.toolCall?.calls) return msg
        const updatedCalls = msg.toolCall.calls.map((call) =>
          call.id === content.tool_call_id
            ? { ...call, result: content.content }
            : call,
        )
        return { ...msg, toolCall: { ...msg.toolCall, calls: updatedCalls } }
      })
    }
  }

  /** 【链路回程】处理 SSE type=token → 打字机效果，追加到最后一条 AI 消息 */
  function handleTokenData(token: string) {
    messages.value = messages.value.map((msg, i) =>
      i === messages.value.length - 1 ? { ...msg, content: msg.content + token } : msg,
    )
  }

  /**
   * 【链路第 3 步】发起流式请求
   * fetch POST → ④ chat_routes.py /chat/stream → LangGraph Agent → DB
   */
  async function handleStream(input: string) {
    if (!input.trim() || isStreaming.value) return
    isStreaming.value = true

    // 先本地展示用户消息 + 空的 AI 占位（流式 token 往这里追加）
    messages.value.push(
      { id: `user_${Date.now()}`, type: 'user', content: input },
      { id: `ai_${Date.now()}`, type: 'ai', content: '' },
    )

    try {
      const requestMsg = {
        thread_id: currentThreadId.value, // 多轮对话上下文，后端 LangGraph checkpoint 使用
        role: 'user',
        message: input, // 如「查一下 jack 的信息」
        agent_id: agentId.value, // 如 oa-assistant → ⑤ agents.py
      }

      // 【关键 HTTP 请求】→ ④ backend/app/api/chat_routes.py
      const response = await fetch(`${config.public.apiBaseUrl}/chat/stream`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(requestMsg),
      })

      const reader = response.body?.getReader()
      const decoder = new TextDecoder()

      while (reader) {
        const { done, value } = await reader.read()
        if (done) break
        const dataChunk = decoder.decode(value, { stream: true })

        for (const line of dataChunk.split('\n')) {
          if (!line.startsWith('data: ')) continue
          const data = JSON.parse(line.replace('data: ', ''))
          switch (data.type) {
            case 'message':
              handleMessageData(data.content)
              break
            case 'token':
              handleTokenData(data.content)
              break
            case 'end':
              isStreaming.value = false
              reader.cancel()
              break
            case 'error':
              isStreaming.value = false
              console.error('Stream Error:', data.content||'服务发生错误，请稍后再试')
              reader.cancel()
              break
          }
        }
      }
    } catch (error) {
      console.error('Request Failed:', error)
      message.error('Request Failed, Please try again later.')
      isStreaming.value = false
    }
  }

  return { handleStream }
}
