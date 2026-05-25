import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { User, CheckCircle, Pencil, Save, X, Key, Mail, Trash2, Check, AlertTriangle, Loader2 } from 'lucide-react';
import { useTranslation } from 'react-i18next';
import styles from './user_profile.module.css';
import { checkVerificationStatus, deleteUserAccount, updateUser } from '../../services/userService';
import authService from '../../services/authService';

const UserProfile = () => {
  const { t } = useTranslation();
  const navigate = useNavigate();

  const [userData, setUserData] = useState({
    id: null, first_name: '', last_name: '', email: '', organization: '', phone: '', role_ids: []
  });

  const [isEditingInfo, setIsEditingInfo] = useState(false);
  const [isSavingInfo, setIsSavingInfo] = useState(false); // Estado de carga para el botón guardar
  const [infoError, setInfoError] = useState("");
  const [tempInfo, setTempInfo] = useState({});

  const [isVerified, setIsVerified] = useState(false);

  // --- ESTADOS PARA EL MODAL DE ELIMINAR CUENTA ---
  const [showDeleteModal, setShowDeleteModal] = useState(false);
  const [confirmEmail, setConfirmEmail] = useState('');
  const [deleteError, setDeleteError] = useState('');
  const [isDeleting, setIsDeleting] = useState(false);

  useEffect(() => {
    const savedUser = JSON.parse(localStorage.getItem('user')) || {
      id: null,
      first_name: '-',
      last_name: '-',
      email: '-',
      organization: '-',
      phone: '-',
      role_ids: []
    };

    setUserData(savedUser);
    setTempInfo(savedUser);

    if (savedUser.email) {
      const token = authService.getToken();
      checkVerificationStatus(savedUser.email, token)
        .then(status => setIsVerified(status))
        .catch(err => console.error(err));
    }
  }, []);

  // --- FUNCIÓN PARA GUARDAR EN EL BACKEND ---
  const handleSaveInfo = async () => {
    setIsSavingInfo(true);
    setInfoError("");

    try {
      const token = authService.getToken();

      // Preparamos solo los datos permitidos por UserUpdate en el backend
      const updatePayload = {
        first_name: tempInfo.first_name,
        last_name: tempInfo.last_name,
        organization: tempInfo.organization,
        phone: tempInfo.phone
      };

      // Llamamos a la API
      const updatedDataFromBackend = await updateUser(userData.id, updatePayload, token);

      // Actualizamos el estado y el localStorage con lo que nos devuelve el servidor
      const updatedUser = { ...userData, ...updatedDataFromBackend };
      setUserData(updatedUser);
      localStorage.setItem('user', JSON.stringify(updatedUser));

      setIsEditingInfo(false);
    } catch (error) {
      console.error(error);
      setInfoError("Error al guardar los cambios en el servidor."); // Puedes traducirlo con i18next si quieres
    } finally {
      setIsSavingInfo(false);
    }
  };

  // Definición de roles con los nuevos IDs reales
  const availableRoles = [
    { id: 3, name: 'Lector' }, // Cambia esto por t('userProfile.roles.lector') si lo tienes en el JSON
    { id: 4, name: 'Gestor' }  // Cambia esto por t('userProfile.roles.gestor') si lo tienes en el JSON
  ];

  // --- LÓGICA PARA ELIMINAR CUENTA ---
  const handleDeleteAccount = async () => {
    if (confirmEmail !== userData.email) {
      setDeleteError(t('userProfile.deleteModal.errors.emailMismatch'));
      return;
    }

    if (!userData.id) {
      setDeleteError(t('userProfile.deleteModal.errors.noUserId'));
      return;
    }

    setIsDeleting(true);
    setDeleteError('');

    try {
      const token = authService.getToken();
      await deleteUserAccount(userData.id, token);

      localStorage.removeItem('user');
      localStorage.removeItem('token');
      navigate('/');

      window.location.reload();
    } catch (error) {
      setDeleteError(t('userProfile.deleteModal.errors.apiError'));
      setIsDeleting(false);
    }
  };

  return (
    <div className={styles.pageWrapper}>
      {/* HEADER */}
      <div className={styles.headerBanner}>
        <div className={styles.userIconCircle}><User size={32} color="#FFFFFF" /></div>
        <div className={styles.userNameContainer}>
          <h1 className={styles.userName}>{userData.first_name} {userData.last_name}</h1>
          <CheckCircle size={24} color={isVerified ? "#90E0EF" : "#626262"} />
        </div>
      </div>

      {/* MAIN GRID */}
      <div className={styles.mainGrid}>
        <div className={styles.leftColumn}>
          {/* Información Personal */}
          <div className={styles.card} style={{ flex: 2 }}>
            <span className={styles.cardTitle}>{t('userProfile.personalInfo.title')}</span>

            {infoError && (
              <div style={{ color: '#B65753', marginBottom: '15px', fontSize: '0.9rem', fontWeight: 'bold' }}>
                {infoError}
              </div>
            )}

            <div className={styles.infoGrid}>
              {['first_name','last_name','organization','phone'].map(field => (
                <div key={field} className={styles.inputGroup}>
                  <label>{t(`userProfile.personalInfo.${field}`)}</label>
                  <input
                    type={field === 'phone' ? 'tel' : 'text'}
                    name={field}
                    value={tempInfo[field] || ''}
                    onChange={e => setTempInfo({...tempInfo, [field]: e.target.value})}
                    disabled={!isEditingInfo || isSavingInfo}
                    className={`${styles.inputField} ${isEditingInfo ? styles.activeInput : styles.disabledInput}`}
                  />
                </div>
              ))}
              <div className={styles.inputGroup}>
                <label>{t('userProfile.personalInfo.email')}</label>
                <input type="email" value={userData.email} disabled className={`${styles.inputField} ${styles.emailInput}`} />
              </div>
            </div>

            <div className={styles.buttonContainer}>
              {!isEditingInfo ? (
                <button className={`${styles.btnAction} ${styles.btnDark}`} onClick={() => setIsEditingInfo(true)}>
                  <Pencil size={16} /> {t('userProfile.actions.edit')}
                </button>
              ) : (
                <>
                  <button className={`${styles.btnAction} ${styles.btnDanger}`} disabled={isSavingInfo} onClick={() => { setTempInfo(userData); setIsEditingInfo(false); setInfoError(""); }}>
                    <X size={16} /> {t('userProfile.actions.cancel')}
                  </button>
                  <button className={`${styles.btnAction} ${styles.btnDark}`} disabled={isSavingInfo} onClick={handleSaveInfo}>
                    {isSavingInfo ? <Loader2 size={16} className={styles.spinner} /> : <Save size={16} />}
                    {t('userProfile.actions.save')}
                  </button>
                </>
              )}
            </div>
          </div>

          {/* Roles (SECCIÓN FIJA Y DESHABILITADA) */}
          <div className={styles.card} style={{ flex: 1 }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
              <span className={styles.cardTitle}>{t('userProfile.roles.title')}</span>
              <div className={styles.buttonContainer} style={{ marginTop: 0 }}>
                {/* Botón visualmente bloqueado */}
                <button
                  className={`${styles.btnAction} ${styles.btnDark}`}
                  disabled
                  style={{ opacity: 0.5, cursor: 'not-allowed' }}
                >
                  <Pencil size={16}/> {t('userProfile.actions.edit')}
                </button>
              </div>
            </div>

            {/* Lista visualmente bloqueada */}
            <div className={`${styles.rolesList} ${styles.rolesDisabled}`}>
              {availableRoles.map(role => {
                // Forzamos que el rol Gestor (ID 4) sea el que siempre aparece seleccionado
                const isSelected = role.id === 4;
                return (
                  <div
                    key={role.id}
                    className={`${styles.roleItem} ${isSelected ? styles.roleSelected : styles.roleUnselected}`}
                  >
                    <div className={`${styles.tickCircle} ${isSelected ? styles.tickSelected : styles.tickUnselected}`}>
                      {isSelected && <Check size={12} color="#0E0E1D" />}
                    </div>
                    {role.name}
                  </div>
                );
              })}
            </div>
          </div>
        </div>

        {/* Seguridad */}
        <div className={`${styles.card} ${styles.securityCard}`}>
          <div className={styles.securityTopActions}>
            <span className={styles.cardTitle}>{t('userProfile.security.title')}</span>
            <button className={`${styles.btnAction} ${styles.btnDark}`} onClick={() => navigate('/recuperar-password')}>
              <Key size={18} /> {t('userProfile.security.changePassword')}
            </button>
            <button className={`${styles.btnAction} ${isVerified ? styles.btnGray : styles.btnDark}`} disabled={isVerified} onClick={() => navigate('/reenviar-verificacion')}>
              <Mail size={18} /> {t('userProfile.security.verifyEmail')}
            </button>
          </div>
          <button className={`${styles.btnAction} ${styles.btnDanger}`} onClick={() => setShowDeleteModal(true)}>
            <Trash2 size={18} /> {t('userProfile.security.deleteAccount')}
          </button>
        </div>
      </div>

      {/* MODAL DE ELIMINAR CUENTA (Se mantiene igual) */}
      {showDeleteModal && (
        <div style={{
          position: 'fixed', top: 0, left: 0, right: 0, bottom: 0,
          backgroundColor: 'rgba(0,0,0,0.6)', display: 'flex',
          justifyContent: 'center', alignItems: 'center', zIndex: 9999
        }}>
          <div style={{
            backgroundColor: '#fff', padding: '30px', borderRadius: '12px',
            maxWidth: '450px', width: '90%', textAlign: 'center', boxShadow: '0 10px 25px rgba(0,0,0,0.2)'
          }}>
            <div style={{ display: 'flex', justifyContent: 'center', marginBottom: '15px' }}>
              <AlertTriangle size={48} color="#B65753" />
            </div>
            <h2 style={{ color: '#0E0E1D', marginBottom: '10px', fontSize: '24px' }}>
              {t('userProfile.deleteModal.title')}
            </h2>
            <p style={{ color: '#626262', marginBottom: '20px', fontSize: '15px', lineHeight: '1.5' }}>
              {t('userProfile.deleteModal.warning')} <br/><br/>
              {t('userProfile.deleteModal.confirmText')} <strong>{userData.email}</strong>
            </p>

            <input
              type="email"
              placeholder={t('userProfile.deleteModal.placeholder')}
              value={confirmEmail}
              onChange={(e) => {
                setConfirmEmail(e.target.value);
                setDeleteError('');
              }}
              style={{
                width: '100%', padding: '12px', marginBottom: '15px',
                borderRadius: '6px', border: '1px solid #ccc', outline: 'none',
                boxSizing: 'border-box', fontSize: '15px'
              }}
            />

            {deleteError && (
              <p style={{ color: '#B65753', fontSize: '14px', marginBottom: '15px', fontWeight: '500' }}>
                {deleteError}
              </p>
            )}

            <div style={{ display: 'flex', justifyContent: 'space-between', gap: '15px', marginTop: '20px' }}>
              <button
                onClick={() => {
                  setShowDeleteModal(false);
                  setConfirmEmail('');
                  setDeleteError('');
                }}
                disabled={isDeleting}
                style={{
                  flex: 1, padding: '12px', borderRadius: '6px', cursor: 'pointer',
                  backgroundColor: '#FFFFFF', color: '#0E0E1D', border: '2px solid #0E0E1D',
                  fontWeight: 'bold', fontSize: '14px', transition: 'all 0.2s'
                }}
              >
                {t('userProfile.deleteModal.keepBtn')}
              </button>

              <button
                onClick={handleDeleteAccount}
                disabled={isDeleting}
                style={{
                  flex: 1, padding: '12px', borderRadius: '6px', cursor: isDeleting ? 'not-allowed' : 'pointer',
                  backgroundColor: '#B65753', color: '#FFFFFF', border: 'none',
                  fontWeight: 'bold', fontSize: '14px', transition: 'all 0.2s',
                  opacity: isDeleting ? 0.7 : 1
                }}
              >
                {isDeleting ? t('userProfile.deleteModal.deletingBtn') : t('userProfile.deleteModal.deleteBtn')}
              </button>
            </div>
          </div>
        </div>
      )}

    </div>
  );
};

export default UserProfile;