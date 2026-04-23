import React, { useContext } from 'react'; // 1. Importamos useContext
import { Link, useLocation } from 'react-router-dom';
import { LayoutDashboard, PieChart, Bell, Rss, User, LogOut } from 'lucide-react';
// 2. Importamos tu AuthContext (asegúrate de que la ruta sea la correcta)
import { AuthContext } from '../../context/AuthContext';
import styles from './Sidebar.module.css';

export default function Sidebar() {
  const location = useLocation();

  // 3. Extraemos la función logout de tu compañero
  const { logout } = useContext(AuthContext);

  const menuItems = [
    { label: 'Dashboard', icon: <LayoutDashboard size={20} />, path: '/dashboard' },
    { label: 'Resumen', icon: <PieChart size={20} />, path: '/resumen' },
    { label: 'Alertas', icon: <Bell size={20} />, path: '/alertas' },
    { label: 'Fuentes y RSS', icon: <Rss size={20} />, path: '/fuentes' },
    {
      label: 'Notificaciones',
      icon: <Bell size={20} />,
      path: '/notificaciones',
      notifications: 3
    },
    { divider: true },
    { label: 'Mi perfil', icon: <User size={20} />, path: '/profile' },
  ];

  return (
    <aside className={styles.sidebar}>
      <ul className={styles.navList}>
        {menuItems.map((item, index) => {
          if (item.divider) {
            return <hr key={index} className={styles.divider} />;
          }

          const isActive = location.pathname === item.path;

          return (
            <li key={index}>
              <Link
                to={item.path}
                className={`${styles.navItem} ${isActive ? styles.active : ''}`}
              >
                <div className={styles.content}>
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
        {/* 4. Añadimos el evento onClick para ejecutar la función antes de navegar */}
        <Link
          to="/"
          onClick={logout}
          className={`${styles.navItem} ${styles.logoutItem}`}
        >
          <div className={styles.content}>
            <LogOut size={20} className={styles.icon} />
            <span className={styles.logoutLabel}>Cerrar sesión</span>
          </div>
        </Link>
      </div>
    </aside>
  );
}