import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useLightboxStore = defineStore('lightbox', () => {
  const isOpen = ref(false)
  const src = ref('')
  const type = ref('image')
  const fileContent = ref('')

  async function open(url, mediaType = 'image') {
    src.value = url
    type.value = mediaType
    isOpen.value = true

    if (mediaType === 'file') {
      try {
        const res = await fetch(url)
        fileContent.value = await res.text()
      } catch {
        fileContent.value = 'Could not load the file.'
      }
    }
  }

  function close() {
    isOpen.value = false
    src.value = ''
    fileContent.value = ''
  }

  return { isOpen, src, type, fileContent, open, close }
})
