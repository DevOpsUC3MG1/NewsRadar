// forgot_pwd.jsx
import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useTranslation } from 'react-i18next';

// Importamos nuestros componentes reutilizables
import Input from '../../components/input';
import Button from '../../components/button';
import HeaderNoUser from '../../components/HeaderNoUser/HeaderNoUser.jsx';

import styles from './forgot_pwd.module.css';

function ChangePwd() {
    const { t } = useTranslation();
    const [email, setEmail] = useState('');
    const [message, setMessage] = useState('');
    const [error, setError] = useState('');
    const [isLoading, setIsLoading] = useState(false);

    const navigate = useNavigate();

    const handleSubmit = async (e) => {
        e.preventDefault();

        setMessage('');
        setError('');

        if (!email) {
            setError(t('forgotPwd.errors.emailRequired'));
            return;
        }

        setIsLoading(true);

        try {
            const response = await fetch('http://localhost:8000/api/v1/auth/forgot-password', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ email: email }),
            });

            const data = await response.json();

            if (response.ok) {
                setMessage(data.message);
                setEmail('');
            } else {
                setError(data.detail || t('forgotPwd.errors.default'));
            }
        } catch (err) {
            setError(t('forgotPwd.errors.network'));
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <div className={styles.pageContainer}>
            <HeaderNoUser />

            <main className={styles.mainContent}>
                <div className={styles.pwdCard}>

                    <div className={styles.darkHeader}>
                        <h1 className={styles.titleText}>{t('forgotPwd.title')}</h1>
                        <p className={styles.subtitleText}>{t('forgotPwd.subtitle')}</p>
                    </div>

                    <div className={styles.lightForm}>
                        <form className={styles.formElement} onSubmit={handleSubmit}>

                            <Input
                                label={t('forgotPwd.emailLabel')}
                                type="email"
                                id="email"
                                value={email}
                                onChange={(e) => setEmail(e.target.value)}
                                className={styles.formInput}
                                labelClassName={styles.formLabel}
                                required
                            />

                            <p className={styles.instructionText}>
                                {t('forgotPwd.instructions')}
                            </p>

                            {error && (
                                <p style={{ color: '#d93025', textAlign: 'center', fontSize: '14px', marginBottom: '10px' }}>
                                    {error}
                                </p>
                            )}
                            {/* Nota: message viene del backend. Podrías llegar a traducirlo también si controlas las respuestas de la API */}
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
                                {isLoading ? t('forgotPwd.loadingBtn') : t('forgotPwd.submitBtn')}
                            </Button>

                        </form>

                        <div className={styles.pwdFooter}>
                            <p className={styles.footerText}>{t('forgotPwd.rememberPwd')}</p>
                            <button
                                type="button"
                                className={styles.loginButton}
                                onClick={() => navigate(-1)}
                            >
                                {t('forgotPwd.backBtn')}
                            </button>
                        </div>
                    </div>
                </div>
            </main>
        </div>
    );
}

export default ChangePwd;