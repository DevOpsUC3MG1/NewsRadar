// Sidebar.jsx
import React from 'react';
import { Link } from 'react-router-dom';
import styles from './Sidebar.module.css';

// Usamos iconos de SVG o cualquier librería de iconos como 'react-icons'
// Aquí simularemos los iconos para que puedas ver el diseño.
const MockIcon = () => (
  <div style={{ width: 20, height: 20, backgroundColor: '#333', borderRadius: 4 }}></div>
);

export default function Sidebar() {
  const menuItems = [
    { label: 'Dashboard', icon: <MockIcon />, path: '/', logo: true },
    { label: 'Resumen', icon: <MockIcon />, path: '/resumen' },
    { label: 'Alertas', icon: <MockIcon />, path: '/alertas' },
    { label: 'Fuentes y RSS', icon: <MockIcon />, path: '/fuentes' },
    {
      label: 'Notificaciones',
      icon: <MockIcon />,
      path: '/notificaciones',
      notifications: 3
    },
    { divider: true },
    { label: 'Mi perfil', icon: <MockIcon />, path: '/perfil' },
  ];

  return (
    <aside className={styles.sidebar}>
      <ul className={styles.navList}>
        {menuItems.map((item, index) => {
          if (item.divider) {
            return <hr key={index} className={styles.divider} />;
          }

          // Renderizar el logo
          if (item.logo) {
            return (
              <li key={index} className={styles.logoArea}>
                {item.icon}
                <h1 className={styles.logoText}>{item.label}</h1>
              </li>
            );
          }

          // Renderizar el resto de ítems
          return (
            <li key={index}>
              <Link to={item.path} className={styles.navItem}>
                <div className={styles.content}>
                  {/* Asegurar que el icono reciba la clase styles.icon */}
                  {React.cloneElement(item.icon, { className: styles.icon })}
                  <span className={styles.label}>{item.label}</span>
                </div>
                {item.notifications > 0 && (
                  <span className={styles.badge}>{item.notifications}</span>
                )}
              </Link>
            </li>
          );
        })}
      </ul>

      {/* Sección inferior de Cerrar Sesión */}
      <div className={styles.logoutArea}>
        <Link to="/logout" className={`${styles.navItem} ${styles.logoutItem}`}>
          <div className={styles.content}>
            <MockIcon /> {/* Icono de salir */}
            <span className={styles.label}>Cerrar sesión</span>
          </div>
        </Link>
      </div>
    </aside>
  );
}