const rawBaseUrl = import.meta.env.VITE_API_URL || '/api'

const BASE_URL = rawBaseUrl.endsWith('/api')
  ? rawBaseUrl
  : `${rawBaseUrl.replace(/\/$/, '')}/api`

async function request(path, options = {}) {
  const response = await fetch(`${BASE_URL}${path}`, options)
  const contentType = response.headers.get('content-type') || ''

  if (!response.ok) {
    const message = contentType.includes('application/json')
      ? JSON.stringify(await response.json())
      : await response.text()

    throw new Error(message || `Request failed with status ${response.status}`)
  }

  if (!contentType.includes('application/json')) {
    const text = await response.text()
    throw new Error(`Expected JSON response, received: ${text.slice(0, 120)}`)
  }

  return response.json()
}

export const api = {
  getComments(params = {}) {
    const query = new URLSearchParams(params).toString()
    return request(`/comments/${query ? `?${query}` : ''}`)
  },

  createComment(formData) {
    return request('/comments/', {
      method: 'POST',
      body: formData,
    })
  },

  getCaptcha() {
    return request('/captcha/')
  },

  previewComment(data) {
    return request('/preview/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(data),
    })
  },
}