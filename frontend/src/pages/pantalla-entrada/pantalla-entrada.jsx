import { Link } from 'react-router-dom';
import styles from './PantallaEntrada.module.css';

// Importamos los SVGs
import systemTaskSvg from './SystemTask.svg';
import newsSvg from './News.svg';
import documentarySvg from './Documentary.svg';

export default function PantallaEntrada() {
  return (
    <div className={styles.container}>
      {/* Barra superior */}
      <header className={styles.topbar}>
        <span className={styles.topbarLogo}>◪</span> NEWSRADAR
      </header>

      {/* Cuerpo principal */}
      <div className={styles.splitLayout}>

        {/* Mitad Izquierda */}
        <div className={styles.leftPanel}>
          <div className={styles.brandArea}>
            <span style={{ fontSize: '3rem', color: '#4b6a9b' }}>◪</span>
            <h1 className={styles.mainLogo}>NEWSRADAR</h1>
          </div>

          <p className={styles.subtitle}>
            Sistema de monitorización<br/>
            de noticias en medios<br/>
            de comunicación y fuentes oficiales
          </p>

          <div className={styles.imageCluster}>
            <img src={systemTaskSvg} alt="Monitor" className={styles.imgTask} />
            <img src={newsSvg} alt="Periódico" className={styles.imgNews} />
            <img src={documentarySvg} alt="Cámara" className={styles.imgDoc} />
          </div>
        </div>

        {/* Mitad Derecha */}
        <div className={styles.rightPanel}>
          <div className={styles.rightPanelHeader}>
            <h2 className={styles.welcomeTitle}>BIENVENIDO</h2>
            <p className={styles.welcomeSubtitle}>INICIE SESIÓN Y ACCEDA AL CONTENIDO</p>
          </div>

          <div className={styles.formContainer}>
            <form onSubmit={(e) => e.preventDefault()}>
              <div className={styles.formGroup}>
                <label className={styles.label}>EMAIL</label>
                <input type="email" className={styles.input} />
              </div>

              <div className={styles.formGroup}>
                <label className={styles.label}>CONTRASEÑA</label>
                <input type="password" className={styles.input} />
              </div>

              {/* Botón de inicio que de momento redirige al Home (Dashboard) */}
              <Link to="/">
                <button type="button" className={styles.loginButton}>
                  INICIAR SESIÓN
                </button>
              </Link>

              <a href="#" className={styles.forgotPassword}>
                ¿OLVIDASTE TU CONTRASEÑA?
              </a>
            </form>

            <div>
              <p className={styles.footerText}>¿No tienes cuenta? Regístrate aquí</p>
              <Link to="/registro" className={styles.registerButton}>
                Crear una cuenta nueva
              </Link>
            </div>
          </div>
        </div>

      </div>
    </div>
  );
}