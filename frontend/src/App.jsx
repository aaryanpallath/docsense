import { NavLink, Route, Routes } from 'react-router-dom'
import DocumentDetailPage from './pages/DocumentDetailPage.jsx'
import DocumentListPage from './pages/DocumentListPage.jsx'
import UploadPage from './pages/UploadPage.jsx'

export default function App() {
  return (
    <div className="app">
      <header className="app-header">
        <h1>DocSense</h1>
        <nav>
          <NavLink to="/" end>
            Documents
          </NavLink>
          <NavLink to="/upload">Upload</NavLink>
        </nav>
      </header>
      <main>
        <Routes>
          <Route path="/" element={<DocumentListPage />} />
          <Route path="/upload" element={<UploadPage />} />
          <Route path="/documents/:id" element={<DocumentDetailPage />} />
        </Routes>
      </main>
    </div>
  )
}
