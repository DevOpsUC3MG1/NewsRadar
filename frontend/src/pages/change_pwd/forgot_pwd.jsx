// forgot_pwd.jsx
import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';

// Importamos nuestros componentes reutilizables
import Input from '../../components/input';
import Button from '../../components/button';
import HeaderNoUser from '../../components/HeaderNoUser/HeaderNoUser.jsx';

import styles from './forgot_pwd.module.css';

function ChangePwd() {
    // 1. Creamos los estados para manejar los datos y la interfaz
    const [email, setEmail] = useState('');
    const [message, setMessage] = useState('');
    const [error, setError] = useState('');
    const [isLoading, setIsLoading] = useState(false);

    const navigate = useNavigate();

    // 2. Función que se ejecuta al hacer clic en "Continuar"
    const handleSubmit = async (e) => {
        e.preventDefault(); // Evita que la página recargue el navegador

        // Limpiamos mensajes anteriores antes de enviar
        setMessage('');
        setError('');

        if (!email) {
            setError('Por favor, introduce tu correo electrónico.');
            return;
        }

        setIsLoading(true); // Activamos estado de carga

        try {
            // 3. Hacemos la petición POST a tu API (FastAPI)
            const response = await fetch('http://localhost:8000/api/v1/auth/forgot-password', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                // El backend espera un 'payload' con la propiedad 'email'
                body: JSON.stringify({ email: email }),
            });

            const data = await response.json();

            if (response.ok) {
                // Éxito: Mostramos el mensaje que nos devuelve FastAPI
                setMessage(data.message);
                setEmail(''); // Opcional: vaciamos el input
            } else {
                // Error desde el backend (ej. 422 Unprocessable Entity si el email es inválido)
                setError(data.detail || 'Ocurrió un error al procesar tu solicitud.');
            }
        } catch (err) {
            // Error de red (ej. el backend está apagado)
            setError('No se pudo conectar con el servidor. Inténtalo de nuevo más tarde.');
        } finally {
            setIsLoading(false); // Apagamos estado de carga
        }
    };

    return (
        <div className={styles.pageContainer}>
            <HeaderNoUser />

            <main className={styles.mainContent}>
                <div className={styles.pwdCard}>

                    {/* Sección 1: Cabecera oscura */}
                    <div className={styles.darkHeader}>
                        <h1 className={styles.titleText}>RECUPERA TU CONTRASEÑA</h1>
                        <p className={styles.subtitleText}>Ingresa tu correo electrónico</p>
                    </div>

                    {/* Sección 2: Formulario de la tarjeta */}
                    <div className={styles.lightForm}>
                        {/* 4. Añadimos el evento onSubmit al form */}
                        <form className={styles.formElement} onSubmit={handleSubmit}>

                            {/* CAMPO EMAIL REUTILIZADO */}
                            <Input
                                label="CORREO ELECTRÓNICO"
                                type="email"
                                id="email"
                                // 5. Conectamos el input con el estado
                                value={email}
                                onChange={(e) => setEmail(e.target.value)}
                                className={styles.formInput}
                                labelClassName={styles.formLabel}
                                required
                            />

                            <p className={styles.instructionText}>
                                Te envíaremos un correo electrónico con las instrucciones para restablecer tu contraseña.
                            </p>

                            {/* 6. Mostramos los mensajes de feedback al usuario */}
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

                            {/* BOTÓN REUTILIZADO */}
                            <Button
                                type="submit"
                                className={styles.continueButton}
                                disabled={isLoading} // Deshabilitamos si está cargando
                            >
                                {isLoading ? 'ENVIANDO...' : 'CONTINUAR'}
                            </Button>

                        </form>

                        <div className={styles.pwdFooter}>
                            <p className={styles.footerText}>¿Te acuerdas de la contraseña?</p>
                            <button
                                type="button"
                                className={styles.loginButton}
                                onClick={() => navigate(-1)}
                            >
                                Volver
                            </button>
                        </div>
                    </div>
                </div>
            </main>
        </div>
    );
}

export default ChangePwd;