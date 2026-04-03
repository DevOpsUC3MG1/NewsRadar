import { BrowserRouter, Routes, Route } from 'react-router-dom'
import PantallaEntrada from './pages/login/login.jsx'
import Registro from './pages/registro/registro.jsx'
import Home from './pages/Home'
import About from './pages/About'
import UiTesting from './pages/UiTesting'
import MainLayout from './components/MainLayout'
import Prueba from './pages/prueba.jsx'


// 1. Importamos nuestro componente protector
import ProtectedRoute from './components/ProtectedRoute' 

function App() {
  return (
    <BrowserRouter>
      <Routes>
        {/* === RUTAS PÚBLICAS === */}
        {/* Cualquiera puede ver estas páginas sin iniciar sesión */}
          { /* <Route path="/" element={<Prueba />} /> */ }
        <Route path="/" element={<PantallaEntrada />} />
        <Route path="/registro" element={<Registro />} />

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
        </Route>
      </Routes>
    </BrowserRouter>
  )
}

export default App