<template>
  <div class="app">
    <header class="app-header">
      <div class="container">
        <h1 class="app-title">Comments</h1>
      </div>
    </header>

    <main class="container">
      <CommentForm @submitted="onCommentSubmitted" />

      <div class="comments-header">
        <h2>Comments ({{ store.pagination.count }})</h2>
        <div class="sort-controls">
          <span>Sort by:</span>
          <button
            v-for="col in sortColumns"
            :key="col.field"
            class="sort-btn"
            :class="{ active: isSortActive(col.field) }"
            @click="store.setOrdering(col.field)"
          >
            {{ col.label }}
            <span class="sort-icon">{{ getSortIcon(col.field) }}</span>
          </button>
        </div>
      </div>

      <div v-if="store.loading" class="loading">
        <div class="spinner"></div>Loading...
      </div>

      <div v-else-if="store.error" class="error-message">
        {{ store.error }}
      </div>

      <TransitionGroup name="comment-list" tag="div" class="comments-list" v-else>
        <CommentCard
          v-for="comment in store.comments"
          :key="comment.id"
          :comment="comment"
          :depth="0"
          @reply="onReply"
        />
      </TransitionGroup>

      <Pagination
        v-if="store.totalPages > 1"
        :current="store.pagination.page"
        :total="store.totalPages"
        @change="store.fetchComments"
      />
    </main>

    <Lightbox />
  </div>
</template>

<script setup>
import { onMounted, onUnmounted, ref } from 'vue'
import { useCommentsStore } from './store/comments.js'
import CommentForm from './components/CommentForm.vue'
import CommentCard from './components/CommentCard.vue'
import Pagination from './components/Pagination.vue'
import Lightbox from './components/Lightbox.vue'

const store = useCommentsStore()

const sortColumns = [
  { field: 'username', label: 'Name' },
  { field: 'email', label: 'E-mail' },
  { field: 'created_at', label: 'Date' },
]

function isSortActive(field) {
  return store.ordering === field || store.ordering === `-${field}`
}

function getSortIcon(field) {
  if (store.ordering === field) return 'ASC'
  if (store.ordering === `-${field}`) return 'DESC'
  return 'SORT'
}

function onCommentSubmitted() {
  store.fetchComments(1)
}

function onReply(commentId) {
  document.querySelector('.comment-form')?.scrollIntoView({ behavior: 'smooth' })
}

onMounted(() => {
  store.fetchComments()
  store.connectWebSocket()
})

onUnmounted(() => {
  store.disconnectWebSocket()
})
</script>
