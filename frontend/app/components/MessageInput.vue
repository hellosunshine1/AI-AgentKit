<script setup lang="ts">
// 聊天输入区：负责输入消息、处理快捷键并触发发送

import { h } from 'vue'
import { ArrowUpOutlined, StopOutlined } from '@ant-design/icons-vue'

// 与父组件双向绑定，表示当前输入框内容
const inputModel = defineModel<string>('input', { required: true })

// 由父组件传入，表示当前是否正在流式输出
defineProps<{
  isStreaming: boolean
}>()

// 向父组件发送“用户点击发送”的事件
const emit = defineEmits<{
  send: []
}>()

// Enter 直接发送；Mac 的 Command + Enter、Windows/Linux 的 Ctrl + Enter 留给换行逻辑
function onKeyPress(e: KeyboardEvent) {
  if (e.key === 'Enter' && !e.ctrlKey && !e.metaKey) {
    e.preventDefault()
    emit('send')
  }
}

// Ctrl + Enter / Command + Enter 手动插入换行
function onKeyDown(e: KeyboardEvent) {
  if (e.key === 'Enter' && (e.ctrlKey || e.metaKey)) {
    e.preventDefault()
    inputModel.value = `${inputModel.value}\n`
  }
}
</script>

<template>
  <div class="p-4 border-t">
    <div class="flex gap-2 items-center">
      <a-textarea
        v-model:value="inputModel"
        placeholder="给OA大模型发送消息"
        :disabled="isStreaming"
        class="flex-1 min-h-[80px] p-3 rounded-lg border border-gray-300 focus:border-blue-500 focus:ring-blue-500 transition-colors"
        :auto-size="{ minRows: 3, maxRows: 5 }"
        @keypress="onKeyPress"
        @keydown="onKeyDown"
      />
      <!-- 满足发送条件时可点击；流式输出中会被禁用 -->
      <a-button
        type="primary"
        class="bg-blue-500 hover:bg-blue-600 text-white h-24 px-6 rounded-lg transition-colors font-semibold shadow-md flex items-center justify-center"
        :disabled="!inputModel.trim() || isStreaming"
        :icon="h(isStreaming ? StopOutlined : ArrowUpOutlined)"
        @click="emit('send')"
      >
        <span class="sr-only">
          {{ isStreaming ? 'generating' : 'send' }}
        </span>
      </a-button>
    </div>
  </div>
</template>
