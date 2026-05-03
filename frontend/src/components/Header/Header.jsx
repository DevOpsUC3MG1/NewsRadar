// Header.jsx
import React from 'react';
import { User, Globe, Menu } from 'lucide-react';
import { Link } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import styles from './Header.module.css';

export default function Header({ onMenuToggle }) {
  const { i18n } = useTranslation();

  const currentLang = i18n.language?.startsWith('en') ? 'en' : 'es';

  const toggleLanguage = () => {
    const newLang = currentLang === 'es' ? 'en' : 'es';
    i18n.changeLanguage(newLang);
  };

  return (
    <header className={styles.header}>

      {/* Sección Izquierda: Hamburguesa (solo móvil/tablet) + Logo */}
      <div className={styles.leftSection}>
        <button
          className={styles.hamburger}
          onClick={onMenuToggle}
          aria-label="Abrir menú"
        >
          <Menu size={22} color="#FFFFFF" />
        </button>

        <Link
          to="/dashboard"
          className={styles.logoSection}
          style={{ textDecoration: 'none', color: 'inherit' }}
        >
          <img src="/newsradar-icon.svg" alt="NewsRadar Logo" className={styles.logoIcon} />
          <span className={styles.logoText}>NEWSRADAR</span>
        </Link>
      </div>

      {/* Sección Derecha: Idioma y Perfil */}
      <div className={styles.rightSection}>
        <button onClick={toggleLanguage} className={styles.langBtn}>
          <Globe size={18} />
          <span>{currentLang.toUpperCase()}</span>
        </button>

        <Link
          to="/profile"
          className={styles.userProfile}
          style={{ textDecoration: 'none' }}
        >
          <User size={20} color="#FFFFFF" />
        </Link>
      </div>
    </header>
  );
}