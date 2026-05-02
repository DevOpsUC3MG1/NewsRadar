import { useState, useContext } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import * as z from 'zod';
import { AuthContext } from '../../context/AuthContext';
import { useTranslation } from 'react-i18next'; // <-- Importamos el hook

// Importamos nuestros componentes reutilizables
import Input from '../../components/input';
import Button from '../../components/button';
import HeaderNoUser from '../../components/HeaderNoUser/HeaderNoUser.jsx';

import styles from './registro.module.css';

// Esquema Zod con claves de traducción en lugar de textos quemados
const registerSchema = z.object({
  nombre: z.string().min(1, 'register.errors.nameRequired'),
  apellidos: z.string().min(1, 'register.errors.lastNameRequired'),
  organizacion: z.string().min(1, 'register.errors.orgRequired'),
  email: z.string().min(1, 'register.errors.emailRequired').email('register.errors.emailInvalid'),
  password: z.string().min(6, 'register.errors.passwordMin'),
  confirmPassword: z.string().min(1, 'register.errors.confirmRequired'),
}).refine((data) => data.password === data.confirmPassword, {
  message: 'register.errors.passwordsMismatch',
  path: ['confirmPassword'],
});

export default function Registro() {
  const { t } = useTranslation(); // <-- Extraemos la función t
  const [isLoading, setIsLoading] = useState(false);
  const [apiError, setApiError] = useState(null);

  const [showSuccess, setShowSuccess] = useState(false);

  const navigate = useNavigate();
  const { registerUser } = useContext(AuthContext);

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm({
    resolver: zodResolver(registerSchema),
    mode: 'onTouched',
  });

  const onSubmitForm = async (data) => {
    setApiError(null);
    setIsLoading(true);

    try {
      const apiPayload = {
        email: data.email,
        first_name: data.nombre,
        last_name: data.apellidos,
        organization: data.organizacion,
        password: data.password,
        role_ids: [4]
      };

      await registerUser(apiPayload);

      setShowSuccess(true);

    } catch (err) {
      if (err.response && err.response.status === 409) {
        setApiError('register.errors.emailExists'); // Guardamos la clave
      } else {
        setApiError('register.errors.apiError'); // Guardamos la clave
      }
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className={styles.pageContainer}>
      <HeaderNoUser />
      <main className={styles.mainContent}>
        <div className={styles.formCard}>

          <div className={styles.cardHeader}>
            <h1 className={styles.title}>{t('register.title')}</h1>
            <p className={styles.subtitle}>{t('register.subtitle')}</p>
          </div>

          <div className={styles.cardBody}>
            <form onSubmit={handleSubmit(onSubmitForm)}>

              <div className={styles.gridRow}>
                <Input
                  label={t('register.nameLabel')}
                  className={styles.input}
                  labelClassName={styles.label}
                  error={errors.nombre?.message ? t(errors.nombre.message) : undefined}
                  {...register('nombre')}
                />

                <Input
                  label={t('register.lastNameLabel')}
                  className={styles.input}
                  labelClassName={styles.label}
                  error={errors.apellidos?.message ? t(errors.apellidos.message) : undefined}
                  {...register('apellidos')}
                />
              </div>

              <Input
                label={t('register.orgLabel')}
                className={styles.input}
                labelClassName={styles.label}
                error={errors.organizacion?.message ? t(errors.organizacion.message) : undefined}
                {...register('organizacion')}
              />

              <Input
                label={t('register.emailLabel')}
                type="email"
                className={styles.input}
                labelClassName={styles.label}
                error={errors.email?.message ? t(errors.email.message) : undefined}
                {...register('email')}
              />

              <div className={styles.gridRow}>
                <Input
                  label={t('register.passwordLabel')}
                  type="password"
                  className={styles.input}
                  labelClassName={styles.label}
                  error={errors.password?.message ? t(errors.password.message) : undefined}
                  {...register('password')}
                />

                <Input
                  label={t('register.confirmPasswordLabel')}
                  type="password"
                  className={styles.input}
                  labelClassName={styles.label}
                  error={errors.confirmPassword?.message ? t(errors.confirmPassword.message) : undefined}
                  {...register('confirmPassword')}
                />
              </div>

              {apiError && (
                <div style={{ color: '#e74c3c', fontSize: '0.85rem', textAlign: 'center', margin: '10px 0' }}>
                  {t(apiError)}
                </div>
              )}

              <Button
                type="submit"
                className={styles.submitButton}
                disabled={isLoading}
              >
                {isLoading ? t('register.loadingBtn') : t('register.submitBtn')}
              </Button>

            </form>

            <div className={styles.footerSection}>
              <p className={styles.footerText}>{t('register.hasAccount')}</p>
              <Link to="/" className={styles.loginButton}>
                {t('register.loginLink')}
              </Link>
            </div>

          </div>
        </div>
      </main>

      {/* Ventana emergente (Modal) de éxito */}
      {showSuccess && (
        <div className={styles.modalOverlay}>
          <div className={styles.modalContent}>
            <div className={styles.successIcon}>✓</div>
            <h2 className={styles.modalTitle}>{t('register.modal.title')}</h2>
            <p className={styles.modalText}>
              {t('register.modal.text')}
            </p>
            <Button
              className={styles.modalButton}
              onClick={() => navigate('/')}
            >
              {t('register.modal.button')}
            </Button>
          </div>
        </div>
      )}
      
    </div>
  );
}