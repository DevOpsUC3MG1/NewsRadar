import { Link } from 'react-router-dom';
import styles from './HeaderNoUser.module.css';

export default function HeaderNoUser() {
  return (
    <header className={styles.header}>
      {/* Usamos Link para que el logo sea clickeable */}
      <Link to="/" className={styles.logoSection}>
        {/* Si prefieres usar tu SVG del icono, cambia el <span> por tu <img src="/newsradar-icon.svg" /> */}
        <img src="/newsradar-icon.svg" alt="NewsRadar Logo" className={styles.logoIcon} />
        <span className={styles.logoText}>NEWSRADAR</span>
      </Link>
    </header>
  );
}