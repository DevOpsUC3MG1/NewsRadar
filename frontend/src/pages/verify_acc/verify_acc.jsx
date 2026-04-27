import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useTranslation } from 'react-i18next'; // <-- Importamos

import Input from '../../components/input';
import Button from '../../components/button';
import HeaderNoUser from '../../components/HeaderNoUser/HeaderNoUser.jsx';

import styles from './verify_acc.module.css';

function VerifyAcc() {
    const { t } = useTranslation(); // <-- Extraemos t
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
        </div>
    );
}

export default VerifyAcc;