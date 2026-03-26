import { BrowserRouter, Routes, Route, Link } from 'react-router-dom'
import Home from './pages/Home'
import About from './pages/About'
import UiTesting from './pages/UiTesting' // 👇 1. Importamos la nueva página de pruebas

function App() {
  return (
    <BrowserRouter>
      {/* Menú de navegación global */}
      <nav style={{ padding: '20px', textAlign: 'center', background: '#1a1a1a', marginBottom: '20px' }}>
        <Link to="/" style={{ margin: '0 15px', color: '#646cff', fontWeight: 'bold' }}>Inicio</Link>
        <Link to="/about" style={{ margin: '0 15px', color: '#646cff', fontWeight: 'bold' }}>Acerca de</Link>
        {/* 👇 2. Añadimos el enlace para ir a ver los componentes */}
        <Link to="/ui-testing" style={{ margin: '0 15px', color: '#42b883', fontWeight: 'bold' }}>Componentes</Link>
      </nav>

      {/* Contenedor donde se cargarán las páginas */}
      <main>
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/about" element={<About />} />
          {/* 👇 3. Añadimos la ruta que carga la página */}
          <Route path="/ui-testing" element={<UiTesting />} />
        </Routes>
      </main>
    </BrowserRouter>
  )
}

export default App