import { useState, useContext } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { AuthContext } from '../../context/AuthContext';
import styles from './PantallaEntrada.module.css';

// Importamos los SVGs
import systemTaskSvg from './SystemTask.svg';
import newsSvg from './News.svg';
import documentarySvg from './Documentary.svg';

export default function PantallaEntrada() {
  // Estados para controlar lo que escribe el usuario y si hay errores
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState(null);
  const [isLoading, setIsLoading] = useState(false);

  // Extraemos la función login del contexto y preparamos la navegación
  const { login } = useContext(AuthContext);
  const navigate = useNavigate();

  // 4. Esta función se ejecuta al darle al botón de Iniciar Sesión
  const handleSubmit = async (e) => {
    e.preventDefault(); // Evita que la página se recargue por defecto
    setError(null);
    setIsLoading(true);

    try {
      // Llamamos a la API a través de nuestro contexto
      await login(username, password);
      
      // Si el código llega hasta aquí, el login fue un éxito. Redirigimos al Home.
      navigate('/');
    } catch (err) {
      // Si el login falla (contraseña incorrecta, servidor caído, etc.)
      setError('Credenciales incorrectas o error en el servidor. Inténtalo de nuevo.');
    } finally {
      setIsLoading(false);
    }
  };
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