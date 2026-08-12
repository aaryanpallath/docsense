import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { listDocuments } from '../api.js'

export default function DocumentListPage() {
  const [documents, setDocuments] = useState([])
  const [error, setError] = useState(null)
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    listDocuments()
      .then(setDocuments)
      .catch((err) => setError(err.message))
      .finally(() => setIsLoading(false))
  }, [])

  if (isLoading) return <p className="page">Loading…</p>
  if (error) return <p className="page error">{error}</p>

  if (documents.length === 0) {
    return (
      <div className="page">
        <p>
          No documents yet. <Link to="/upload">Upload one</Link> to get started.
        </p>
      </div>
    )
  }

  return (
    <div className="page">
      <h2>Documents</h2>
      <table>
        <thead>
          <tr>
            <th>Vendor</th>
            <th>Date</th>
            <th>Amount</th>
            <th>Category</th>
          </tr>
        </thead>
        <tbody>
          {documents.map((doc) => (
            <tr key={doc.id}>
              <td>
                <Link to={`/documents/${doc.id}`}>{doc.vendor || doc.filename}</Link>
              </td>
              <td>{doc.date || '—'}</td>
              <td>{doc.total_amount != null ? `$${doc.total_amount.toFixed(2)}` : '—'}</td>
              <td>{doc.category || '—'}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}
