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

  // 当前正在读取的流，用于切换会话时主动中断旧请求
  let currentReader: ReadableStreamDefaultReader<Uint8Array> | null = null

  function stopStream() {
    currentReader?.cancel()
    currentReader = null
    isStreaming.value = false
  }

  /**
   * 处理后端发来的 `message` 事件。
   *
   * 这里的 `content` 不是整条聊天记录，
   * 而是后端 SSE 推过来的一条“业务事件”。
   *
   * 可能出现三种情况：
   * 1. AI 要调用工具了，带着 `tool_calls`
   * 2. AI 直接返回了一段文字，带着 `content`
   * 3. 工具执行完了，带着 `tool_call_id` 和结果
   */
  function handleMessageData(content: {
    type: string
    content?: string
    tool_calls?: ToolCall[]
    tool_call_id?: string
  }) {
    // 情况 1：AI 说“我要调用工具”，并且把工具参数一起发过来了
    if (content.type === 'ai' && content.tool_calls && content.tool_calls.length > 0) {
      // 先拿到当前聊天列表里的最后一条消息
      // 因为这里我们默认：正在更新的就是那条空的 AI 占位消息
      const lastMsg = messages.value[messages.value.length - 1]

      // 取出最后一条消息里，已经存在的工具调用列表
      const calls = lastMsg?.toolCall?.calls || []

      // 后端这次新发来的工具调用列表
      const toolCalls = content.tool_calls

      // 先准备一个“要补进去的新工具调用”数组
      let addCalls: ToolCall[] = []

      // 如果之前一个工具都没有，那就直接全部加入
      // 如果之前已经有工具了，就尽量只加没重复的
      if (calls.length === 0) {
        addCalls = toolCalls
      } else {
        // 逐个比较旧的和新的工具调用，避免重复添加
        for (const call of calls) {
          for (const toolCall of toolCalls) {
            // id 不一样，说明可能是一个新的工具调用
            if (call.id !== toolCall.id) {
              // 再确认一下这个新 toolCall 之前没有加过
              if (!addCalls.find((c) => c.id === toolCall.id)) {
                addCalls.push(toolCall)
              }
            }
          }
        }
      }

      // 把这些工具调用写回“最后一条 AI 消息”里
      // 这样页面上就能展开显示工具调用面板
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
    // 情况 2：AI 没有工具调用，而是直接返回了一段文字
    } else if (content.type === 'ai' && content.content) {
      // 直接把最后一条 AI 消息的正文替换成新的内容
      messages.value = messages.value.map((msg, i) =>
        i === messages.value.length - 1 ? { ...msg, content: content.content! } : msg,
      )
    }

    // 情况 3：工具执行完了，后端把工具结果发回来了
    if (content.type === 'tool' && content.tool_call_id) {
      // 这里是给工具调用补“result”字段
      // 也就是：这个工具最后查到了什么结果
      messages.value = messages.value.map((msg, i) => {
        // 只更新最后一条消息，并且它必须真的有 toolCall
        if (i !== messages.value.length - 1 || !msg.toolCall?.calls) return msg

        // 找到对应的 tool_call_id，把结果挂到那个 call 上
        const updatedCalls = msg.toolCall.calls.map((call) =>
          call.id === content.tool_call_id
            ? { ...call, result: content.content }
            : call,
        )

        // 返回更新后的最后一条消息
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

      currentReader = response.body?.getReader() || null
      const reader = currentReader
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
              stopStream()
              break
            case 'error':
              stopStream()
              console.error('Stream Error:', data.content||'服务发生错误，请稍后再试')
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

  return { handleStream, stopStream }
}
