<template>
  <div class="app">
    <header class="app-header">
      <div class="page-container header-inner">
        <div>
          <p class="eyebrow">SPA application</p>
          <h1 class="app-title">Comments</h1>
        </div>
        <span class="comments-total">{{ store.pagination.count }} total</span>
      </div>
    </header>

    <main class="page-container main-layout">
      <section class="form-section top-form-section">
        <CommentForm @submitted="onCommentSubmitted" />
      </section>

      <section class="comments-panel">
        <div class="comments-toolbar">
          <h2>Discussion</h2>
          <div class="sort-controls">
            <span>Sort by</span>
            <button
              v-for="col in sortColumns"
              :key="col.field"
              class="sort-btn"
              :class="{ active: isSortActive(col.field) }"
              @click="store.setOrdering(col.field)"
            >
              {{ col.label }}
              <span>{{ getSortIcon(col.field) }}</span>
            </button>
          </div>
        </div>

        <div v-if="store.loading" class="loading">
          <div class="spinner"></div>
          <span>Loading comments...</span>
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
          />
        </TransitionGroup>

        <Pagination
          v-if="store.totalPages > 1"
          :current="store.pagination.page"
          :total="store.totalPages"
          @change="store.fetchComments"
        />
      </section>
    </main>

    <Lightbox />
  </div>
</template>

<script setup>
import { onMounted, onUnmounted } from 'vue'
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
  if (store.ordering === field) return 'up'
  if (store.ordering === `-${field}`) return 'down'
  return 'sort'
}

function onCommentSubmitted() {
  store.fetchComments(1)
}

onMounted(() => {
  store.fetchComments()
  store.connectWebSocket()
})

onUnmounted(() => {
  store.disconnectWebSocket()
})
</script>
