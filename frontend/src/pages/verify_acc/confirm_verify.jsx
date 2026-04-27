import React, { useState } from 'react';
import { Link, useSearchParams } from 'react-router-dom';
import { useTranslation } from 'react-i18next'; // <-- Importamos

import Button from '../../components/button';
import HeaderNoUser from '../../components/HeaderNoUser/HeaderNoUser.jsx';

import styles from './verify_acc.module.css';

function ConfirmVerify() {
    const { t } = useTranslation(); // <-- Extraemos t
    const [searchParams] = useSearchParams();
    const token = searchParams.get('token');

    const [message, setMessage] = useState('');
    const [error, setError] = useState('');
    const [isLoading, setIsLoading] = useState(false);
    const [isVerified, setIsVerified] = useState(false);

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
        </div>
    );
}

export default ConfirmVerify;