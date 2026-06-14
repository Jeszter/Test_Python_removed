<template>
  <div class="pagination">
    <button
      class="page-btn"
      :disabled="current === 1"
      @click="$emit('change', current - 1)"
    >Previous</button>

    <button
      v-for="page in visiblePages"
      :key="page"
      class="page-btn"
      :class="{ active: page === current, ellipsis: page === '...' }"
      :disabled="page === '...'"
      @click="page !== '...' && $emit('change', page)"
    >{{ page }}</button>

    <button
      class="page-btn"
      :disabled="current === total"
      @click="$emit('change', current + 1)"
    >Next</button>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  current: { type: Number, required: true },
  total: { type: Number, required: true },
})
defineEmits(['change'])

const visiblePages = computed(() => {
  const pages = []
  const { current, total } = props
  if (total <= 7) {
    for (let i = 1; i <= total; i++) pages.push(i)
    return pages
  }
  pages.push(1)
  if (current > 3) pages.push('...')
  for (let i = Math.max(2, current - 1); i <= Math.min(total - 1, current + 1); i++) pages.push(i)
  if (current < total - 2) pages.push('...')
  pages.push(total)
  return pages
})
</script>
