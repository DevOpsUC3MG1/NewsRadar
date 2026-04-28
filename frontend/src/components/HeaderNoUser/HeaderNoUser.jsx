import React from 'react';
import { Link } from 'react-router-dom';
import { Globe } from 'lucide-react';
import { useTranslation } from 'react-i18next';
import styles from './HeaderNoUser.module.css';

export default function HeaderNoUser() {
  const { i18n } = useTranslation();

  // Detectamos el idioma actual con seguridad
  const currentLang = i18n.language?.startsWith('en') ? 'en' : 'es';

  const toggleLanguage = () => {
    const newLang = currentLang === 'es' ? 'en' : 'es';
    i18n.changeLanguage(newLang);
  };

  return (
    <header className={styles.header}>
      <Link to="/" className={styles.logoSection} style={{ textDecoration: 'none', color: 'inherit' }}>
        <img src="/newsradar-icon.svg" alt="NewsRadar Logo" className={styles.logoIcon} />
        <span className={styles.logoText}>NEWSRADAR</span>
      </Link>

      <div className={styles.rightSection}>
        <button onClick={toggleLanguage} className={styles.langBtn}>
          <Globe size={18} />
          <span>{currentLang.toUpperCase()}</span>
        </button>
      </div>
    </header>
  );
}