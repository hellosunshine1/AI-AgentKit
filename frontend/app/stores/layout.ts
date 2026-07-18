import { defineStore } from 'pinia'
import { v4 as uuidv4 } from 'uuid'
import type { Session } from '~/types/chat.types'

// 布局与会话状态：管理当前 Agent、会话列表和侧边栏折叠状态
export const useLayoutStore = defineStore('layout', {
  state: () => ({
    // 当前选中的 Agent，默认使用 oa-assistant
    agentId: 'oa-assistant',
    // 当前活跃会话的 threadId；为空表示尚未选择会话
    currentThreadId: null as string | null,
    // 会话列表，按创建顺序保存
    sessions: [] as Session[],
    // 侧边栏是否折叠
    collapsed: false,
  }),

  actions: {
    // 从 localStorage 恢复会话列表；解析失败时回退为空数组
    loadSessions() {
      try {
        this.sessions = JSON.parse(localStorage.getItem('chatSessions') || '[]')
      } catch {
        this.sessions = []
      }
    },

    // 将会话列表写回 localStorage，保证刷新后不丢失
    persistSessions() {
      localStorage.setItem('chatSessions', JSON.stringify(this.sessions))
    },

    // 切换当前 Agent；切换后通常需要重新开始新会话
    setAgentId(agentId: string) {
      this.agentId = agentId
    },

    // 设置当前活跃会话
    setCurrentThreadId(threadId: string | null) {
      this.currentThreadId = threadId
    },

    // 切换侧边栏折叠状态
    toggleCollapsed() {
      this.collapsed = !this.collapsed
    },

    // 新增会话并设为当前会话；首条消息会用于生成会话名称
    addSession(threadId: string, startMsg: string) {
      const id = threadId || uuidv4()
      const msg = startMsg || `greet ${new Date().toLocaleString()}`
      const newSession: Session = {
        threadId: id,
        name: msg.substring(0, 10),
        lastUpdated: Date.now(),
      }
      this.sessions = [...this.sessions, newSession]
      this.currentThreadId = id
      this.persistSessions()
      return id
    },

    // 删除指定会话及其消息缓存；若还有会话则自动切换到最后一个
    deleteSession(delThreadId: string) {
      this.sessions = this.sessions.filter((s) => s.threadId !== delThreadId)
      this.persistSessions()
      localStorage.removeItem(`chatMessages-${delThreadId}`)

      if (this.sessions.length > 0) {
        const lastSession = [...this.sessions].reverse()[0]
        this.currentThreadId = lastSession?.threadId || null
      } else {
        this.currentThreadId = null
      }
    },

    // 开始新聊天：仅清空当前会话标识，不直接清空历史会话列表
    startNewChat() {
      this.currentThreadId = null
    },
  },
})