import { useState, useContext } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import * as z from 'zod';
import { AuthContext } from '../../context/AuthContext';

// Importamos nuestros componentes reutilizables
import Input from '../../components/input';
import Button from '../../components/button';
import HeaderNoUser from '../../components/HeaderNoUser/HeaderNoUser.jsx';

import styles from './registro.module.css';

const registerSchema = z.object({
  nombre: z.string().min(1, 'El nombre es obligatorio'),
  apellidos: z.string().min(1, 'Los apellidos son obligatorios'),
  organizacion: z.string().min(1, 'La organización es obligatoria'),
  email: z.string().min(1, 'El email es obligatorio').email('Formato de correo no válido'),
  password: z.string().min(6, 'Debe tener al menos 6 caracteres'),
  confirmPassword: z.string().min(1, 'Debes confirmar la contraseña'),
}).refine((data) => data.password === data.confirmPassword, {
  message: "Las contraseñas no coinciden",
  path: ["confirmPassword"], 
});

export default function Registro() {
  const [isLoading, setIsLoading] = useState(false);
  const [apiError, setApiError] = useState(null);
  
  // NUEVO: Estado para controlar si mostramos la ventana de éxito
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
        role_ids: [] 
      };

      await registerUser(apiPayload);
      
      // En lugar de navegar de golpe, mostramos la ventana emergente
      setShowSuccess(true);
      
    } catch (err) {
      if (err.response && err.response.status === 409) {
        setApiError('El email ya está registrado.');
      } else {
        setApiError('Error al crear la cuenta. Inténtalo de nuevo.');
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
            <h1 className={styles.title}>CREA TU CUENTA</h1>
            <p className={styles.subtitle}>Regístrate para acceder a NEWSRADAR</p>
          </div>

          <div className={styles.cardBody}>
            <form onSubmit={handleSubmit(onSubmitForm)}>
              
              <div className={styles.gridRow}>
                <Input
                  label="NOMBRE"
                  className={styles.input}
                  labelClassName={styles.label}
                  error={errors.nombre?.message}
                  {...register('nombre')}
                />
                
                <Input
                  label="APELLIDOS"
                  className={styles.input}
                  labelClassName={styles.label}
                  error={errors.apellidos?.message}
                  {...register('apellidos')}
                />
              </div>

              <Input
                label="ORGANIZACIÓN"
                className={styles.input}
                labelClassName={styles.label}
                error={errors.organizacion?.message}
                {...register('organizacion')}
              />

              <Input
                label="EMAIL"
                type="email"
                className={styles.input}
                labelClassName={styles.label}
                error={errors.email?.message}
                {...register('email')}
              />

              <div className={styles.gridRow}>
                <Input
                  label="CONTRASEÑA"
                  type="password"
                  className={styles.input}
                  labelClassName={styles.label}
                  error={errors.password?.message}
                  {...register('password')}
                />
                
                <Input
                  label="CONFIRMAR CONTRASEÑA"
                  type="password"
                  className={styles.input}
                  labelClassName={styles.label}
                  error={errors.confirmPassword?.message}
                  {...register('confirmPassword')}
                />
              </div>

              {apiError && (
                <div style={{ color: '#e74c3c', fontSize: '0.85rem', textAlign: 'center', marginTop: '10px' }}>
                  {apiError}
                </div>
              )}

              <Button 
                type="submit" 
                className={styles.submitButton} 
                disabled={isLoading}
              >
                {isLoading ? 'CREANDO...' : 'CREAR CUENTA'}
              </Button>

            </form>

            <div className={styles.footerSection}>
              <p className={styles.footerText}>¿Ya tienes cuenta?</p>
              <Link to="/" className={styles.loginButton}>
                Iniciar sesión
              </Link>
            </div>

          </div>
        </div>
      </main>

      {/* NUEVO: Ventana emergente (Modal) de éxito */}
      {showSuccess && (
        <div className={styles.modalOverlay}>
          <div className={styles.modalContent}>
            <div className={styles.successIcon}>✓</div>
            <h2 className={styles.modalTitle}>¡Registro Completado!</h2>
            <p className={styles.modalText}>
              Tu cuenta ha sido creada correctamente. Ya puedes iniciar sesión en Newsradar para comenzar.
            </p>
            <Button 
              className={styles.modalButton} 
              onClick={() => navigate('/')}
            >
              IR A INICIAR SESIÓN
            </Button>
          </div>
        </div>
      )}
      
    </div>
  );
}