import React from 'react';
import { User, Globe } from 'lucide-react';
import { Link } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import styles from './Header.module.css';

export default function Header() {
  const { i18n } = useTranslation();

  // Detectamos el idioma actual con seguridad
  const currentLang = i18n.language?.startsWith('en') ? 'en' : 'es';

  const toggleLanguage = () => {
    const newLang = currentLang === 'es' ? 'en' : 'es';
    i18n.changeLanguage(newLang);
  };

  return (
    <header className={styles.header}>

      {/* Sección Izquierda: Logo y Título */}
      <Link
        to="/dashboard"
        className={styles.logoSection}
        style={{ textDecoration: 'none', color: 'inherit' }}
      >
        <img src="/newsradar-icon.svg" alt="NewsRadar Logo" className={styles.logoIcon} />
        <span className={styles.logoText}>NEWSRADAR</span>
      </Link>

      {/* Sección Derecha: Idioma y Perfil */}
      <div className={styles.rightSection}>

        <button onClick={toggleLanguage} className={styles.langBtn}>
          <Globe size={18} />
          <span>{currentLang.toUpperCase()}</span>
        </button>

        {/* El circulito del usuario */}
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