<script setup lang="ts">
// 单条消息渲染：负责展示用户消息、AI 回复以及工具调用结果

import { computed } from 'vue'
import MarkdownIt from 'markdown-it'
import { UserOutlined, RobotOutlined } from '@ant-design/icons-vue'
import type { Message } from '~/types/chat.types'

const props = defineProps<{
  // 当前要渲染的消息
  message: Message
  // 用于判断是否需要显示流式加载状态
  isStreaming: boolean
}>()

const md = new MarkdownIt()
// AI 最终回复统一用 Markdown 渲染，便于展示富文本内容
const renderedContent = computed(() => md.render(props.message.content || ''))
</script>

<template>
  <div
    :class="[
      'mb-4',
      message.type === 'user' ? 'text-right flex justify-end' : 'text-left',
    ]"
  >
    <div
      :class="[
        'flex items-start gap-3 max-w-2xl',
        message.type === 'user' ? 'flex-row-reverse' : 'flex-row',
      ]"
    >
      <a-avatar
        :size="40"
        :class="message.type === 'user' ? 'bg-blue-500' : 'bg-gray-500'"
        class="text-white"
      >
        <template #icon>
          <UserOutlined v-if="message.type === 'user'" />
          <RobotOutlined v-else />
        </template>
      </a-avatar>
      <div
        :class="[
          'p-3 rounded-lg flex-1',
          message.type === 'user' ? 'bg-blue-50' : 'bg-gray-50',
        ]"
      >
        <!-- AI 正在流式输出且内容还为空时，先显示加载状态 -->
        <template v-if="message.type === 'ai' && isStreaming && message.content === ''">
          <div v-if="message.toolCall">
            <a-spin size="small" /> invoking tool...
          </div>
          <a-spin v-else size="small" />
        </template>
        <template v-else>
          <!-- 存在工具调用结果时，优先展示工具调用明细 -->
          <a-collapse
            v-if="message.toolCall?.calls?.length"
            :default-active-key="['0']"
            class="mt-2"
          >
            <a-collapse-panel
              v-for="(call, index) in message.toolCall.calls"
              :key="index"
              :header="`Tool ${index + 1}: ${call.name}`"
            >
              <p class="mb-2">input：{{ JSON.stringify(call.args) }}</p>
              <p v-if="call.result">result：{{ call.result }}</p>
            </a-collapse-panel>
          </a-collapse>
          <!-- 最终回复区域：用 Markdown 渲染 AI 整理后的内容 -->
          <div class="markdown-body" v-html="renderedContent" />
        </template>
      </div>
    </div>
  </div>
</template>
