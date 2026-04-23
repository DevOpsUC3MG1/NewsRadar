import React, { useState } from 'react';
import { Link, useSearchParams } from 'react-router-dom';

import Button from '../../components/button';
import HeaderNoUser from '../../components/HeaderNoUser/HeaderNoUser.jsx';

import styles from './verify_acc.module.css'; // Puedes reutilizar el mismo CSS

function ConfirmVerify() {
    // Extraemos el token de la URL (ej: ?token=abc-123)
    const [searchParams] = useSearchParams();
    const token = searchParams.get('token');

    // Estados para manejar el resultado de la verificación
    const [message, setMessage] = useState('');
    const [error, setError] = useState('');
    const [isLoading, setIsLoading] = useState(false);
    const [isVerified, setIsVerified] = useState(false); // Para cambiar la vista si ya se verificó

    const handleVerify = async () => {
        setMessage('');
        setError('');

        if (!token) {
            setError('No se encontró ningún código de verificación en el enlace. Por favor, revisa tu correo.');
            return;
        }

        setIsLoading(true);

        try {
            // Hacemos el POST al endpoint de verificación
            const response = await fetch('http://localhost:8000/api/v1/auth/verify', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                // El backend espera un 'VerifyAccountRequest' con la propiedad 'token'
                body: JSON.stringify({ token: token }),
            });

            const data = await response.json();

            if (response.ok) {
                setMessage(data.message || '¡Tu cuenta ha sido verificada exitosamente!');
                setIsVerified(true);
            } else {
                setError(data.detail || 'El enlace es inválido o ha expirado.');
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
                <div className={styles.accCard}>

                    <div className={styles.darkHeader}>
                        <h1 className={styles.titleText}>CONFIRMA TU REGISTRO</h1>
                        <p className={styles.subtitleText}>Estás a un paso de terminar</p>
                    </div>

                    <div className={styles.lightForm}>
                        {/* Contenedor centralizado para los mensajes y el botón */}
                        <div className={styles.formElement} style={{ flex: 1 }}>

                            {!isVerified ? (
                                <>
                                    <p style={ { marginTop: '2rem', marginBottom: '3.5rem', color: '#09090F', fontWeight: '400', fontSize: '0.85rem' }}>
                                        Haz clic en el botón de "verificar cuenta" para poder verificar tu cuenta y empezar a usar <strong>NewsRadar</strong>.
                                    </p>

                                    <Button
                                        type="button"
                                        onClick={handleVerify}
                                        className={styles.continueButton}
                                        disabled={isLoading}
                                    >
                                        {isLoading ? 'VERIFICANDO...' : 'VERIFICAR CUENTA'}
                                    </Button>
                                </>
                            ) : (
                                <p style={{ color: '#188038', textAlign: 'center', fontSize: '18px', fontWeight: 'bold' }}>
                                    {message}
                                </p>
                            )}

                            {error && (
                                <p style={{ color: '#d93025', textAlign: 'center', fontSize: '14px', marginTop: '20px' }}>
                                    {error}
                                </p>
                            )}
                        </div>

                        <div className={styles.accFooter}>
                            <p className={styles.footerText}>¿Ya está todo listo?</p>
                            <Link className={styles.loginButton} to="/" style={{ color: '#5B8DE9', textDecoration: 'none', border: '1px solid #5B8DE9', padding: '8px 30px', borderRadius: '8px' }}>
                                Iniciar sesión
                            </Link>
                        </div>
                    </div>
                </div>
            </main>
        </div>
    );
}

export default ConfirmVerify;