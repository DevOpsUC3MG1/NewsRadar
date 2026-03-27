import { BrowserRouter, Routes, Route } from 'react-router-dom'
import PantallaEntrada from './pages/pantalla-entrada/pantalla-entrada.jsx'
import Home from './pages/Home'
import About from './pages/About'
import UiTesting from './pages/UiTesting'
import MainLayout from './components/MainLayout'
import Prueba from './pages/prueba.jsx'

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Prueba />} />
        <Route path="/logout" element={<PantallaEntrada />} />

        {/* Envolvemos todas las rutas dentro del MainLayout */}
        <Route path="/app" element={<MainLayout />}>

          {/* El index significa que Home se carga por defecto en la ruta "/app" */}
          <Route index element={<Home />} />

          <Route path="about" element={<About />} />
          <Route path="ui-testing" element={<UiTesting />} />

        </Route>
      </Routes>
    </BrowserRouter>
  )
}

export default App