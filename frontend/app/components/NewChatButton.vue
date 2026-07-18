<script setup lang="ts">
// 新建聊天按钮：根据侧边栏折叠状态切换展示样式

import { h } from 'vue'
import { PlusOutlined } from '@ant-design/icons-vue'

defineProps<{
  // 控制按钮在侧边栏展开/折叠时的展示形态
  collapsed: boolean
}>()

// 点击按钮时通知父组件开始新聊天
const emit = defineEmits<{
  click: []
}>()
</script>

<template>
  <a-button
    type="primary"
    :icon="h(PlusOutlined)"
    :style="{ margin: '16px', width: collapsed ? '40px' : 'calc(100% - 32px)' }"
    :shape="collapsed ? 'circle' : 'round'"
    @click="emit('click')"
  >
    <!-- 侧边栏展开时显示完整文案，折叠时只保留图标 -->
    <template v-if="!collapsed">NEW CHAT</template>
  </a-button>
</template>
