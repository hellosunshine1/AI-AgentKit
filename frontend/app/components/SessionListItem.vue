<script setup lang="ts">
// 会话列表项：展示会话名称，并提供删除入口

import { h } from 'vue'
import { EllipsisOutlined } from '@ant-design/icons-vue'
import type { Session } from '~/types/chat.types'

defineProps<{
  // 当前会话的基础信息
  session: Session
}>()

// 点击删除时通知父组件处理会话删除
const emit = defineEmits<{
  delete: [threadId: string]
}>()
</script>

<template>
  <div class="flex items-center gap-2 w-full min-w-0 flex-1 overflow-visible">
    <!-- 会话名称：过长时省略显示 -->
    <span class="flex-1 overflow-hidden text-clip whitespace-nowrap min-w-0">
      {{ session.name }}
    </span>
    <!-- 更多操作菜单：目前只提供删除会话 -->
    <a-dropdown :trigger="['click']" class="shrink-0 w-6 ml-2 flex-none">
      <template #overlay>
        <a-menu>
          <a-menu-item key="delete" @click="emit('delete', session.threadId)">
            DELETE
          </a-menu-item>
        </a-menu>
      </template>
      <a-button
        :icon="h(EllipsisOutlined)"
        shape="circle"
        size="small"
        :style="{ flexShrink: 0, backgroundColor: 'transparent', color: '#fff' }"
      />
    </a-dropdown>
  </div>
</template>
