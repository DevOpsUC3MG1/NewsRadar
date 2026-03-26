import { Outlet } from 'react-router-dom';
import Sidebar from './Sidebar/Sidebar'; // Importamos tu nuevo componente

export default function MainLayout() {
  return (
    // Usamos Flexbox para poner Sidebar a la izquierda y el contenido a la derecha
    <div style={{ display: 'flex', minHeight: '100vh', margin: 0, backgroundColor: '#1a1a1a' }}>

      {/* 1. El menú lateral fijo */}
      <Sidebar />

      {/* 2. El contenido de la página que va cambiando */}
      <main style={{ flex: 1, padding: '20px', overflowY: 'auto' }}>
        <Outlet />
      </main>

    </div>
  );
}