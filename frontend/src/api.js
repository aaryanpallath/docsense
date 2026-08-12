const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'

async function handleResponse(response) {
  if (!response.ok) {
    const body = await response.json().catch(() => ({}))
    throw new Error(body.detail || `Request failed: ${response.status}`)
  }
  return response.json()
}

export function listDocuments() {
  return fetch(`${API_BASE_URL}/documents`).then(handleResponse)
}

export function getDocument(id) {
  return fetch(`${API_BASE_URL}/documents/${id}`).then(handleResponse)
}

export function uploadDocument({ file, text }) {
  const formData = new FormData()
  if (file) formData.append('file', file)
  if (text) formData.append('text', text)

  return fetch(`${API_BASE_URL}/documents`, {
    method: 'POST',
    body: formData,
  }).then(handleResponse)
}

export function updateDocument(id, fields) {
  return fetch(`${API_BASE_URL}/documents/${id}`, {
    method: 'PATCH',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(fields),
  }).then(handleResponse)
}
