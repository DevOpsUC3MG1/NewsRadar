// frontend/src/pages/verify_acc/confirm_verify.jsx
import React, { useState } from 'react';
import { Link, useSearchParams, useNavigate } from 'react-router-dom'; // <-- Añadido useNavigate
import { useTranslation } from 'react-i18next';
import { CheckCircle } from 'lucide-react'; // <-- Importamos el icono para el modal

import Button from '../../components/button';
import HeaderNoUser from '../../components/HeaderNoUser/HeaderNoUser.jsx';

import styles from './verify_acc.module.css';

function ConfirmVerify() {
    const { t } = useTranslation();
    const [searchParams] = useSearchParams();
    const token = searchParams.get('token');
    const navigate = useNavigate(); // <-- Inicializamos navigate

    const [message, setMessage] = useState('');
    const [error, setError] = useState('');
    const [isLoading, setIsLoading] = useState(false);
    const [isVerified, setIsVerified] = useState(false);

    // --- NUEVO: Estado para el modal de éxito ---
    const [showSuccessModal, setShowSuccessModal] = useState(false);

    const handleVerify = async () => {
        setMessage('');
        setError('');

        if (!token) {
            setError(t('confirmVerify.errors.noToken'));
            return;
        }

        setIsLoading(true);

        try {
            const response = await fetch('http://localhost:8000/api/v1/auth/verify', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ token: token }),
            });

            const data = await response.json();

            if (response.ok) {
                setMessage(data.message || t('confirmVerify.successDefault'));
                setIsVerified(true);

                // --- NUEVO: Mostramos el modal de éxito ---
                setShowSuccessModal(true);

                // Mantenemos el BroadcastChannel por si la otra pestaña sigue abierta
                const channel = new BroadcastChannel('auth_channel');
                channel.postMessage({ type: 'VERIFICATION_SUCCESS' });
                channel.close();
            } else {
                setError(data.detail || t('confirmVerify.errors.defaultError'));
            }
        } catch (err) {
            setError(t('confirmVerify.errors.networkError'));
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
                        <h1 className={styles.titleText}>{t('confirmVerify.title')}</h1>
                        <p className={styles.subtitleText}>{t('confirmVerify.subtitle')}</p>
                    </div>

                    <div className={styles.lightForm}>
                        <div className={styles.formElement} style={{ flex: 1 }}>

                            {!isVerified ? (
                                <>
                                    <p style={ { marginTop: '2rem', marginBottom: '3.5rem', color: '#09090F', fontWeight: '400', fontSize: '0.85rem' }}>
                                        {t('confirmVerify.instruction')} <strong>NewsRadar</strong>.
                                    </p>

                                    <Button
                                        type="button"
                                        onClick={handleVerify}
                                        className={styles.continueButton}
                                        disabled={isLoading}
                                    >
                                        {isLoading ? t('confirmVerify.buttonVerifying') : t('confirmVerify.buttonVerify')}
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
                            <p className={styles.footerText}>{t('confirmVerify.footerQuestion')}</p>
                            <Link className={styles.loginButton} to="/" style={{ color: '#5B8DE9', textDecoration: 'none', border: '1px solid #5B8DE9', padding: '8px 30px', borderRadius: '8px' }}>
                                {t('confirmVerify.loginBtn')}
                            </Link>
                        </div>
                    </div>
                </div>
            </main>

            {/* --- NUEVO: MODAL DE ÉXITO IDÉNTICO --- */}
            {showSuccessModal && (
                <div style={{
                    position: 'fixed', top: 0, left: 0, right: 0, bottom: 0,
                    backgroundColor: 'rgba(0,0,0,0.6)', display: 'flex',
                    justifyContent: 'center', alignItems: 'center', zIndex: 9999
                }}>
                    <div style={{
                        backgroundColor: '#fff', padding: '40px 30px', borderRadius: '12px',
                        maxWidth: '400px', width: '90%', textAlign: 'center', boxShadow: '0 10px 25px rgba(0,0,0,0.2)',
                        animation: 'fadeIn 0.3s ease-out'
                    }}>
                        <div style={{ display: 'flex', justifyContent: 'center', marginBottom: '20px' }}>
                            <CheckCircle size={60} color="#188038" />
                        </div>
                        <h2 style={{ color: '#0E0E1D', marginBottom: '15px', fontSize: '24px' }}>
                            Cuenta verificada correctamente
                        </h2>
                        <p style={{ color: '#626262', marginBottom: '30px', fontSize: '15px', lineHeight: '1.5' }}>
                            Tu correo electrónico ha sido verificado con éxito. Ya puedes volver a tu perfil de usuario.
                        </p>
                        <button
                            onClick={() => navigate('/profile')}
                            style={{
                                width: '100%', padding: '14px', borderRadius: '8px', cursor: 'pointer',
                                backgroundColor: '#09090F', color: '#FFFFFF', border: 'none',
                                fontWeight: 'bold', fontSize: '15px', transition: 'all 0.2s',
                                textTransform: 'uppercase'
                            }}
                        >
                            Volver al perfil
                        </button>
                    </div>
                </div>
            )}

        </div>
    );
}

export default ConfirmVerify;