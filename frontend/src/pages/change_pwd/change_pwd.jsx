// frontend/src/pages/change_pwd/change_pwd.jsx
import React, { useState } from 'react';
import { Link, useSearchParams, useNavigate } from 'react-router-dom';

// Importamos nuestros componentes reutilizables
import Input from '../../components/input';
import Button from '../../components/button';
import HeaderNoUser from '../../components/HeaderNoUser/HeaderNoUser.jsx';

import styles from './change_pwd.module.css';

function ChangePwd() {
    const [searchParams] = useSearchParams();
    const token = searchParams.get('token');
    
    // Añadimos useNavigate para redirigir desde el modal
    const navigate = useNavigate();

    const [password, setPassword] = useState('');
    const [error, setError] = useState('');
    const [isLoading, setIsLoading] = useState(false);
    
    // NUEVO: Estado para el modal de éxito
    const [showSuccess, setShowSuccess] = useState(false);

    const handleSubmit = async (e) => {
        e.preventDefault();
        setError('');

        if (!token) {
            setError('Enlace no válido o expirado. Por favor, solicita un nuevo correo de recuperación.');
            return;
        }

        if (!password || password.length < 6) {
            setError('La contraseña debe tener al menos 6 caracteres.');
            return;
        }

        setIsLoading(true);

        try {
            const response = await fetch('http://localhost:8000/api/v1/auth/reset-password', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    token: token,
                    new_password: password
                }),
            });

            const data = await response.json();

            if (response.ok) {
                // Éxito: Mostramos el modal y limpiamos el input
                setShowSuccess(true);
                setPassword('');
            } else {
                setError(data.detail || 'Ocurrió un error al procesar tu solicitud.');
            }
        } catch (err) {
            setError('No se pudo conectar con el servidor. Inténtalo de nuevo más tarde.');
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <div className={styles.pageContainer}>
            <HeaderNoUser />

            <main className={styles.mainContent}>
                <div className={styles.pwdCard}>

                    {/* Sección 1: Cabecera oscura */}
                    <div className={styles.darkHeader}>
                        <h1 className={styles.titleText}>RESTABLECE TU CONTRASEÑA</h1>
                        <p className={styles.subtitleText}>
                            Crea una contraseña que tenga al menos 6 letras y números. <br />
                            La necesitarás para iniciar sesión.
                        </p>
                    </div>

                    {/* Sección 2: Formulario de la tarjeta */}
                    <div className={styles.lightForm}>
                        <form className={styles.formElement} onSubmit={handleSubmit}>

                            <Input
                                label="CONTRASEÑA NUEVA"
                                type="password"
                                id="password"
                                value={password}
                                onChange={(e) => setPassword(e.target.value)}
                                className={styles.formInput}
                                labelClassName={styles.formLabel}
                                required
                            />

                            {/* Mensajes de error visual */}
                            {error && (
                                <p style={{ color: '#d93025', textAlign: 'center', fontSize: '14px', marginBottom: '10px', marginTop: '20px' }}>
                                    {error}
                                </p>
                            )}

                            {/* BOTÓN CONTINUAR */}
                            <Button
                                type="submit"
                                className={styles.continueButton}
                                disabled={isLoading}
                                style={{ marginTop: '35px' }}
                            >
                                {isLoading ? 'GUARDANDO...' : 'CONTINUAR'}
                            </Button>

                        </form>

                        <div className={styles.pwdFooter}>
                            <p className={styles.footerText}>¿Te acuerdas de la contraseña?</p>
                            <Link className={styles.loginButton} to="/">
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
                        <h2 className={styles.modalTitle}>¡Contraseña Restablecida!</h2>
                        <p className={styles.modalText}>
                            Tu contraseña ha sido cambiada correctamente. Ya puedes iniciar sesión con tu nueva clave.
                        </p>
                        <Button 
                            className={styles.modalButton} 
                            onClick={() => navigate('/')}
                        >
                            Ir a iniciar sesión
                        </Button>
                    </div>
                </div>
            )}

        </div>
    );
}

export default ChangePwd;