import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { api } from '../api/index.js'

export const useCommentsStore = defineStore('comments', () => {
  const comments = ref([])
  const loading = ref(false)
  const error = ref(null)
  const pagination = ref({ count: 0, next: null, previous: null, page: 1 })
  const ordering = ref('-created_at')

  let ws = null

  const totalPages = computed(() => Math.ceil(pagination.value.count / 25))

  async function fetchComments(page = 1) {
    loading.value = true
    error.value = null
    try {
      const data = await api.getComments({ page, ordering: ordering.value })
      comments.value = data.results
      pagination.value = {
        count: data.count,
        next: data.next,
        previous: data.previous,
        page,
      }
    } catch (e) {
      error.value = e.message
    } finally {
      loading.value = false
    }
  }

  async function createComment(formData) {
    const data = await api.createComment(formData)
    addComment(data)
    return data
  }

  async function previewComment(text) {
    return await api.previewComment(text)
  }

  function setOrdering(field) {
    if (ordering.value === field) {
      ordering.value = ordering.value.startsWith('-') ? field : `-${field}`
    } else {
      ordering.value = field
    }
    fetchComments(1)
  }

  function addComment(comment) {
    if (!comment) return

    if (!comment.parent) {
      const exists = comments.value.find((item) => item.id === comment.id)
      if (!exists && pagination.value.page === 1) {
        comments.value.unshift(comment)
        pagination.value.count += 1
      }
      return
    }

    if (insertReply(comments.value, comment)) {
      pagination.value.count += 1
    } else {
      fetchComments(pagination.value.page)
    }
  }

  function insertReply(items, reply) {
    for (const item of items) {
      if (item.id === reply.parent) {
        if (!Array.isArray(item.replies)) item.replies = []
        const exists = item.replies.find((child) => child.id === reply.id)
        if (!exists) {
          item.replies.unshift(reply)
          item.replies_count = (item.replies_count || 0) + 1
          return true
        }
        return false
      }

      if (item.replies?.length && insertReply(item.replies, reply)) {
        return true
      }
    }
    return false
  }

  function connectWebSocket() {
    if (ws) return

    const protocol = window.location.protocol === 'https:' ? 'wss' : 'ws'
    const host = import.meta.env.VITE_WS_URL || `${protocol}://${window.location.host}`
    ws = new WebSocket(`${host}/ws/comments/`)

    ws.onmessage = (event) => {
      const data = JSON.parse(event.data)
      if (data.type === 'new_comment' && data.comment) {
        addComment(data.comment)
      }
    }

    ws.onclose = () => {
      ws = null
      setTimeout(connectWebSocket, 3000)
    }
  }

  function disconnectWebSocket() {
    if (ws) {
      ws.close()
      ws = null
    }
  }

  return {
    comments,
    loading,
    error,
    pagination,
    ordering,
    totalPages,
    fetchComments,
    createComment,
    previewComment,
    setOrdering,
    connectWebSocket,
    disconnectWebSocket,
  }
})
