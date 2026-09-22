import { Navigate, Route, Routes } from 'react-router-dom'
import { useAuth } from './lib/auth.jsx'
import Layout from './components/Layout.jsx'
import LoadingScreen from './components/LoadingScreen.jsx'
import Login from './pages/Login.jsx'
import Home from './pages/Home.jsx'
import ModulePage from './pages/ModulePage.jsx'
import SettingsPage from './pages/SettingsPage.jsx'
import PersonFormPage from './pages/PersonFormPage.jsx'

function Protected({ children }) {
  const { user, loading } = useAuth()
  if (loading) return <LoadingScreen />
  return user ? children : <Navigate to="/login" replace />
}

export default function App() {
  const { user, loading } = useAuth()

  return (
    <Routes>
      <Route
        path="/login"
        element={loading ? <LoadingScreen /> : user ? <Navigate to="/" replace /> : <Login />}
      />
      <Route element={<Protected><Layout /></Protected>}>
        <Route index element={<Home />} />
        <Route path="configuracion" element={<SettingsPage />} />
        <Route path="doctores/nuevo" element={<PersonFormPage moduleKey="doctores" />} />
        <Route path="operadores/nuevo" element={<PersonFormPage moduleKey="operadores" />} />
        <Route path=":module" element={<ModulePage />} />
      </Route>
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  )
}
