import { useState, useContext } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { AuthContext } from '../../context/AuthContext';
// Importamos las nuevas herramientas
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import * as z from 'zod';

import styles from './login.module.css';

// Importamos los SVGs
import systemTaskSvg from './SystemTask.svg';
import newsSvg from './News.svg';
import documentarySvg from './Documentary.svg';

// 1. EL "GORILA": Definimos las reglas de validación con Zod
const loginSchema = z.object({
  email: z
    .string()
    .min(1, 'El email es obligatorio')
    .email('Debe ser un formato de correo válido'),
  password: z
    .string()
    .min(6, 'La contraseña debe tener al menos 6 caracteres'),
});

export default function PantallaEntrada() {
  // Solo dejamos los estados que NO son del formulario
  const [apiError, setApiError] = useState(null);
  const [isLoading, setIsLoading] = useState(false);

  const { login } = useContext(AuthContext);
  const navigate = useNavigate();

  // 2. EL "ASISTENTE": Configuramos React Hook Form
  const {
    register, // Para "conectar" los inputs
    handleSubmit, // Para manejar el envío
    formState: { errors }, // Para leer los errores que Zod detecte
  } = useForm({
    resolver: zodResolver(loginSchema),
  });

  // 3. Esta función SOLO se ejecuta si Zod dice que todo está correcto
  const onSubmitForm = async (data) => {
    setApiError(null);
    setIsLoading(true);

    try {
      // Pasamos los datos validados a la API
      await login(data.email, data.password);
      // Redirigimos al Dashboard
      navigate('/app');
    } catch (err) {
      setApiError('Credenciales incorrectas o error en el servidor. Inténtalo de nuevo.');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className={styles.container}>
      <header className={styles.topbar}>
        <span className={styles.topbarLogo}>◪</span> NEWSRADAR
      </header>

      <div className={styles.splitLayout}>
        {/* --- Mitad Izquierda --- */}
        <div className={styles.leftPanel}>
          <div className={styles.brandArea}>
            <span style={{ fontSize: '3rem', color: '#4b6a9b' }}>◪</span>
            <h1 className={styles.mainLogo}>NEWSRADAR</h1>
          </div>

          <p className={styles.subtitle}>
            Sistema de monitorización<br />
            de noticias en medios<br />
            de comunicación y fuentes oficiales
          </p>

          <div className={styles.imageCluster}>
            <img src={systemTaskSvg} alt="Monitor" className={styles.imgTask} />
            <img src={newsSvg} alt="Periódico" className={styles.imgNews} />
            <img src={documentarySvg} alt="Cámara" className={styles.imgDoc} />
          </div>
        </div>

        {/* --- Mitad Derecha --- */}
        <div className={styles.rightPanel}>
          <div className={styles.rightPanelHeader}>
            <h2 className={styles.welcomeTitle}>BIENVENIDO</h2>
            <p className={styles.welcomeSubtitle}>INICIE SESIÓN Y ACCEDA AL CONTENIDO</p>
          </div>

          <div className={styles.formContainer}>
            {/* Conectamos el form con handleSubmit de React Hook Form */}
            <form onSubmit={handleSubmit(onSubmitForm)}>

              {/* CAMPO EMAIL */}
              <div className={styles.formGroup}>
                <label className={styles.label}>EMAIL</label>
                <input
                  type="email"
                  className={styles.input}
                  {...register('email')} // Conectamos el input
                />
                {/* Mostramos el error si Zod lo detecta */}
                {errors.email && (
                  <span style={{ color: '#e74c3c', fontSize: '0.8rem', marginTop: '5px' }}>
                    {errors.email.message}
                  </span>
                )}
              </div>

              {/* CAMPO CONTRASEÑA */}
              <div className={styles.formGroup}>
                <label className={styles.label}>CONTRASEÑA</label>
                <input
                  type="password"
                  className={styles.input}
                  {...register('password')} // Conectamos el input
                />
                {/* Mostramos el error si Zod lo detecta */}
                {errors.password && (
                  <span style={{ color: '#e74c3c', fontSize: '0.8rem', marginTop: '5px' }}>
                    {errors.password.message}
                  </span>
                )}
              </div>

              {/* Mostrar errores que vienen del backend (ej. contraseña mal) */}
              {apiError && (
                <div style={{ color: '#e74c3c', fontSize: '0.85rem', marginBottom: '15px', textAlign: 'center' }}>
                  {apiError}
                </div>
              )}

              {/* Botón de envío. Ahora es type="submit" y sin <Link> */}
              <button
                type="submit"
                className={styles.loginButton}
                disabled={isLoading}
              >
                {isLoading ? 'CARGANDO...' : 'INICIAR SESIÓN'}
              </button>

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