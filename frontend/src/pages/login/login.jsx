// login.jsx
import { useState, useContext } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { AuthContext } from '../../context/AuthContext';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import * as z from 'zod';
import { useTranslation } from 'react-i18next';

// Componentes reutilizables
import Input from '../../components/input';
import Button from '../../components/button';
import HeaderNoUser from '../../components/HeaderNoUser/HeaderNoUser.jsx';

// Estilos e imágenes
import styles from './login.module.css';
import imgInicioSvg from './img-inicio.svg';

// 1. Volvemos a poner el esquema fuera, pero en vez del texto, le pasamos la CLAVE del JSON
const loginSchema = z.object({
  email: z
    .string()
    .min(1, 'login.errors.emailRequired')
    .email('login.errors.emailInvalid'),
  password: z
    .string()
    .min(6, 'login.errors.passwordMin'),
});

export default function PantallaEntrada() {
  const { t } = useTranslation();
  const [apiError, setApiError] = useState(null);
  const [isLoading, setIsLoading] = useState(false);

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
      await login(data.email, data.password);
      navigate('/dashboard');
    } catch (err) {
      console.error(err);
      // 2. Aquí también guardamos solo la clave en lugar del texto ya traducido
      setApiError('login.errors.apiError');
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
            {t('login.subtitleLine1')}<br />
            {t('login.subtitleLine2')}<br />
            {t('login.subtitleLine3')}
          </p>

          <div className={styles.imageContainer}>
            <img src={imgInicioSvg} alt={t('login.altImage')} className={styles.mainImage} />
          </div>
        </div>

        {/* --- Mitad Derecha --- */}
        <div className={styles.rightPanel}>
          <div className={styles.rightPanelHeader}>
            <h2 className={styles.welcomeTitle}>{t('login.welcome')}</h2>
            <p className={styles.welcomeSubtitle}>{t('login.welcomeSubtitle')}</p>
          </div>

          <div className={styles.formContainer}>
            <form onSubmit={handleSubmit(onSubmitForm)}>

              <Input
                label={t('login.emailLabel')}
                type="email"
                className={styles.input}
                labelClassName={styles.label}
                // 3. Traducimos el error justo al pasárselo al Input
                error={errors.email?.message ? t(errors.email.message) : undefined}
                {...register('email')}
              />

              <Input
                label={t('login.passwordLabel')}
                type="password"
                className={styles.input}
                labelClassName={styles.label}
                // Traducimos el error al vuelo
                error={errors.password?.message ? t(errors.password.message) : undefined}
                {...register('password')}
              />

              {/* Traducimos el error de la API al vuelo también */}
              {apiError && (
                <div style={{ color: '#e74c3c', fontSize: '0.85rem', marginBottom: '15px', textAlign: 'center' }}>
                  {t(apiError)}
                </div>
              )}

              <Button
                type="submit"
                className={styles.loginButton}
                disabled={isLoading}
              >
                {isLoading ? t('login.loadingBtn') : t('login.loginBtn')}
              </Button>

              <Link to="/recuperar-password" className={styles.forgotPassword}>
                {t('login.forgotPassword')}
              </Link>
            </form>

            <div>
              <p className={styles.footerText}>{t('login.noAccount')}</p>
              <Link to="/registro" className={styles.registerButton}>
                {t('login.registerBtn')}
              </Link>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}