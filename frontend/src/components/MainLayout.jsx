import { Outlet } from 'react-router-dom';
import Sidebar from './Sidebar/Sidebar';
import Header from './Header/Header';

export default function MainLayout() {
  return (
    // CONTENEDOR PRINCIPAL: Ahora es una columna (flexDirection: 'column')
    <div style={{ display: 'flex', flexDirection: 'column', height: '100vh', margin: 0, backgroundColor: 'var(--bg)', overflow: 'hidden' }}>

      {/* 1. FILA SUPERIOR: El Header ocupa todo el ancho de la pantalla */}
      <Header />

      {/* 2. FILA INFERIOR: Ocupa el resto del espacio (flex: 1) y se divide en 2 columnas */}
      <div style={{ display: 'flex', flex: 1, overflow: 'hidden' }}>

        {/* Columna Izquierda: El menú lateral */}
        <Sidebar />

        {/* Columna Derecha: El contenido de la página */}
        <main style={{ flex: 1, padding: '30px', overflowY: 'auto' }}>
          <Outlet />
        </main>

      </div>
    </div>
  );
}