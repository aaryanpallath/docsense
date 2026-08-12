import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { uploadDocument } from '../api.js'

export default function UploadPage() {
  const [file, setFile] = useState(null)
  const [text, setText] = useState('')
  const [isUploading, setIsUploading] = useState(false)
  const [error, setError] = useState(null)
  const [isDragging, setIsDragging] = useState(false)
  const navigate = useNavigate()

  async function handleSubmit(event) {
    event.preventDefault()
    if (!file && !text.trim()) {
      setError('Choose a file or paste some text first.')
      return
    }
    setIsUploading(true)
    setError(null)
    try {
      const doc = await uploadDocument({ file, text: text.trim() || undefined })
      navigate(`/documents/${doc.id}`)
    } catch (err) {
      setError(err.message)
    } finally {
      setIsUploading(false)
    }
  }

  function handleDrop(event) {
    event.preventDefault()
    setIsDragging(false)
    const dropped = event.dataTransfer.files?.[0]
    if (dropped) setFile(dropped)
  }

  return (
    <div className="page">
      <h2>Upload a document</h2>
      <form onSubmit={handleSubmit}>
        <div
          className={`dropzone ${isDragging ? 'dropzone-active' : ''}`}
          onDragOver={(event) => {
            event.preventDefault()
            setIsDragging(true)
          }}
          onDragLeave={() => setIsDragging(false)}
          onDrop={handleDrop}
        >
          <p>{file ? file.name : 'Drag and drop a PDF or image, or click to choose a file'}</p>
          <input
            type="file"
            accept=".pdf,image/*"
            onChange={(event) => setFile(event.target.files?.[0] ?? null)}
          />
        </div>

        <p className="or-divider">— or paste raw text —</p>

        <textarea
          rows={8}
          placeholder="Paste receipt or invoice text here..."
          value={text}
          onChange={(event) => setText(event.target.value)}
        />

        {error && <p className="error">{error}</p>}

        <button type="submit" disabled={isUploading}>
          {isUploading ? 'Extracting…' : 'Upload & Extract'}
        </button>
      </form>
    </div>
  )
}
