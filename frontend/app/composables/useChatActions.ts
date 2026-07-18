import type { Ref } from 'vue'
import type { Message } from '~/types/chat.types'

interface UseChatActionsOptions {
  messages: Ref<Message[]>
  input: Ref<string>
  isStreaming: Ref<boolean>
}

export function useChatActions({ messages, input, isStreaming }: UseChatActionsOptions) {
  function handleNewChat() {
    messages.value = []
    input.value = ''
    if (isStreaming.value) {
      isStreaming.value = false
    }
  }

  return { handleNewChat }
}
