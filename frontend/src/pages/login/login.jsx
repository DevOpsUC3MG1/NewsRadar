// login.jsx
import { useState, useContext } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { AuthContext } from '../../context/AuthContext';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import * as z from 'zod';

// Importamos el Header sin usuario
import HeaderNoUser from '../../components/HeaderNoUser/HeaderNoUser.jsx';
import styles from './login.module.css';

// Importamos la ÚNICA imagen SVG agrupada
import imgInicioSvg from './img-inicio.svg';

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
  const [apiError, setApiError] = useState(null);
  const [isLoading, setIsLoading] = useState(false);

  // Traemos la nueva función login que hemos creado en AuthContext
  const { login } = useContext(AuthContext);
  const navigate = useNavigate();

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm({
    resolver: zodResolver(loginSchema),
  });

  const onSubmitForm = async (data) => {
    setApiError(null);
    setIsLoading(true);

    try {
      // Enviamos email y password al AuthContext
      await login(data.email, data.password);
      
      // Si llega aquí sin dar error, el usuario y el token ya están guardados
      navigate('/app'); 
    } catch (err) {
      console.error(err);
      setApiError('Credenciales incorrectas o error en el servidor. Inténtalo de nuevo.');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className={styles.container}>
      <HeaderNoUser />

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

          <div className={styles.imageContainer}>
            <img src={imgInicioSvg} alt="Ilustración de monitorización" className={styles.mainImage} />
          </div>
        </div>

        {/* --- Mitad Derecha --- */}
        <div className={styles.rightPanel}>
          <div className={styles.rightPanelHeader}>
            <h2 className={styles.welcomeTitle}>BIENVENIDO</h2>
            <p className={styles.welcomeSubtitle}>INICIE SESIÓN Y ACCEDA AL CONTENIDO</p>
          </div>

          <div className={styles.formContainer}>
            <form onSubmit={handleSubmit(onSubmitForm)}>
              {/* CAMPO EMAIL */}
              <div className={styles.formGroup}>
                <label className={styles.label}>EMAIL</label>
                <input
                  type="email"
                  className={styles.input}
                  {...register('email')}
                />
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
                  {...register('password')}
                />
                {errors.password && (
                  <span style={{ color: '#e74c3c', fontSize: '0.8rem', marginTop: '5px' }}>
                    {errors.password.message}
                  </span>
                )}
              </div>

              {apiError && (
                <div style={{ color: '#e74c3c', fontSize: '0.85rem', marginBottom: '15px', textAlign: 'center' }}>
                  {apiError}
                </div>
              )}

              <button
                type="submit"
                className={styles.loginButton}
                disabled={isLoading}
              >
                {isLoading ? 'CARGANDO...' : 'INICIAR SESIÓN'}
              </button>

              {/* AQUÍ ESTÁ EL CAMBIO CLAVE: Usamos Link en lugar de a */}
              <Link to="/recuperar-password" className={styles.forgotPassword}>
                ¿OLVIDASTE TU CONTRASEÑA?
              </Link>
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