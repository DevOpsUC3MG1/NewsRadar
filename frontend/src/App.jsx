import { BrowserRouter, Routes, Route, Link } from 'react-router-dom'
import Home from './pages/Home'
import About from './pages/About' // Asegúrate de tener este archivo creado

function App() {
  return (
    <BrowserRouter>
      {/* Menú de navegación global */}
      <nav style={{ padding: '20px', textAlign: 'center', background: '#1a1a1a', marginBottom: '20px' }}>
        <Link to="/" style={{ margin: '0 15px', color: '#646cff', fontWeight: 'bold' }}>Inicio</Link>
        <Link to="/about" style={{ margin: '0 15px', color: '#646cff', fontWeight: 'bold' }}>Acerca de</Link>
      </nav>

      {/* Contenedor donde se cargarán las páginas */}
      <main>
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/about" element={<About />} />
        </Routes>
      </main>
    </BrowserRouter>
  )
}

export default App