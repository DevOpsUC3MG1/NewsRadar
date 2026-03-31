import { BrowserRouter, Routes, Route } from 'react-router-dom'
import PantallaEntrada from './pages/pantalla-entrada/pantalla-entrada.jsx'
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
        <Route path="/" element={<Prueba />} />
        <Route path="/pantalla-entrada" element={<PantallaEntrada />} />

        {/* === RUTAS PROTEGIDAS === */}
        {/* Envolvemos el MainLayout con ProtectedRoute */}
        <Route 
          path="/app" 
          element={
            <ProtectedRoute>
              <MainLayout />
            </ProtectedRoute>
          }
        >
          {/* Todas estas rutas ahora están protegidas gracias al padre */}
          <Route index element={<Home />} />
          <Route path="about" element={<About />} />
          <Route path="ui-testing" element={<UiTesting />} />
        </Route>
      </Routes>
    </BrowserRouter>
  )
}

export default App