<script setup lang="ts">
// 聊天主组件：负责会话切换、消息恢复、发送消息和渲染消息列表

import { ref, watch, computed, nextTick } from 'vue'
import { v4 as uuidv4 } from 'uuid'
import type { Message } from '~/types/chat.types'
import { useLayoutStore } from '~/stores/layout'


const props = defineProps<{
  // 当前路由传入的会话 ID；为空时表示新会话
  threadId?: string
}>()

const layoutStore = useLayoutStore()
const router = useRouter()

// 输入框内容，传给 MessageInput 组件
const input = ref('')
// 当前会话的消息列表
const messages = ref<Message[]>([])
// 是否正在接收后端流式输出
const isStreaming = ref(false)
// 用于消息列表滚动到底部的锚点元素
const messagesEndRef = ref<HTMLElement | null>(null)

// 当前会话 ID，与 store 保持同步；空字符串表示当前没有会话
const currentThreadId = computed({
  get: () => layoutStore.currentThreadId || '',
  set: (val: string) => layoutStore.setCurrentThreadId(val || null),
})

// 当前选中的 Agent，由布局顶部选择器控制
const agentId = computed(() => layoutStore.agentId)

// 路由参数变化时，同步当前会话到 store
watch(
  () => props.threadId,
  (threadId) => {
    if (threadId) {
      layoutStore.setCurrentThreadId(threadId)
    }
  },
  { immediate: true },
)

// 每次消息更新后都滚动到底部，保证最新内容可见
function scrollToBottom() {
  nextTick(() => {
    messagesEndRef.value?.scrollIntoView({ behavior: 'smooth' })
  })
}

watch(messages, scrollToBottom, { deep: true })

// 消息变化时持久化到 localStorage，刷新后仍可恢复当前会话
watch(
  messages,
  (val) => {
    if (val.length > 0 && currentThreadId.value) {
      localStorage.setItem(
        `chatMessages-${currentThreadId.value}`,
        JSON.stringify(val),
      )
    }
  },
  { deep: true },
)

// 清空当前聊天视图，用于新会话或切换到空状态
function handleNewChat() {
  messages.value = []
  input.value = ''
  isStreaming.value = false
}

// 切换会话时，从 localStorage 恢复对应消息；流式输出期间不打断当前状态
watch(
  () => layoutStore.currentThreadId,
  (threadId, oldThreadId) => {
    if (!threadId) {
      handleNewChat()
      return
    }
    if (threadId === oldThreadId) {
      return
    }
    if (isStreaming.value) {
      stopStream()
    }
    const storedMessages = localStorage.getItem(`chatMessages-${threadId}`)
    messages.value = storedMessages ? JSON.parse(storedMessages) : []
  },
  { immediate: true },
)

// 聊天发送能力由 composable 提供，组件只负责传入当前状态
const { handleStream, stopStream } = useStreamChat({
  currentThreadId,
  agentId,
  messages,
  isStreaming,
})

/**
 * 发送消息的统一入口：
 * 1. 读取输入内容并清空输入框
 * 2. 如果是新会话，先生成 threadId 并写入会话列表
 * 3. 调用流式发送逻辑
 * 4. 新会话创建成功后，更新路由到对应 threadId
 */
async function handleSend() {
  const messageText = input.value
  input.value = ''

  let threadId = currentThreadId.value
  const isNewThread = !threadId
  if (!threadId) {
    threadId = uuidv4()
    layoutStore.addSession(threadId, messageText)
  }

  await handleStream(messageText)

  if (isNewThread) {
    await router.replace(`/chat/${threadId}`)
  }
}
</script>

<template>
  <div class="h-full">
    <!-- 消息展示区：空状态时显示欢迎文案，否则逐条渲染消息 -->
    <div class="chat-messages overflow-y-auto p-4 h-[calc(100vh-280px)]">
      <div
        v-if="messages.length === 0"
        class="flex flex-col justify-center items-center min-h-full text-gray-600 space-y-2"
      >
        <div class="text-2xl font-medium">欢迎使用 AI ChatKit</div>
        <div class="text-base">
          你现在可以开始输入你的问题，我会在这里帮助你！
        </div>
      </div>
      <MessageBubble
        v-for="msg in messages"
        :key="msg.id"
        :message="msg"
        :is-streaming="isStreaming"
      />
      <div ref="messagesEndRef" />
    </div>
    <!-- 输入区：负责接收用户输入并触发发送 -->
    <MessageInput
      v-model:input="input"
      :is-streaming="isStreaming"
      @send="handleSend"
    />
  </div>
</template>
