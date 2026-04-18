// verify_acc.jsx
import React from 'react';
import { Link } from 'react-router-dom';

// Importamos nuestros componentes reutilizables
import Input from '../../components/input';
import Button from '../../components/button';
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
                        <h1 className={styles.titleText}>VERIFICA TU CUENTA</h1>
                        <p className={styles.subtitleText}>Ingresa tu correo electrónico</p>
                    </div>

                    {/* Sección 2: Formulario de la tarjeta */}
                    <div className={styles.lightForm}>
                        <form className={styles.formElement}>
                            
                            {/* CAMPO EMAIL REUTILIZADO */}
                            <Input
                                label="CORREO ELECTRÓNICO"
                                type="email"
                                id="email"
                                className={styles.formInput}
                                labelClassName={styles.formLabel}
                            />

                            <p className={styles.instructionText}>
                                Te envíaremos un correo electrónico con las instrucciones para verificar tu cuenta.
                            </p>

                            {/* BOTÓN REUTILIZADO */}
                            <Button type="submit" className={styles.continueButton}>
                                CONTINUAR
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