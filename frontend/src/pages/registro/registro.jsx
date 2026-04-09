import { useState, useContext } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import * as z from 'zod';
import { AuthContext } from '../../context/AuthContext';

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
  const navigate = useNavigate();
  
  const { registerUser } = useContext(AuthContext);

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm({
    resolver: zodResolver(registerSchema),
  });

  const onSubmitForm = async (data) => {
    setApiError(null);
    setIsLoading(true);

    try {
      // Adaptado exactamente a UserCreate de main.py
      const apiPayload = {
        email: data.email,
        first_name: data.nombre, 
        last_name: data.apellidos, 
        organization: data.organizacion,
        password: data.password,
        role_ids: [] 
      };

      // Esto registra y hace auto-login
      await registerUser(apiPayload);
      
      // Ya está logueado, lo mandamos al panel principal (cambia la ruta si es distinta)
      navigate('/dashboard'); 
      
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
              
              {/* --- RESTO DE TU CÓDIGO HTML/JSX (No cambia nada) --- */}
              <div className={styles.gridRow}>
                <div className={styles.formGroup}>
                  <label className={styles.label}>NOMBRE</label>
                  <input type="text" className={styles.input} {...register('nombre')} />
                  {errors.nombre && <span className={styles.errorText}>{errors.nombre.message}</span>}
                </div>
                <div className={styles.formGroup}>
                  <label className={styles.label}>APELLIDOS</label>
                  <input type="text" className={styles.input} {...register('apellidos')} />
                  {errors.apellidos && <span className={styles.errorText}>{errors.apellidos.message}</span>}
                </div>
              </div>

              <div className={styles.formGroup}>
                <label className={styles.label}>ORGANIZACIÓN</label>
                <input type="text" className={styles.input} {...register('organizacion')} />
                {errors.organizacion && <span className={styles.errorText}>{errors.organizacion.message}</span>}
              </div>

              <div className={styles.formGroup}>
                <label className={styles.label}>EMAIL</label>
                <input type="email" className={styles.input} {...register('email')} />
                {errors.email && <span className={styles.errorText}>{errors.email.message}</span>}
              </div>

              <div className={styles.gridRow}>
                <div className={styles.formGroup}>
                  <label className={styles.label}>CONTRASEÑA</label>
                  <input type="password" className={styles.input} {...register('password')} />
                  {errors.password && <span className={styles.errorText}>{errors.password.message}</span>}
                </div>
                <div className={styles.formGroup}>
                  <label className={styles.label}>CONFIRMAR CONTRASEÑA</label>
                  <input type="password" className={styles.input} {...register('confirmPassword')} />
                  {errors.confirmPassword && <span className={styles.errorText}>{errors.confirmPassword.message}</span>}
                </div>
              </div>

              {apiError && (
                <div style={{ color: '#e74c3c', fontSize: '0.85rem', textAlign: 'center', marginTop: '10px' }}>
                  {apiError}
                </div>
              )}

              <button type="submit" className={styles.submitButton} disabled={isLoading}>
                {isLoading ? 'CREANDO...' : 'CREAR CUENTA'}
              </button>

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
    </div>
  );
}