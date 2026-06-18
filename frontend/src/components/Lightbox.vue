<template>
  <Teleport to="body">
    <Transition name="lightbox-fade">
      <div v-if="lightbox.isOpen" class="lightbox-overlay" @click.self="lightbox.close()">
        <div class="lightbox-box" :class="lightbox.type">
          <button class="lightbox-close" @click="lightbox.close()">Close</button>

          <div v-if="lightbox.type === 'image'" class="lightbox-image-wrap">
            <img :src="lightbox.src" alt="Attachment" class="lightbox-img" />
          </div>

          <div v-else class="lightbox-file-wrap">
            <div class="lightbox-file-header">
              <span class="file-icon-lg"></span>
              <span class="file-name">{{ fileName }}</span>
              <a :href="lightbox.src" download class="download-btn">Download</a>
            </div>
            <pre class="file-content">{{ lightbox.fileContent }}</pre>
          </div>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup>
import { computed } from 'vue'
import { useLightboxStore } from '../store/lightbox.js'

const lightbox = useLightboxStore()

const fileName = computed(() => lightbox.src.split('/').pop())
</script>
