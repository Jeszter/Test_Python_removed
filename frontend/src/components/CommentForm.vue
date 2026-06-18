<template>
  <div class="comment-form-wrapper">
    <div class="comment-form" :class="{ 'is-reply': parentId }">
      <h3 class="form-title">
        {{ parentId ? 'Reply to comment' : 'Leave a comment' }}
        <button v-if="parentId" class="cancel-reply" @click="cancelReply">Cancel</button>
      </h3>

      <form @submit.prevent="handleSubmit" novalidate>
        <div class="form-row">
          <div class="form-group" :class="{ error: errors.username }">
            <label for="username">User name <span class="required">*</span></label>
            <input
              id="username"
              v-model.trim="form.username"
              type="text"
              placeholder="Latin letters and digits only"
              @blur="validateField('username')"
              @input="clearError('username')"
            />
            <span class="field-error" v-if="errors.username">{{ errors.username }}</span>
          </div>

          <div class="form-group" :class="{ error: errors.email }">
            <label for="email">E-mail <span class="required">*</span></label>
            <input
              id="email"
              v-model.trim="form.email"
              type="email"
              placeholder="user@example.com"
              @blur="validateField('email')"
              @input="clearError('email')"
            />
            <span class="field-error" v-if="errors.email">{{ errors.email }}</span>
          </div>

          <div class="form-group" :class="{ error: errors.homepage }">
            <label for="homepage">Home page</label>
            <input
              id="homepage"
              v-model.trim="form.homepage"
              type="url"
              placeholder="https://example.com"
              @blur="validateField('homepage')"
              @input="clearError('homepage')"
            />
            <span class="field-error" v-if="errors.homepage">{{ errors.homepage }}</span>
          </div>
        </div>

        <div class="tag-toolbar">
          <span class="toolbar-label">Tags:</span>
          <button type="button" class="tag-btn" @click="insertTag('i')">[i]</button>
          <button type="button" class="tag-btn" @click="insertTag('strong')">[strong]</button>
          <button type="button" class="tag-btn" @click="insertTag('code')">[code]</button>
          <button type="button" class="tag-btn" @click="insertLinkTag()">[a]</button>
          <button type="button" class="toolbar-preview-btn" @click="togglePreview">
            {{ showPreview ? 'Edit' : 'Preview' }}
          </button>
        </div>

        <div class="form-group" :class="{ error: errors.text }">
          <label for="text">Message <span class="required">*</span></label>
          <div v-if="showPreview" class="preview-box" v-html="previewHtml"></div>
          <textarea
            v-else
            id="text"
            ref="textareaRef"
            v-model="form.text"
            rows="5"
            placeholder="Your comment... (allowed tags: &lt;i&gt;, &lt;strong&gt;, &lt;code&gt;, &lt;a&gt;)"
            @blur="validateField('text')"
            @input="clearError('text')"
          ></textarea>
          <span class="field-error" v-if="errors.text">{{ errors.text }}</span>
        </div>

        <div class="form-row uploads-row">
          <div class="form-group" :class="{ error: errors.image }">
            <label>Image <span class="hint">(JPG, GIF, PNG - up to 320x240)</span></label>
            <div class="file-drop-zone" @click="$refs.imageInput.click()" @dragover.prevent @drop.prevent="handleImageDrop">
              <span v-if="!imagePreviewUrl">Select or drop a file</span>
              <img v-else :src="imagePreviewUrl" class="image-thumb" alt="preview" />
            </div>
            <input ref="imageInput" type="file" accept=".jpg,.jpeg,.gif,.png" hidden @change="handleImageChange" />
            <button v-if="form.image" type="button" class="remove-file" @click="removeImage">Remove</button>
            <span class="field-error" v-if="errors.image">{{ errors.image }}</span>
          </div>

          <div class="form-group" :class="{ error: errors.attachment }">
            <label>Text file <span class="hint">(TXT - up to 100 KB)</span></label>
            <div class="file-drop-zone" @click="$refs.fileInput.click()">
              <span v-if="!form.attachment">Select TXT file</span>
              <span v-else class="file-name">{{ form.attachment.name }}</span>
            </div>
            <input ref="fileInput" type="file" accept=".txt" hidden @change="handleFileChange" />
            <button v-if="form.attachment" type="button" class="remove-file" @click="removeFile">Remove</button>
            <span class="field-error" v-if="errors.attachment">{{ errors.attachment }}</span>
          </div>
        </div>

        <div class="form-group captcha-group" :class="{ error: errors.captcha_value }">
          <label>CAPTCHA <span class="required">*</span></label>
          <div class="captcha-row">
            <img
              v-if="captcha.image"
              :src="captcha.image"
              class="captcha-img"
              alt="CAPTCHA"
              @click="refreshCaptcha"
              title="Click to refresh"
            />
            <div v-else class="captcha-placeholder">Loading...</div>
            <button type="button" class="captcha-refresh" @click="refreshCaptcha" title="Refresh CAPTCHA">Refresh</button>
            <input
              v-model.trim="form.captcha_value"
              type="text"
              class="captcha-input"
              placeholder="Enter characters"
              maxlength="10"
              @blur="validateField('captcha_value')"
              @input="clearError('captcha_value')"
            />
          </div>
          <span class="field-error" v-if="errors.captcha_value">{{ errors.captcha_value }}</span>
        </div>

        <div class="server-errors" v-if="serverErrors.length">
          <p v-for="(err, i) in serverErrors" :key="i">{{ err }}</p>
        </div>

        <div class="form-actions">
          <button type="submit" class="submit-btn" :disabled="submitting">
            <span v-if="submitting" class="btn-spinner"></span>
            {{ submitting ? 'Sending...' : 'Submit' }}
          </button>
        </div>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, watch, onMounted } from 'vue'
