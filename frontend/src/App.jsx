import { BrowserRouter, Routes, Route } from 'react-router-dom'
import Home from './pages/Home'
import About from './pages/About'
import UiTesting from './pages/UiTesting'
import MainLayout from './components/MainLayout' // 👇 Importamos el Layout

function App() {
  return (
    <BrowserRouter>
      <Routes>
        {/* Envolvemos todas las rutas dentro del MainLayout */}
        <Route path="/" element={<MainLayout />}>

          {/* El index significa que Home se carga por defecto en la ruta "/" */}
          <Route index element={<Home />} />

          <Route path="about" element={<About />} />
          <Route path="ui-testing" element={<UiTesting />} />

        </Route>
      </Routes>
    </BrowserRouter>
  )
}

export default App