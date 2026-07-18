<script setup lang="ts">
import { computed } from 'vue'
import { useRoute } from 'vue-router'

const route = useRoute()
const threadId = computed(() => route.params.threadId as string)
</script>

<template>
  <Chat :thread-id="threadId" />
</template>