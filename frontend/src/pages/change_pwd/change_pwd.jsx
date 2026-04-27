// frontend/src/pages/change_pwd/change_pwd.jsx
import React, { useState } from 'react';
import { Link, useSearchParams, useNavigate } from 'react-router-dom';
import { useTranslation } from 'react-i18next';

// Importamos nuestros componentes reutilizables
import Input from '../../components/input';
import Button from '../../components/button';
import HeaderNoUser from '../../components/HeaderNoUser/HeaderNoUser.jsx';

import styles from './change_pwd.module.css';

function ChangePwd() {
    const { t } = useTranslation();
    const [searchParams] = useSearchParams();
    const token = searchParams.get('token');

    const navigate = useNavigate();

    const [password, setPassword] = useState('');
    const [error, setError] = useState('');
    const [isLoading, setIsLoading] = useState(false);

    const [showSuccess, setShowSuccess] = useState(false);

    const handleSubmit = async (e) => {
        e.preventDefault();
        setError('');

        if (!token) {
            setError(t('changePwd.errors.invalidToken'));
            return;
        }

        if (!password || password.length < 6) {
            setError(t('changePwd.errors.passwordMin'));
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
                setShowSuccess(true);
                setPassword('');
            } else {
                // Si el backend devuelve un error detallado lo mostramos, si no, uno genérico traducido
                setError(data.detail || t('changePwd.errors.default'));
            }
        } catch (err) {
            setError(t('changePwd.errors.network'));
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
                        <h1 className={styles.titleText}>{t('changePwd.title')}</h1>
                        <p className={styles.subtitleText}>
                            {t('changePwd.subtitle1')} <br />
                            {t('changePwd.subtitle2')}
                        </p>
                    </div>

                    <div className={styles.lightForm}>
                        <form className={styles.formElement} onSubmit={handleSubmit}>

                            <Input
                                label={t('changePwd.newPasswordLabel')}
                                type="password"
                                id="password"
                                value={password}
                                onChange={(e) => setPassword(e.target.value)}
                                className={styles.formInput}
                                labelClassName={styles.formLabel}
                                required
                            />

                            {error && (
                                <p style={{ color: '#d93025', textAlign: 'center', fontSize: '14px', marginBottom: '10px', marginTop: '20px' }}>
                                    {error}
                                </p>
                            )}

                            <Button
                                type="submit"
                                className={styles.continueButton}
                                disabled={isLoading}
                                style={{ marginTop: '35px' }}
                            >
                                {isLoading ? t('changePwd.loadingBtn') : t('changePwd.submitBtn')}
                            </Button>

                        </form>

                        <div className={styles.pwdFooter}>
                            <p className={styles.footerText}>{t('changePwd.rememberPwd')}</p>
                            <Link className={styles.loginButton} to="/">
                                {t('changePwd.loginLink')}
                            </Link>
                        </div>
                    </div>
                </div>
            </main>

            {showSuccess && (
                <div className={styles.modalOverlay}>
                    <div className={styles.modalContent}>
                        <div className={styles.successIcon}>✓</div>
                        <h2 className={styles.modalTitle}>{t('changePwd.modal.title')}</h2>
                        <p className={styles.modalText}>
                            {t('changePwd.modal.text')}
                        </p>
                        <Button
                            className={styles.modalButton}
                            onClick={() => navigate('/')}
                        >
                            {t('changePwd.modal.button')}
                        </Button>
                    </div>
                </div>
            )}

        </div>
    );
}

export default ChangePwd;