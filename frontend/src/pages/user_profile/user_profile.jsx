import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { User, CheckCircle, Pencil, Save, X, Key, Mail, Trash2, Check } from 'lucide-react';
import styles from './user_profile.module.css';
import { checkVerificationStatus } from '../../services/userService';
import authService from '../../services/authService';

const UserProfile = () => {
  const navigate = useNavigate();

  const [userData, setUserData] = useState({
    first_name: '', last_name: '', email: '', organization: '', role_ids: []
  });

  const [isEditingInfo, setIsEditingInfo] = useState(false);
  const [tempInfo, setTempInfo] = useState({});

  const [isEditingRoles, setIsEditingRoles] = useState(false);
  const [tempRoles, setTempRoles] = useState([]);

  const [isVerified, setIsVerified] = useState(false);

  useEffect(() => {
    const savedUser = JSON.parse(localStorage.getItem('user')) || {
      first_name: '-',
      last_name: '-',
      email: '-',
      organization: '-',
      role_ids: []
    };

    setUserData(savedUser);
    setTempInfo(savedUser);
    setTempRoles(savedUser.role_ids);

    // Llamada al servicio para comprobar verificación
    if (savedUser.email) {
      const token = authService.getToken();
      checkVerificationStatus(savedUser.email, token)
        .then(status => setIsVerified(status))
        .catch(err => console.error(err));
    }
  }, []);

  // --- Manejo de información personal ---
  const handleSaveInfo = () => {
    const updatedUser = { ...userData, ...tempInfo };
    setUserData(updatedUser);
    localStorage.setItem('user', JSON.stringify(updatedUser));
    setIsEditingInfo(false);
  };

  // --- Manejo de roles ---
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
              {/* Nombre, Apellidos, Email, Organización */}
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
          <button className={`${styles.btnAction} ${styles.btnDanger}`} onClick={() => navigate('/remove-acc')}>
            <Trash2 size={18} /> Eliminar Cuenta
          </button>
        </div>
      </div>
    </div>
  );
};

export default UserProfile;