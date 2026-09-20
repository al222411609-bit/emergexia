import { Navigate, Route, Routes } from 'react-router-dom'
import { useAuth } from './lib/auth.jsx'
import Layout from './components/Layout.jsx'
import BrandLoader from './components/BrandLoader.jsx'
import Login from './pages/Login.jsx'
import Home from './pages/Home.jsx'
import ModulePage from './pages/ModulePage.jsx'
import SettingsPage from './pages/SettingsPage.jsx'

function Protected({ children }) {
  const { user, loading, connError, retry } = useAuth()
  if (connError) {
    return <BrandLoader mode="error" message="No se pudo conectar con el servidor" detail={connError} onRetry={retry} />
  }
  if (loading) return <BrandLoader mode="loading" />
  return user ? children : <Navigate to="/login" replace />
}

export default function App() {
  const { user, loading, connError, retry } = useAuth()

  if (connError) {
    return <BrandLoader mode="error" message="No se pudo conectar con el servidor" detail={connError} onRetry={retry} />
  }

  return (
    <Routes>
      <Route
        path="/login"
        element={loading ? <BrandLoader mode="loading" /> : user ? <Navigate to="/" replace /> : <Login />}
      />
      <Route element={<Protected><Layout /></Protected>}>
        <Route index element={<Home />} />
        <Route path="configuracion" element={<SettingsPage />} />
        <Route path=":module" element={<ModulePage />} />
      </Route>
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  )
}
