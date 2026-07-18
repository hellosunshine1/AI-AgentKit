<script setup lang="ts">
import { computed } from 'vue'
import { useLayoutStore } from '~/stores/layout'

const layoutStore = useLayoutStore()

const emit = defineEmits<{
  'new-chat': []
  'select-session': [key: string]
  'delete-session': [threadId: string]
}>()

const reversedSessions = computed(() => [...layoutStore.sessions].reverse())
</script>

<template>
  <a-layout-sider
    :collapsed="layoutStore.collapsed"
    collapsible
    :width="200"
    @collapse="(val: boolean) => (layoutStore.collapsed = val)"
  >
    <div
      v-if="!layoutStore.collapsed"
      class="logo flex items-center justify-center h-16 text-white text-lg"
    >
      AI-CHATKIT
    </div>
    <NewChatButton
      :collapsed="layoutStore.collapsed"
      @click="emit('new-chat')"
    />
    <a-menu
      v-if="!layoutStore.collapsed"
      theme="dark"
      class="max-h-[calc(100vh-180px)] overflow-y-auto"
      mode="inline"
      :selected-keys="layoutStore.currentThreadId ? [layoutStore.currentThreadId] : []"
      @select="({ key }: { key: string }) => emit('select-session', key)"
    >
      <a-menu-item v-for="session in reversedSessions" :key="session.threadId">
        <SessionListItem
          :session="session"
          @delete="emit('delete-session', $event)"
        />
      </a-menu-item>
    </a-menu>
  </a-layout-sider>
</template>
