// change_pwd.jsx
import React from 'react';
import { Link } from 'react-router-dom';
import HeaderNoUser from '../../components/HeaderNoUser/HeaderNoUser.jsx';
import styles from './change_pwd.module.css';

function ChangePwd() {
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
                        <form className={styles.formElement}>
                            <div className={styles.formGroup}>
                                <label className={styles.formLabel} htmlFor="email">
                                    CORREO ELECTRÓNICO
                                </label>
                                <input
                                    className={styles.formInput}
                                    type="email"
                                    id="email"
                                />
                            </div>

                            <p className={styles.instructionText}>
                                Te envíaremos un correo electrónico con las instrucciones para restablecer tu contraseña.
                            </p>

                            <button className={styles.continueButton} type="submit">
                                CONTINUAR
                            </button>
                        </form>

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