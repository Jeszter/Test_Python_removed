const BASE_URL = import.meta.env.VITE_API_URL || '/api'

async function request(path, options = {}) {
  const res = await fetch(`${BASE_URL}${path}`, options)
  if (!res.ok) {
    const err = await res.json().catch(() => ({}))
    throw Object.assign(new Error('API Error'), { data: err, status: res.status })
  }
  if (res.status === 204) return null
  return res.json()
}

export const api = {
  getComments({ page = 1, ordering = '-created_at' } = {}) {
    return request(`/comments/?page=${page}&ordering=${ordering}`)
  },

  createComment(formData) {
    return request('/comments/', {
      method: 'POST',
      body: formData,
    })
  },

  previewComment(text) {
    return request('/comments/preview/', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ text }),
    })
  },

  getCaptcha() {
    return request('/captcha/')
  },

  validateCaptcha(key, value) {
    return request('/captcha/validate/', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ key, value }),
    })
  },
}
