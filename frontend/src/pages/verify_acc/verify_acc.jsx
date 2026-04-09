// verify_acc.jsx
import React from 'react';
import { Link } from 'react-router-dom';
import HeaderNoUser from '../../components/HeaderNoUser/HeaderNoUser.jsx';
import styles from './verify_acc.module.css';

function VerifyAcc() {
    return (
        <div className={styles.pageContainer}>
            <HeaderNoUser />

            <main className={styles.mainContent}>
                <div className={styles.accCard}>

                    {/* Sección 1: Cabecera oscura */}
                    <div className={styles.darkHeader}>
                        {/* CAMBIO: Texto del título actualizado */}
                        <h1 className={styles.titleText}>VERIFICA TU CUENTA</h1>
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

                            {/* CAMBIO: Texto de instrucciones actualizado */}
                            <p className={styles.instructionText}>
                                Te envíaremos un correo electrónico con las instrucciones para verificar tu cuenta.
                            </p>

                            <button className={styles.continueButton} type="submit">
                                CONTINUAR
                            </button>
                        </form>

                        <div className={styles.accFooter}>
                            {/* CAMBIO: Textos del footer actualizados */}
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