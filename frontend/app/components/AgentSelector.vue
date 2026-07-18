<script setup lang="ts">
// Agent 选择器：负责展示当前 Agent，并在切换时通知父组件
const props = defineProps<{
  value: string
}>()

// 当用户切换选项时，通过 change 事件把新值交给父组件
const emit = defineEmits<{
  change: [value: string]
}>()
</script>

<template>
  <!-- 切换当前聊天所使用的 Agent -->
  <a-select
    :value="props.value"
    class="ml-2 mr-5 w-36"
    @change="(val: string) => emit('change', val)"
  >
    <!-- OA 助手 -->
    <a-select-option value="oa-assistant">OA-ASSISTANT</a-select-option>
    <!-- 多 Agent 协作调度器 -->
    <a-select-option value="multi-agent-supervisor">MULTI-AGENT-SUPERVISOR</a-select-option>
  </a-select>
</template>
