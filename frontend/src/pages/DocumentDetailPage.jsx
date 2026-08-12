import { useEffect, useState } from 'react'
import { useParams } from 'react-router-dom'
import { getDocument, updateDocument } from '../api.js'

const FIELDS = [
  { key: 'vendor', label: 'Vendor' },
  { key: 'date', label: 'Date' },
  { key: 'total_amount', label: 'Total Amount', type: 'number' },
  { key: 'category', label: 'Category' },
]

export default function DocumentDetailPage() {
  const { id } = useParams()
  const [doc, setDoc] = useState(null)
  const [form, setForm] = useState({})
  const [status, setStatus] = useState('idle')
  const [error, setError] = useState(null)

  useEffect(() => {
    getDocument(id)
      .then((data) => {
        setDoc(data)
        setForm(data)
      })
      .catch((err) => setError(err.message))
  }, [id])

  async function handleSave(event) {
    event.preventDefault()
    setStatus('saving')
    setError(null)
    try {
      const updated = await updateDocument(id, {
        vendor: form.vendor,
        date: form.date,
        total_amount: form.total_amount === '' ? null : Number(form.total_amount),
        category: form.category,
      })
      setDoc(updated)
      setForm(updated)
      setStatus('saved')
    } catch (err) {
      setError(err.message)
      setStatus('idle')
    }
  }

  if (error) return <p className="page error">{error}</p>
  if (!doc) return <p className="page">Loading…</p>

  return (
    <div className="page">
      <h2>{doc.filename}</h2>
      {doc.corrected && <p className="badge">Corrected</p>}

      <form onSubmit={handleSave} className="detail-form">
        {FIELDS.map(({ key, label, type }) => (
          <label key={key}>
            {label}
            <input
              type={type || 'text'}
              step={type === 'number' ? '0.01' : undefined}
              value={form[key] ?? ''}
              onChange={(event) => setForm({ ...form, [key]: event.target.value })}
            />
          </label>
        ))}

        <button type="submit" disabled={status === 'saving'}>
          {status === 'saving' ? 'Saving…' : 'Save corrections'}
        </button>
        {status === 'saved' && <span className="saved-indicator">Saved ✓</span>}
      </form>

      <h3>Line items</h3>
      {doc.line_items?.length ? (
        <table>
          <thead>
            <tr>
              <th>Description</th>
              <th>Qty</th>
              <th>Unit Price</th>
              <th>Amount</th>
            </tr>
          </thead>
          <tbody>
            {doc.line_items.map((item, index) => (
              <tr key={index}>
                <td>{item.description}</td>
                <td>{item.quantity ?? '—'}</td>
                <td>{item.unit_price ?? '—'}</td>
                <td>{item.amount ?? '—'}</td>
              </tr>
            ))}
          </tbody>
        </table>
      ) : (
        <p>No line items extracted.</p>
      )}

      {doc.raw_text && (
        <details>
          <summary>Raw extracted text</summary>
          <pre>{doc.raw_text}</pre>
        </details>
      )}
    </div>
  )
}
