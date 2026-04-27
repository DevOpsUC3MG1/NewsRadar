import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { User, CheckCircle, Pencil, Save, X, Key, Mail, Trash2, Check, AlertTriangle } from 'lucide-react';
import styles from './user_profile.module.css';
import { checkVerificationStatus, deleteUserAccount } from '../../services/userService';
import authService from '../../services/authService';

const UserProfile = () => {
  const navigate = useNavigate();

  const [userData, setUserData] = useState({
    id: null, first_name: '', last_name: '', email: '', organization: '', role_ids: []
  });

  const [isEditingInfo, setIsEditingInfo] = useState(false);
  const [tempInfo, setTempInfo] = useState({});

  const [isEditingRoles, setIsEditingRoles] = useState(false);
  const [tempRoles, setTempRoles] = useState([]);

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
      role_ids: []
    };

    setUserData(savedUser);
    setTempInfo(savedUser);
    setTempRoles(savedUser.role_ids);

    if (savedUser.email) {
      const token = authService.getToken();
      checkVerificationStatus(savedUser.email, token)
        .then(status => setIsVerified(status))
        .catch(err => console.error(err));
    }
  }, []);

  const handleSaveInfo = () => {
    const updatedUser = { ...userData, ...tempInfo };
    setUserData(updatedUser);
    localStorage.setItem('user', JSON.stringify(updatedUser));
    setIsEditingInfo(false);
  };

  const availableRoles = [
    { id: 1, name: "Gestor de alertas" },
    { id: 2, name: "Lector" }
  ];

  const handleEditRoles = () => setIsEditingRoles(true);
  const handleCancelRoles = () => { setTempRoles(userData.role_ids); setIsEditingRoles(false); };
  const handleSaveRoles = () => {
    const updatedUser = { ...userData, role_ids: tempRoles };
    setUserData(updatedUser);
    localStorage.setItem('user', JSON.stringify(updatedUser));
    setIsEditingRoles(false);
  };

  const toggleRole = (roleId) => {
    if (!isEditingRoles) return;
    setTempRoles(tempRoles.includes(roleId) ? tempRoles.filter(id => id !== roleId) : [...tempRoles, roleId]);
  };

  // --- LÓGICA PARA ELIMINAR CUENTA ---
  const handleDeleteAccount = async () => {
    if (confirmEmail !== userData.email) {
      setDeleteError('El correo electrónico no coincide.');
      return;
    }

    if (!userData.id) {
      setDeleteError('Error: No se ha encontrado el ID del usuario.');
      return;
    }

    setIsDeleting(true);
    setDeleteError('');

    try {
      const token = authService.getToken();
      await deleteUserAccount(userData.id, token);

      // Limpiamos los datos de sesión y redirigimos a la pantalla de entrada
      localStorage.removeItem('user');
      localStorage.removeItem('token');
      navigate('/');

      // Forzamos la recarga para que el AuthContext se limpie completamente
      window.location.reload();
    } catch (error) {
      setDeleteError('Error al eliminar la cuenta. Inténtalo de nuevo.');
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
            <span className={styles.cardTitle}>Información Personal</span>
            <div className={styles.infoGrid}>
              {['first_name','last_name','organization'].map(field => (
                <div key={field} className={styles.inputGroup}>
                  <label>{field.replace('_',' ').toUpperCase()}</label>
                  <input
                    type="text"
                    name={field}
                    value={tempInfo[field] || ''}
                    onChange={e => setTempInfo({...tempInfo, [field]: e.target.value})}
                    disabled={!isEditingInfo}
                    className={`${styles.inputField} ${isEditingInfo ? styles.activeInput : styles.disabledInput}`}
                  />
                </div>
              ))}
              <div className={styles.inputGroup}>
                <label>Correo electrónico</label>
                <input type="email" value={userData.email} disabled className={`${styles.inputField} ${styles.emailInput}`} />
              </div>
            </div>
            <div className={styles.buttonContainer}>
              {!isEditingInfo ? (
                <button className={`${styles.btnAction} ${styles.btnDark}`} onClick={() => setIsEditingInfo(true)}>
                  <Pencil size={16} /> Editar
                </button>
              ) : (
                <>
                  <button className={`${styles.btnAction} ${styles.btnDanger}`} onClick={() => { setTempInfo(userData); setIsEditingInfo(false); }}>
                    <X size={16} /> Cancelar
                  </button>
                  <button className={`${styles.btnAction} ${styles.btnDark}`} onClick={handleSaveInfo}>
                    <Save size={16} /> Guardar
                  </button>
                </>
              )}
            </div>
          </div>

          {/* Roles */}
          <div className={styles.card} style={{ flex: 1 }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
              <span className={styles.cardTitle}>Roles y Permisos</span>
              <div className={styles.buttonContainer} style={{ marginTop: 0 }}>
                {!isEditingRoles ? (
                  <button className={`${styles.btnAction} ${styles.btnDark}`} onClick={handleEditRoles}><Pencil size={16}/> Editar</button>
                ) : (
                  <>
                    <button className={`${styles.btnAction} ${styles.btnDanger}`} onClick={handleCancelRoles}><X size={16}/> Cancelar</button>
                    <button className={`${styles.btnAction} ${styles.btnDark}`} onClick={handleSaveRoles}><Save size={16}/> Guardar</button>
                  </>
                )}
              </div>
            </div>
            <div className={`${styles.rolesList} ${!isEditingRoles ? styles.rolesDisabled : ''}`}>
              {availableRoles.map(role => {
                const isSelected = tempRoles.includes(role.id);
                return (
                  <div key={role.id} onClick={() => toggleRole(role.id)} className={`${styles.roleItem} ${isSelected ? styles.roleSelected : styles.roleUnselected}`}>
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
            <span className={styles.cardTitle}>Seguridad</span>
            <button className={`${styles.btnAction} ${styles.btnDark}`} onClick={() => navigate('/recuperar-password')}>
              <Key size={18} /> Cambiar Contraseña
            </button>
            <button className={`${styles.btnAction} ${isVerified ? styles.btnGray : styles.btnDark}`} disabled={isVerified} onClick={() => navigate('/reenviar-verificacion')}>
              <Mail size={18} /> Verificar Email
            </button>
          </div>
          {/* Cambiamos la acción para abrir el modal en lugar de navegar */}
          <button className={`${styles.btnAction} ${styles.btnDanger}`} onClick={() => setShowDeleteModal(true)}>
            <Trash2 size={18} /> Eliminar Cuenta
          </button>
        </div>
      </div>

      {/* MODAL DE ELIMINAR CUENTA */}
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
            <h2 style={{ color: '#0E0E1D', marginBottom: '10px', fontSize: '24px' }}>¿Está seguro de eliminar la cuenta?</h2>
            <p style={{ color: '#626262', marginBottom: '20px', fontSize: '15px', lineHeight: '1.5' }}>
              Esta acción no se puede deshacer. Todos tus datos y alertas serán borrados permanentemente.
              Para confirmar, escribe tu correo electrónico: <strong>{userData.email}</strong>
            </p>

            <input
              type="email"
              placeholder="Escribe tu correo aquí..."
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
              {/* BOTÓN MANTENER */}
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
                MANTENER
              </button>

              {/* BOTÓN BORRAR CUENTA */}
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
                {isDeleting ? 'BORRANDO...' : 'BORRAR CUENTA'}
              </button>
            </div>
          </div>
        </div>
      )}

    </div>
  );
};

export default UserProfile;