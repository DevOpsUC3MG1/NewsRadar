import React from 'react';
import { Search, User } from 'lucide-react';
import styles from './Header.module.css';

export default function Header() {
  return (
    <header className={styles.header}>
      {/* Sección Izquierda: Logo y Título */}
      <div className={styles.logoSection}>
        {/* En React, la carpeta 'public' se referencia con '/' directamente */}
        <img src="/newsradar-icon.svg" alt="NewsRadar Logo" className={styles.logoIcon} />
        <span className={styles.logoText}>NEWSRADAR</span>
      </div>

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

        {/* El circulito del usuario (opcional, extraído de tu imagen) */}
        <div className={styles.userProfile}>
          <User size={20} color="#FFFFFF" />
        </div>
      </div>
    </header>
  );
}