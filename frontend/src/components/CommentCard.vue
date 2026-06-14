<template>
  <div class="comment-card" :class="{ 'is-reply': depth > 0 }" :style="{ '--depth': depth }">
    <div class="comment-header">
      <div class="comment-avatar">
        <img :src="avatarUrl" :alt="comment.username" />
      </div>
      <div class="comment-meta">
        <span class="comment-username">
          <a v-if="comment.homepage" :href="comment.homepage" target="_blank" rel="noopener noreferrer">
            {{ comment.username }}
          </a>
          <span v-else>{{ comment.username }}</span>
        </span>
        <span class="comment-date" :title="fullDate">{{ relativeDate }}</span>
        <span class="comment-email">{{ comment.email }}</span>
      </div>
    </div>

    <div class="comment-quote" v-if="depth > 0 && comment.parent">
      <blockquote>{{ quotedText }}</blockquote>
    </div>

    <div class="comment-body" v-html="comment.text"></div>

    <div class="comment-attachments" v-if="comment.image || comment.attachment">
      <div
        v-if="comment.image"
        class="attachment-image"
        @click="openLightbox(comment.image, 'image')"
      >
        <img :src="mediaUrl(comment.image)" :alt="'Image by ' + comment.username" />
        <div class="attachment-overlay">Open</div>
      </div>
      <div
        v-if="comment.attachment"
        class="attachment-file"
        @click="openLightbox(comment.attachment, 'file')"
      >
        <span class="file-icon"></span>
        <span class="file-label">{{ fileName(comment.attachment) }}</span>
      </div>
    </div>

    <div class="comment-actions">
      <button class="action-btn reply-btn" @click="toggleReplyForm">
        {{ showReplyForm ? 'Cancel' : 'Reply' }}
      </button>
      <span class="replies-count" v-if="comment.replies_count > 0">
        {{ comment.replies_count }}
      </span>
    </div>

    <Transition name="slide-down">
      <CommentForm
        v-if="showReplyForm"
        :parentId="comment.id"
        class="inline-reply-form"
        @submitted="onReplySubmitted"
        @cancel="showReplyForm = false"
      />
    </Transition>

    <div class="replies-container" v-if="comment.replies && comment.replies.length">
      <TransitionGroup name="comment-list">
        <CommentCard
          v-for="reply in comment.replies"
          :key="reply.id"
          :comment="reply"
          :depth="depth + 1"
          @reply="$emit('reply', $event)"
        />
      </TransitionGroup>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useLightboxStore } from '../store/lightbox.js'
import CommentForm from './CommentForm.vue'

const props = defineProps({
  comment: { type: Object, required: true },
  depth: { type: Number, default: 0 },
})
const emit = defineEmits(['reply'])

const lightbox = useLightboxStore()
const showReplyForm = ref(false)

const API_BASE = import.meta.env.VITE_API_URL?.replace('/api', '') || ''

const avatarUrl = computed(() =>
  `https://api.dicebear.com/7.x/avataaars/svg?seed=${encodeURIComponent(props.comment.email)}&size=40`
)

const fullDate = computed(() => {
  const d = new Date(props.comment.created_at)
  return d.toLocaleString('en-US')
})

const relativeDate = computed(() => {
  const d = new Date(props.comment.created_at)
  const now = new Date()
  const diff = Math.floor((now - d) / 1000)
  if (diff < 60) return 'just now'
  if (diff < 3600) return `${Math.floor(diff / 60)} min ago`
  if (diff < 86400) return `${Math.floor(diff / 3600)} h ago`
  return d.toLocaleDateString('en-US', { day: '2-digit', month: '2-digit', year: '2-digit', hour: '2-digit', minute: '2-digit' })
})

const quotedText = computed(() => {
  const text = props.comment.text?.replace(/<[^>]+>/g, '') || ''
  return text.length > 80 ? text.slice(0, 80) + '...' : text
})

function mediaUrl(path) {
  if (path.startsWith('http')) return path
  return `${API_BASE}${path}`
}

function fileName(path) {
  return path.split('/').pop()
}

function openLightbox(src, type) {
  lightbox.open(type === 'image' ? mediaUrl(src) : mediaUrl(src), type)
}

function toggleReplyForm() {
  showReplyForm.value = !showReplyForm.value
}

function onReplySubmitted() {
  showReplyForm.value = false
  emit('reply', props.comment.id)
}
</script>
