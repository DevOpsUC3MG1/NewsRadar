// src/layouts/MainLayout.jsx
import { useState, useEffect } from 'react';
import { Outlet } from 'react-router-dom';
import Sidebar from './Sidebar/Sidebar';
import Header from './Header/Header';

export default function MainLayout() {
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [isMobile, setIsMobile]       = useState(window.innerWidth <= 900);

  useEffect(() => {
    const handleResize = () => {
      const mobile = window.innerWidth <= 900;
      setIsMobile(mobile);
      if (!mobile) setSidebarOpen(false);
    };
    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, []);

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

      <Header onMenuToggle={() => setSidebarOpen((prev) => !prev)} />

      <div style={{ display: 'flex', flex: 1, overflow: 'hidden', position: 'relative' }}>

        {/* OVERLAY */}
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

        {/* SIDEBAR WRAPPER */}
        <div style={isMobile ? {
          // Cubre TODA la pantalla desde el borde superior
          position: 'fixed',
          top: 0,
          left: 0,
          width: '100vw',
          height: '100vh',
          zIndex: 300,
          transform: sidebarOpen ? 'translateX(0)' : 'translateX(-100%)',
          transition: 'transform 0.28s cubic-bezier(0.4, 0, 0.2, 1)',
          // Flex column: botón ✕ arriba + sidebar ocupa el resto
          display: 'flex',
          flexDirection: 'column',
          overflow: 'hidden',
        } : {
          flexShrink: 0,
          height: '100%',
        }}>

          {/* Barra superior con el botón ✕ — solo en móvil/tablet */}
          {isMobile && (
            <div style={{
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'flex-end',
              padding: '12px 16px',
              backgroundColor: 'var(--color-nav, #12141d)',
              flexShrink: 0,          // no se comprime
            }}>
              <button
                onClick={() => setSidebarOpen(false)}
                style={{
                  background: 'none',
                  border: 'none',
                  color: '#ffffff',
                  fontSize: '1.3rem',
                  cursor: 'pointer',
                  lineHeight: 1,
                  padding: '4px 8px',
                  borderRadius: '6px',
                }}
              >
                ✕
              </button>
            </div>
          )}

          {/* SIDEBAR — ocupa el espacio restante */}
          <div style={isMobile ? { flex: 1, overflowY: 'auto', minHeight: 0 } : { height: '100%' }}>
            <Sidebar onNavigate={() => setSidebarOpen(false)} />
          </div>

        </div>

        {/* CONTENIDO PRINCIPAL */}
        <main style={{ flex: 1, padding: isMobile ? '0' : '30px', overflowY: 'auto' }}>
          <Outlet />
        </main>

      </div>
    </div>
  );
}