import { useCommentsStore } from '../store/comments.js'
import { api } from '../api/index.js'

const props = defineProps({
  parentId: { type: Number, default: null }
})
const emit = defineEmits(['submitted', 'cancel'])

const store = useCommentsStore()
const textareaRef = ref(null)
const imageInput = ref(null)
const fileInput = ref(null)

const form = reactive({
  username: '',
  email: '',
  homepage: '',
  text: '',
  image: null,
  attachment: null,
  captcha_value: '',
})

const errors = reactive({})
const serverErrors = ref([])
const submitting = ref(false)
const showPreview = ref(false)
const previewHtml = ref('')
const imagePreviewUrl = ref(null)

const captcha = reactive({ key: '', image: '' })

onMounted(() => refreshCaptcha())

async function refreshCaptcha() {
  try {
    const data = await api.getCaptcha()
    captcha.key = data.key
    captcha.image = data.image
    form.captcha_value = ''
    clearError('captcha_value')
  } catch (e) {
    console.error('Failed to load CAPTCHA', e)
  }
}

function insertTag(tag) {
  const ta = textareaRef.value
  if (!ta) return
  const start = ta.selectionStart
  const end = ta.selectionEnd
  const selected = form.text.slice(start, end) || 'text'
  const before = form.text.slice(0, start)
  const after = form.text.slice(end)
  form.text = `${before}<${tag}>${selected}</${tag}>${after}`
  const newPos = start + tag.length + 2 + selected.length
  setTimeout(() => { ta.focus(); ta.setSelectionRange(newPos, newPos) })
}

function insertLinkTag() {
  const href = prompt('Enter URL:')
  if (!href) return
  const title = prompt('Enter title (optional):') || ''
  const ta = textareaRef.value
  if (!ta) return
  const start = ta.selectionStart
  const end = ta.selectionEnd
  const selected = form.text.slice(start, end) || 'link'
  const before = form.text.slice(0, start)
  const after = form.text.slice(end)
  const titleAttr = title ? ` title="${title}"` : ''
  form.text = `${before}<a href="${href}"${titleAttr}>${selected}</a>${after}`
}

