// App.jsx
import { BrowserRouter, Routes, Route } from 'react-router-dom'
import PantallaEntrada from './pages/login/login.jsx'
import Registro from './pages/registro/registro.jsx'
import ForgotPwd from './pages/change_pwd/forgot_pwd.jsx'
import ChangePwd from './pages/change_pwd/change_pwd.jsx'
import ResendVerify from './pages/verify_acc/verify_acc.jsx' // <-- 1. Importamos la nueva pantalla
import VerifyAcc from './pages/verify_acc/confirm_verify.jsx'
import Dashboard from './pages/dashboard/dashboard.jsx'
import Notifications from './pages/notificaciones/notificaciones.jsx'
import Resumen from './pages/resumen/resumen.jsx'
import Profile from './pages/user_profile/user_profile.jsx'
import Home from './pages/Home'
import About from './pages/About'
import UiTesting from './pages/UiTesting'
import MainLayout from './components/MainLayout'
import Prueba from './pages/prueba.jsx'

// Importamos nuestro componente protector
import ProtectedRoute from './components/ProtectedRoute'

function App() {
  return (
    <BrowserRouter>
      <Routes>
        {/* === RUTAS PÚBLICAS === */}
        {/* Cualquiera puede ver estas páginas sin iniciar sesión */}
        <Route path="/" element={<PantallaEntrada />} />
        <Route path="/registro" element={<Registro />} />
        <Route path="/recuperar-password" element={<ForgotPwd />} />
        <Route path="/restablecer-password" element={<ChangePwd />} />
          {/* <-- 2. Añadimos la ruta de verificación aquí temporalmente para depurar --> */}
        <Route path="/reenviar-verificacion" element={<ResendVerify />} />
        <Route path="/verificar-cuenta" element={<VerifyAcc />} />


        {/* === RUTAS PROTEGIDAS === */}
        {/* Envolvemos el MainLayout con ProtectedRoute */}
        <Route 
          element={
            <ProtectedRoute>
              <MainLayout />
            </ProtectedRoute>
          }
        >
          {/* Ahora sí, las URLs serán directas */}
          <Route path="/app" element={<Home />} />
          <Route path="/about" element={<About />} />
          <Route path="/ui-testing" element={<UiTesting />} />
          <Route path="/pr" element={<Prueba />} />
          <Route path="/dashboard" element={<Dashboard />} />
          <Route path="/notificaciones" element={<Notifications />} />
          <Route path="/profile" element={<Profile />} />
          <Route path="/resumen" element={<Resumen />} />
        </Route>
      </Routes>
    </BrowserRouter>
  )
}

export default App