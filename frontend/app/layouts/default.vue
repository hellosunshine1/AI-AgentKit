<script setup lang="ts">
// 应用主布局：负责加载会话、组织侧边栏和顶部 Agent 选择区

import { onMounted } from 'vue'
import { BarsOutlined } from '@ant-design/icons-vue'
import { useRouter } from 'vue-router'
import { useLayoutStore } from '~/stores/layout'

const layoutStore = useLayoutStore()
const router = useRouter()

// 页面首次进入时恢复本地会话列表
onMounted(() => {
  layoutStore.loadSessions()
})

// 删除会话后，自动跳转到剩余会话或聊天首页
function handleDeleteSession(threadId: string) {
  layoutStore.deleteSession(threadId)
  if (layoutStore.currentThreadId) {
    router.push(`/chat/${layoutStore.currentThreadId}`)
  } else {
    router.push('/chat')
  }
}

// 新建聊天时，先清空当前会话状态，再回到聊天首页
function handleNewChat() {
  layoutStore.startNewChat()
  router.push('/chat')
}

// 切换 Agent 后，新会话需要重新开始，避免和旧上下文混淆
function handleSelectAgent(value: string) {
  layoutStore.setAgentId(value)
  handleNewChat()
}

// 选中某个历史会话后，更新当前会话并跳转到对应路由
function handleSelectSession(key: string) {
  layoutStore.setCurrentThreadId(key)
  router.push(`/chat/${key}`)
}
</script>

<template>
  <a-layout style="min-height: auto">
    <Sidebar
      @new-chat="handleNewChat"
      @select-session="handleSelectSession"
      @delete-session="handleDeleteSession"
    />
    <a-layout>
      <a-layout-header class="flex flex-nowrap bg-white p-0">
        <BarsOutlined
          class="ml-4 cursor-pointer text-xl"
          @click="layoutStore.toggleCollapsed()"
        />
        <div class="ml-8 flex flex-none shrink-0 items-center">
          <span class="text-base">AI-Agent:</span>
          <AgentSelector :value="layoutStore.agentId" @change="handleSelectAgent" />
        </div>
      </a-layout-header>
      <a-layout-content class="m-4 min-h-[calc(100vh-120px)] bg-white p-6">
        <slot />
      </a-layout-content>
    </a-layout>
  </a-layout>
</template>