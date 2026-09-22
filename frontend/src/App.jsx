import { Navigate, Route, Routes } from 'react-router-dom'
import { useAuth } from './lib/auth.jsx'
import Layout from './components/Layout.jsx'
import Login from './pages/Login.jsx'
import Home from './pages/Home.jsx'
import ModulePage from './pages/ModulePage.jsx'
import ModuleFormPage from './pages/ModuleFormPage.jsx'
import RecordDetailPage from './pages/RecordDetailPage.jsx'
import SettingsPage from './pages/SettingsPage.jsx'

function Protected({ children }) {
  const { user, loading } = useAuth()
  if (loading) return <div className="splash">Cargando…</div>
  return user ? children : <Navigate to="/login" replace />
}

export default function App() {
  const { user, loading } = useAuth()

  return (
    <Routes>
      <Route
        path="/login"
        element={loading ? <div className="splash">Cargando…</div> : user ? <Navigate to="/" replace /> : <Login />}
      />
      <Route element={<Protected><Layout /></Protected>}>
        <Route index element={<Home />} />
        <Route path="configuracion" element={<SettingsPage />} />
        <Route path=":module/nuevo" element={<ModuleFormPage />} />
        <Route path=":module/:id" element={<RecordDetailPage />} />
        <Route path=":module" element={<ModulePage />} />
      </Route>
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  )
}
