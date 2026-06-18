<template>
  <article :id="`comment-${comment.id}`" class="comment-card" :class="{ 'is-reply': depth > 0 }">
    <div class="comment-row">
      <div class="thread-column">
        <div class="comment-avatar">
          <img :src="avatarUrl" :alt="comment.username" />
        </div>
        <div v-if="hasReplies" class="thread-line"></div>
      </div>

      <div class="comment-main">
        <div class="comment-meta">
          <a
            v-if="comment.homepage"
            class="comment-username"
            :href="comment.homepage"
            target="_blank"
            rel="noopener noreferrer"
            :title="comment.email"
          >
            {{ comment.username }}
          </a>
          <span v-else class="comment-username" :title="comment.email">{{ comment.username }}</span>
          <span class="meta-dot">/</span>
          <time class="comment-date" :datetime="comment.created_at" :title="fullDate">{{ shortDate }}</time>
        </div>

        <div class="comment-content">
          <blockquote v-if="depth > 0 && quotedText" class="reply-quote">{{ quotedText }}</blockquote>
          <div class="comment-body" v-html="comment.text"></div>

          <div class="comment-attachments" v-if="comment.image || comment.attachment">
            <button
              v-if="comment.image"
              type="button"
              class="attachment-image"
              @click="openLightbox(comment.image, 'image')"
            >
              <img :src="mediaUrl(comment.image)" :alt="`Image by ${comment.username}`" />
              <span>Open image</span>
            </button>

            <button
              v-if="comment.attachment"
              type="button"
              class="attachment-file"
              @click="openLightbox(comment.attachment, 'file')"
            >
              <span class="file-label">{{ fileName(comment.attachment) }}</span>
            </button>
          </div>
        </div>

        <div class="comment-actions" aria-label="Comment actions">
          <button type="button" class="reply-button" @click="toggleReplyForm">
            Reply
          </button>
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

        <div class="replies-container" v-if="hasReplies">
          <TransitionGroup name="comment-list">
            <CommentCard
              v-for="reply in comment.replies"
              :key="reply.id"
              :comment="reply"
              :depth="depth + 1"
            />
          </TransitionGroup>
        </div>
      </div>
    </div>
  </article>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useLightboxStore } from '../store/lightbox.js'
import CommentForm from './CommentForm.vue'

const props = defineProps({
  comment: { type: Object, required: true },
  depth: { type: Number, default: 0 },
})

const lightbox = useLightboxStore()
const showReplyForm = ref(false)

const API_ORIGIN = (import.meta.env.VITE_API_URL || '')
  .replace(/\/api\/?$/, '')
  .replace(/\/$/, '')

const hasReplies = computed(() => Array.isArray(props.comment.replies) && props.comment.replies.length > 0)

const avatarUrl = computed(() => {
  const seed = props.comment.username || `comment-${props.comment.id}`
  return `https://api.dicebear.com/10.x/lorelei-neutral/svg?seed=${encodeURIComponent(seed)}&size=80`
})

const fullDate = computed(() => {
  const date = new Date(props.comment.created_at)
  return date.toLocaleString('en-GB')
})

const shortDate = computed(() => {
  const date = new Date(props.comment.created_at)
  const day = String(date.getDate()).padStart(2, '0')
  const month = String(date.getMonth() + 1).padStart(2, '0')
  const year = String(date.getFullYear()).slice(-2)
  const hours = String(date.getHours()).padStart(2, '0')
  const minutes = String(date.getMinutes()).padStart(2, '0')
  return `${day}.${month}.${year} at ${hours}:${minutes}`
})

const quotedText = computed(() => {
  const source = props.comment.parent_text || ''
  const text = source.replace(/<[^>]+>/g, '')
  return text.length > 120 ? `${text.slice(0, 120)}...` : text
})

function mediaUrl(path) {
  if (!path) {
    return ''
  }

  if (path.startsWith('http://') || path.startsWith('https://')) {
    return path
  }

  return `${API_ORIGIN}${path}`
}

function fileName(path) {
  return path.split('/').pop()
}

function openLightbox(path, type) {
  lightbox.open(mediaUrl(path), type)
}

function toggleReplyForm() {
  showReplyForm.value = !showReplyForm.value
}

function onReplySubmitted() {
  showReplyForm.value = false
}
</script>