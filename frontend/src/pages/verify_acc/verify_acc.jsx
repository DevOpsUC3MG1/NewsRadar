// frontend/src/pages/verify_acc/verify_acc.jsx
import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { CheckCircle } from 'lucide-react'; // <-- Importamos el icono para el modal

import Input from '../../components/input';
import Button from '../../components/button';
import HeaderNoUser from '../../components/HeaderNoUser/HeaderNoUser.jsx';

import styles from './verify_acc.module.css';

function VerifyAcc() {
    const { t } = useTranslation();
    const [email, setEmail] = useState('');
    const [message, setMessage] = useState('');
    const [error, setError] = useState('');
    const [isLoading, setIsLoading] = useState(false);

    // --- NUEVO: Estado para el modal de éxito ---
    const [showSuccessModal, setShowSuccessModal] = useState(false);

    const navigate = useNavigate();

    // --- NUEVO: Escuchar si otra pestaña verifica la cuenta ---
    useEffect(() => {
        const channel = new BroadcastChannel('auth_channel');

        channel.onmessage = (event) => {
            if (event.data && event.data.type === 'VERIFICATION_SUCCESS') {
                setShowSuccessModal(true); // Mostramos el modal de inmediato
            }
        };

        // Limpiamos el canal cuando se desmonte el componente
        return () => {
            channel.close();
        };
    }, []);

    const handleSubmit = async (e) => {
        e.preventDefault();
        setMessage('');
        setError('');

        if (!email) {
            setError(t('verifyAcc.errors.emptyEmail'));
            return;
        }

        setIsLoading(true);

        try {
            const url = `http://localhost:8000/api/v1/auth/resend-verification?payload=${encodeURIComponent(email)}`;

            const response = await fetch(url, {
                method: 'POST',
                headers: {
                    'Accept': 'application/json',
                }
            });

            const data = await response.json();

            if (response.ok) {
                setMessage(data.message || t('verifyAcc.successDefault'));
                setEmail('');
            } else {
                setError(data.detail || t('verifyAcc.errors.defaultError'));
            }
        } catch (err) {
            setError(t('verifyAcc.errors.networkError'));
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
                        <h1 className={styles.titleText}>{t('verifyAcc.title')}</h1>
                        <p className={styles.subtitleText}>{t('verifyAcc.subtitle')}</p>
                    </div>

                    <div className={styles.lightForm}>
                        <form className={styles.formElement} onSubmit={handleSubmit}>

                            <Input
                                label={t('verifyAcc.emailLabel')}
                                type="email"
                                id="email"
                                value={email}
                                onChange={(e) => setEmail(e.target.value)}
                                className={styles.formInput}
                                labelClassName={styles.formLabel}
                                required
                            />

                            <p className={styles.instructionText}>
                                {t('verifyAcc.instruction')}
                            </p>

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

                            <Button
                                type="submit"
                                className={styles.continueButton}
                                disabled={isLoading}
                            >
                                {isLoading ? t('verifyAcc.buttonSending') : t('verifyAcc.buttonContinue')}
                            </Button>

                        </form>

                        <div className={styles.accFooter}>
                            <p className={styles.footerText}>{t('verifyAcc.footerQuestion')}</p>
                            <button
                                type="button"
                                className={styles.backButton}
                                onClick={() => navigate(-1)}
                            >
                                {t('verifyAcc.backBtn')}
                            </button>
                        </div>
                    </div>
                </div>
            </main>

            {/* --- NUEVO: MODAL DE ÉXITO --- */}
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

export default VerifyAcc;