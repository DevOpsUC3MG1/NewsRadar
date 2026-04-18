// frontend/src/pages/change_pwd/change_pwd.jsx
import React, { useState } from 'react';
import { Link, useSearchParams } from 'react-router-dom';

// Importamos nuestros componentes reutilizables
import Input from '../../components/input';
import Button from '../../components/button';
import HeaderNoUser from '../../components/HeaderNoUser/HeaderNoUser.jsx';

import styles from './change_pwd.module.css';

function ChangePwd() {
    // 2. Usamos useSearchParams para atrapar el '?token=...'
    const [searchParams] = useSearchParams();
    const token = searchParams.get('token');

    // 2. Estados para manejar los datos y la interfaz
    const [password, setPassword] = useState('');
    const [message, setMessage] = useState('');
    const [error, setError] = useState('');
    const [isLoading, setIsLoading] = useState(false);

    // 3. Función que se ejecuta al hacer clic en "Continuar"
    const handleSubmit = async (e) => {
        e.preventDefault();

        // Limpiamos mensajes anteriores
        setMessage('');
        setError('');

        // Verificamos que tenemos el token (por si el usuario entra a la ruta a mano sin un enlace válido)
        if (!token) {
            setError('Enlace no válido o expirado. Por favor, solicita un nuevo correo de recuperación.');
            return;
        }

        // Validación básica de la contraseña
        if (!password || password.length < 6) {
            setError('La contraseña debe tener al menos 6 caracteres.');
            return;
        }

        setIsLoading(true);

        try {
            // Hacemos la petición POST a la API de FastAPI
            const response = await fetch('http://localhost:8000/api/v1/auth/reset-password', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                // Enviamos tanto el token como la nueva contraseña
                body: JSON.stringify({
                    token: token,
                    new_password: password
                }),
            });

            const data = await response.json();

            if (response.ok) {
                // Éxito: Mostramos el mensaje y limpiamos el input
                setMessage('Contraseña restablecida con éxito. Ya puedes iniciar sesión.');
                setPassword('');
            } else {
                // Error desde el backend
                setError(data.detail || 'Ocurrió un error al procesar tu solicitud.');
            }
        } catch (err) {
            // Error de conexión
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

                            {/* CAMPO CONTRASEÑA */}
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

                            {/* Mensajes de feedback visual */}
                            {error && (
                                <p style={{ color: '#d93025', textAlign: 'center', fontSize: '14px', marginBottom: '10px', marginTop: '20px' }}>
                                    {error}
                                </p>
                            )}
                            {message && (
                                <p style={{ color: '#188038', textAlign: 'center', fontSize: '14px', marginBottom: '10px', marginTop: '20px', fontWeight: 'bold' }}>
                                    {message}
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

                        {/* Sección 3: Footer */}
                        <div className={styles.pwdFooter}>
                            <p className={styles.footerText}>¿Te acuerdas de la contraseña?</p>
                            <Link className={styles.loginButton} to="/">
                                Iniciar sesión
                            </Link>
                        </div>
                    </div>
                </div>
            </main>
        </div>
    );
}

export default ChangePwd;