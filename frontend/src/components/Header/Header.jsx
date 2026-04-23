import React from 'react';
import { Search, User } from 'lucide-react';
import { Link } from 'react-router-dom'; // <-- 1. Importamos Link
import styles from './Header.module.css';

export default function Header() {
  return (
    <header className={styles.header}>

      {/* Sección Izquierda: Logo y Título */}
      <Link
        to="/app"
        className={styles.logoSection}
        style={{ textDecoration: 'none', color: 'inherit' }} // Evita que se subraye o cambie de color
      >
        <img src="/newsradar-icon.svg" alt="NewsRadar Logo" className={styles.logoIcon} />
        <span className={styles.logoText}>NEWSRADAR</span>
      </Link>

      {/* Sección Derecha: Buscador y Perfil */}
      <div className={styles.rightSection}>
        <div className={styles.searchBar}>
          <Search size={18} className={styles.searchIcon} />
          <input
            type="text"
            placeholder="Buscar noticia..."
            className={styles.searchInput}
          />
        </div>

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