async function togglePreview() {
  if (!showPreview.value) {
    try {
      const data = await store.previewComment(form.text)
      previewHtml.value = data.preview
      showPreview.value = true
    } catch (e) {
      errors.text = 'Preview failed. Check the HTML tags.'
    }
  } else {
    showPreview.value = false
  }
}

function handleImageChange(e) {
  const file = e.target.files[0]
  if (!file) return
  const allowed = ['image/jpeg', 'image/gif', 'image/png']
  if (!allowed.includes(file.type)) {
    errors.image = 'Allowed formats: JPG, GIF, PNG'
    return
  }
  form.image = file
  imagePreviewUrl.value = URL.createObjectURL(file)
  clearError('image')
}

function handleImageDrop(e) {
  const file = e.dataTransfer.files[0]
  if (file) {
    const fakeEvent = { target: { files: [file] } }
    handleImageChange(fakeEvent)
  }
}

function removeImage() {
  form.image = null
  imagePreviewUrl.value = null
  if (imageInput.value) imageInput.value.value = ''
}

function handleFileChange(e) {
  const file = e.target.files[0]
  if (!file) return
  if (!file.name.endsWith('.txt')) {
    errors.attachment = 'Allowed format: TXT'
    return
  }
  if (file.size > 100 * 1024) {
    errors.attachment = 'File must not exceed 100 KB'
    return
  }
  form.attachment = file
  clearError('attachment')
}

function removeFile() {
  form.attachment = null
  if (fileInput.value) fileInput.value.value = ''
}

function validateField(field) {
  clearError(field)
  switch (field) {
    case 'username':
      if (!form.username) { errors.username = 'Required field'; return false }
      if (!/^[a-zA-Z0-9]+$/.test(form.username)) { errors.username = 'Latin letters and digits only'; return false }
      break
    case 'email':
      if (!form.email) { errors.email = 'Required field'; return false }
      if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(form.email)) { errors.email = 'Invalid email'; return false }
      break
    case 'homepage':
      if (form.homepage && !/^https?:\/\/.+/.test(form.homepage)) { errors.homepage = 'Invalid URL'; return false }
      break
    case 'text':
      if (!form.text.trim()) { errors.text = 'Required field'; return false }
      break
    case 'captcha_value':
      if (!form.captcha_value) { errors.captcha_value = 'Enter the characters from the image'; return false }
      if (!/^[a-zA-Z0-9]+$/.test(form.captcha_value)) { errors.captcha_value = 'Latin letters and digits only'; return false }
      break
  }
  return true
}

function validateAll() {
  const fields = ['username', 'email', 'homepage', 'text', 'captcha_value']
  return fields.every(f => validateField(f))
}

function clearError(field) {
  delete errors[field]
}

async function handleSubmit() {
  serverErrors.value = []
  if (!validateAll()) return

  submitting.value = true
  try {
    const formData = new FormData()
    formData.append('username', form.username)
    formData.append('email', form.email)
    if (form.homepage) formData.append('homepage', form.homepage)
    formData.append('text', form.text)
    formData.append('captcha_key', captcha.key)
    formData.append('captcha_value', form.captcha_value)
    if (props.parentId) formData.append('parent', props.parentId)
    if (form.image) formData.append('image', form.image)
    if (form.attachment) formData.append('attachment', form.attachment)

    await store.createComment(formData)

    Object.assign(form, { username: '', email: '', homepage: '', text: '', image: null, attachment: null, captcha_value: '' })
    imagePreviewUrl.value = null
    showPreview.value = false
    await refreshCaptcha()
    emit('submitted')
  } catch (e) {
    if (e.data) {
      const data = e.data
      Object.keys(data).forEach(key => {
        const msgs = Array.isArray(data[key]) ? data[key] : [data[key]]
        if (key === 'non_field_errors') {
          serverErrors.value.push(...msgs)
        } else {
          errors[key] = msgs[0]
        }
      })
      if (data.captcha_value) await refreshCaptcha()
    } else {
      serverErrors.value = ['Server error. Try again later.']
    }
  } finally {
    submitting.value = false
  }
}

function cancelReply() {
  emit('cancel')
}
</script>
