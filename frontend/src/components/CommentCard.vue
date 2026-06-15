<template>
  <article :id="'comment-' + comment.id" class="comment-card" :class="{ 'is-reply': depth > 0 }" :style="{ '--level': normalizedDepth }">
    <div class="comment-header-line">
      <div class="comment-avatar">
        <img :src="avatarUrl" :alt="comment.username" />
      </div>

      <div class="comment-header-bar">
        <div class="comment-author-block">
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
          <time class="comment-date" :datetime="comment.created_at" :title="fullDate">{{ shortDate }}</time>
        </div>

        <div class="comment-tools" aria-label="Comment actions">
          <a class="icon-link" :href="anchorHref" aria-label="Comment link">#</a>
          <button type="button" class="icon-btn" aria-label="Bookmark">
            <svg viewBox="0 0 24 24" aria-hidden="true">
              <path d="M7 4h10a1 1 0 0 1 1 1v15l-6-3-6 3V5a1 1 0 0 1 1-1z" />
            </svg>
          </button>
          <button type="button" class="icon-btn" aria-label="Reply" @click="toggleReplyForm">
            <svg viewBox="0 0 24 24" aria-hidden="true">
              <path d="M9 8H6v5a5 5 0 0 0 5 5h7" />
              <path d="M9 5v6l-4-3 4-3z" />
            </svg>
          </button>
          <button type="button" class="icon-btn" aria-label="Details">
            <svg viewBox="0 0 24 24" aria-hidden="true">
              <path d="M12 11v6" />
              <path d="M12 7h.01" />
              <path d="M12 21a9 9 0 1 0 0-18 9 9 0 0 0 0 18z" />
            </svg>
          </button>
        </div>

        <div class="comment-rating" aria-label="Comment rating">
          <button type="button" aria-label="Vote up">
            <svg viewBox="0 0 24 24" aria-hidden="true">
              <path d="M12 5v14" />
              <path d="M7 10l5-5 5 5" />
            </svg>
          </button>
          <span>0</span>
          <button type="button" aria-label="Vote down">
            <svg viewBox="0 0 24 24" aria-hidden="true">
              <path d="M12 5v14" />
              <path d="M7 14l5 5 5-5" />
            </svg>
          </button>
        </div>
      </div>
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
          <img :src="mediaUrl(comment.image)" :alt="'Image by ' + comment.username" />
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
        />
      </TransitionGroup>
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

const API_BASE = import.meta.env.VITE_API_URL?.replace('/api', '') || ''

const normalizedDepth = computed(() => Math.min(props.depth, 5))
const anchorHref = computed(() => `#comment-${props.comment.id}`)

const avatarUrl = computed(() =>
  `https://api.dicebear.com/7.x/avataaars/svg?seed=${encodeURIComponent(props.comment.email)}&size=48`
)

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
  return text.length > 100 ? `${text.slice(0, 100)}...` : text
})

function mediaUrl(path) {
  if (path.startsWith('http')) return path
  return `${API_BASE}${path}`
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
