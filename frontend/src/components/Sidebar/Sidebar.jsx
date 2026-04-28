import React, { useContext } from 'react';
import { Link, useLocation } from 'react-router-dom';
import { LayoutDashboard, PieChart, Bell, Rss, User, LogOut } from 'lucide-react';
import { AuthContext } from '../../context/AuthContext';
import { useTranslation } from 'react-i18next'; // <-- 1. Importamos el hook

import styles from './Sidebar.module.css';

export default function Sidebar() {
  const { t } = useTranslation(); // <-- 2. Extraemos la función t
  const location = useLocation();

  const { logout } = useContext(AuthContext);

  // 3. Traducimos directamente los labels usando t()
  const menuItems = [
    { label: t('sidebar.dashboard'), icon: <LayoutDashboard size={20} />, path: '/dashboard' },
    { label: t('sidebar.clouds'), icon: <PieChart size={20} />, path: '/nubes' },
    { label: t('sidebar.alerts'), icon: <Bell size={20} />, path: '/alerts' },
    { label: t('sidebar.sources'), icon: <Rss size={20} />, path: '/fuentes' },
    {
      label: t('sidebar.notifications'),
      icon: <Bell size={20} />,
      path: '/notificaciones',
      notifications: 3 // Este número supongo que vendrá de alguna API más adelante
    },
    { divider: true },
    { label: t('sidebar.profile'), icon: <User size={20} />, path: '/profile' },
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
        <Link
          to="/"
          onClick={logout}
          className={`${styles.navItem} ${styles.logoutItem}`}
        >
          <div className={styles.content}>
            <LogOut size={20} className={styles.icon} />
            {/* 4. Traducimos también el texto del botón de salir */}
            <span className={styles.logoutLabel}>{t('sidebar.logout')}</span>
          </div>
        </Link>
      </div>
    </aside>
  );
}