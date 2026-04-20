// verify_acc.jsx
import React, { useState } from 'react';
import { Link } from 'react-router-dom';

// Importamos nuestros componentes reutilizables
import Input from '../../components/input';
import Button from '../../components/button';
import HeaderNoUser from '../../components/HeaderNoUser/HeaderNoUser.jsx';

import styles from './verify_acc.module.css';

function VerifyAcc() {
    // 1. Estados para manejar el correo y la interfaz
    const [email, setEmail] = useState('');
    const [message, setMessage] = useState('');
    const [error, setError] = useState('');
    const [isLoading, setIsLoading] = useState(false);

    // 2. Función para reenviar el correo de verificación
    const handleSubmit = async (e) => {
        e.preventDefault();

        // Limpiamos mensajes previos
        setMessage('');
        setError('');

        if (!email) {
            setError('Por favor, introduce tu correo electrónico.');
            return;
        }

        setIsLoading(true);

        try {
            // CAMBIO CLAVE: Enviamos el email como parámetro de consulta (?payload=...)
            // y eliminamos el 'body' de la configuración del fetch.
            const url = `http://localhost:8000/api/v1/auth/resend-verification?payload=${encodeURIComponent(email)}`;

            const response = await fetch(url, {
                method: 'POST',
                headers: {
                    'Accept': 'application/json',
                    // Ya no necesitamos Content-Type porque no enviamos body
                }
            });

            const data = await response.json();

            if (response.ok) {
                setMessage(data.message || 'Se ha enviado un nuevo enlace de verificación a tu correo.');
                setEmail('');
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
                <div className={styles.accCard}>

                    {/* Sección 1: Cabecera oscura */}
                    <div className={styles.darkHeader}>
                        <h1 className={styles.titleText}>VERIFICA TU CUENTA</h1>
                        <p className={styles.subtitleText}>Ingresa tu correo electrónico</p>
                    </div>

                    {/* Sección 2: Formulario de la tarjeta */}
                    <div className={styles.lightForm}>
                        <form className={styles.formElement} onSubmit={handleSubmit}>

                            {/* CAMPO EMAIL */}
                            <Input
                                label="CORREO ELECTRÓNICO"
                                type="email"
                                id="email"
                                value={email}
                                onChange={(e) => setEmail(e.target.value)}
                                className={styles.formInput}
                                labelClassName={styles.formLabel}
                                required
                            />

                            <p className={styles.instructionText}>
                                Te enviaremos un correo electrónico con las instrucciones para verificar tu cuenta.
                            </p>

                            {/* Mensajes de feedback visual */}
                            {error && (
                                <p style={{ color: '#d93025', textAlign: 'center', fontSize: '14px', marginBottom: '10px' }}>
                                    {error}
                                </p>
                            )}
                            {message && (
                                <p style={{ color: '#188038', textAlign: 'center', fontSize: '14px', marginBottom: '10px', fontWeight: 'bold' }}>
                                    {message}
                                </p>
                            )}

                            {/* BOTÓN CONTINUAR */}
                            <Button
                                type="submit"
                                className={styles.continueButton}
                                disabled={isLoading}
                            >
                                {isLoading ? 'ENVIANDO...' : 'CONTINUAR'}
                            </Button>

                        </form>

                        <div className={styles.accFooter}>
                            <p className={styles.footerText}>¿Lo quieres hacer en otro momento?</p>
                            <Link className={styles.backButton} to="/">
                                Volver
                            </Link>
                        </div>
                    </div>
                </div>
            </main>
        </div>
    );
}

export default VerifyAcc;