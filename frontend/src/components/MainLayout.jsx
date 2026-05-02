// src/layouts/MainLayout.jsx
import { useState, useEffect } from 'react';
import { Outlet } from 'react-router-dom';
import Sidebar from './Sidebar/Sidebar';
import Header from './Header/Header';

export default function MainLayout() {
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [isMobile, setIsMobile]       = useState(window.innerWidth <= 900);

  // Detectar si estamos en móvil/tablet
  useEffect(() => {
    const handleResize = () => {
      const mobile = window.innerWidth <= 900;
      setIsMobile(mobile);
      if (!mobile) setSidebarOpen(false); // cerrar al pasar a desktop
    };
    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, []);

  // Bloquear scroll del body cuando el sidebar está abierto
  useEffect(() => {
    document.body.style.overflow = (isMobile && sidebarOpen) ? 'hidden' : '';
    return () => { document.body.style.overflow = ''; };
  }, [isMobile, sidebarOpen]);

  return (
    <div style={{
      display: 'flex',
      flexDirection: 'column',
      height: '100vh',
      margin: 0,
      backgroundColor: 'var(--bg)',
      overflow: 'hidden',
    }}>

      {/* HEADER */}
      <Header onMenuToggle={() => setSidebarOpen((prev) => !prev)} />

      {/* CUERPO */}
      <div style={{ display: 'flex', flex: 1, overflow: 'hidden', position: 'relative' }}>

        {/* OVERLAY oscuro — solo en móvil/tablet con sidebar abierto */}
        {isMobile && sidebarOpen && (
          <div
            onClick={() => setSidebarOpen(false)}
            style={{
              position: 'fixed',
              inset: 0,
              backgroundColor: 'rgba(0,0,0,0.6)',
              zIndex: 299,
              backdropFilter: 'blur(2px)',
            }}
          />
        )}

        {/* SIDEBAR */}
        <div style={isMobile ? {
          position: 'fixed',
          top: 0,
          left: 0,
          height: '100vh',
          width: '100vw',
          zIndex: 300,
          transform: sidebarOpen ? 'translateX(0)' : 'translateX(-100%)',
          transition: 'transform 0.28s cubic-bezier(0.4, 0, 0.2, 1)',
          overflowY: 'auto',
        } : {
          flexShrink: 0,
          height: '100%',
          overflowY: 'auto',
        }}>
          {/* Botón cerrar — solo en móvil/tablet */}
          {isMobile && (
            <button
              onClick={() => setSidebarOpen(false)}
              style={{
                display: 'flex',
                justifyContent: 'flex-end',
                width: '100%',
                padding: '16px 20px',
                background: 'none',
                border: 'none',
                color: '#ffffff',
                fontSize: '1.4rem',
                cursor: 'pointer',
                boxSizing: 'border-box',
              }}
            >
              ✕
            </button>
          )}
          <Sidebar onNavigate={() => setSidebarOpen(false)} />
        </div>

        {/* CONTENIDO PRINCIPAL */}
        <main style={{ flex: 1, padding: '30px', overflowY: 'auto' }}>
          <Outlet />
        </main>

      </div>
    </div>
  );
}