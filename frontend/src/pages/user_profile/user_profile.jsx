import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom'; // <-- 1. Importamos useNavigate
import { User, CheckCircle, Pencil, Save, X, Key, Mail, Trash2, Check } from 'lucide-react';
import styles from './user_profile.module.css';

const UserProfile = () => {
  const navigate = useNavigate(); // <-- 2. Inicializamos el hook de navegación

  const [userData, setUserData] = useState({
    first_name: '', last_name: '', email: '', organization: '', role_ids: []
  });

  // Estados de edición independientes
  const [isEditingInfo, setIsEditingInfo] = useState(false);
  const [tempInfo, setTempInfo] = useState({});

  const [isEditingRoles, setIsEditingRoles] = useState(false);
  const [tempRoles, setTempRoles] = useState([]);

  const [isVerified, setIsVerified] = useState(false);

  useEffect(() => {
    const savedUser = JSON.parse(localStorage.getItem('user')) || {
      first_name: 'Pepe', last_name: 'Fernández', email: 'pepe@gmail.com', organization: 'UC3M', role_ids: []
    };
    setUserData(savedUser);
    setTempInfo(savedUser);
    setTempRoles(savedUser.role_ids);
  }, []);

  // --- LÓGICA INFORMACIÓN PERSONAL ---
  const handleSaveInfo = () => {
    const updatedUser = { ...userData, ...tempInfo };
    setUserData(updatedUser);
    localStorage.setItem('user', JSON.stringify(updatedUser));
    setIsEditingInfo(false);
  };

  // --- LÓGICA DE ROLES ---
  const availableRoles = [
    { id: 1, name: "Gestor de alertas" },
    { id: 2, name: "Lector" }
  ];

  const handleEditRoles = () => setIsEditingRoles(true);

  const handleCancelRoles = () => {
    setTempRoles(userData.role_ids); // Revertir a los roles guardados
    setIsEditingRoles(false);
  };

  const handleSaveRoles = () => {
    const updatedUser = { ...userData, role_ids: tempRoles };
    setUserData(updatedUser);
    localStorage.setItem('user', JSON.stringify(updatedUser));
    setIsEditingRoles(false);
  };

  const toggleRole = (roleId) => {
    if (!isEditingRoles) return;
    if (tempRoles.includes(roleId)) {
      setTempRoles(tempRoles.filter(id => id !== roleId));
    } else {
      setTempRoles([...tempRoles, roleId]);
    }
  };

  return (
    <div className={styles.pageWrapper}>
      {/* BANNER SUPERIOR */}
      <div className={styles.headerBanner}>
        <div className={styles.userIconCircle}><User size={32} color="#FFFFFF" /></div>
        <div className={styles.userNameContainer}>
          <h1 className={styles.userName}>{userData.first_name} {userData.last_name}</h1>
          <CheckCircle size={24} color={isVerified ? "#90E0EF" : "#626262"} />
        </div>
      </div>

      <div className={styles.mainGrid}>
        <div className={styles.leftColumn}>

          {/* BLOQUE INFORMACIÓN PERSONAL */}
          <div className={styles.card} style={{ flex: 2 }}>
            <span className={styles.cardTitle}>Información Personal</span>
            <div className={styles.infoGrid}>
              <div className={styles.inputGroup}>
                <label>Nombre</label>
                <input type="text" name="first_name" value={tempInfo.first_name || ''}
                  onChange={(e) => setTempInfo({...tempInfo, first_name: e.target.value})}
                  disabled={!isEditingInfo} className={`${styles.inputField} ${isEditingInfo ? styles.activeInput : styles.disabledInput}`} />
              </div>
              <div className={styles.inputGroup}>
                <label>Apellidos</label>
                <input type="text" name="last_name" value={tempInfo.last_name || ''}
                  onChange={(e) => setTempInfo({...tempInfo, last_name: e.target.value})}
                  disabled={!isEditingInfo} className={`${styles.inputField} ${isEditingInfo ? styles.activeInput : styles.disabledInput}`} />
              </div>
              <div className={styles.inputGroup}>
                <label>Correo electrónico</label>
                <input type="email" value={userData.email} disabled className={`${styles.inputField} ${styles.emailInput}`} />
              </div>
              <div className={styles.inputGroup}>
                <label>Organización</label>
                <input type="text" name="organization" value={tempInfo.organization || ''}
                  onChange={(e) => setTempInfo({...tempInfo, organization: e.target.value})}
                  disabled={!isEditingInfo} className={`${styles.inputField} ${isEditingInfo ? styles.activeInput : styles.disabledInput}`} />
              </div>
            </div>
            <div className={styles.buttonContainer}>
              {!isEditingInfo ? (
                <button className={`${styles.btnAction} ${styles.btnDark}`} onClick={() => setIsEditingInfo(true)}>
                  <Pencil size={16} /> Editar
                </button>
              ) : (
                <>
                  <button className={`${styles.btnAction} ${styles.btnDanger}`} onClick={() => {setTempInfo(userData); setIsEditingInfo(false);}}>
                    <X size={16} /> Cancelar
                  </button>
                  <button className={`${styles.btnAction} ${styles.btnDark}`} onClick={handleSaveInfo}>
                    <Save size={16} /> Guardar
                  </button>
                </>
              )}
            </div>
          </div>

          {/* BLOQUE ROLES Y PERMISOS */}
          <div className={styles.card} style={{ flex: 1 }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
              <span className={styles.cardTitle}>Roles y Permisos</span>
              <div className={styles.buttonContainer} style={{marginTop: 0}}>
                {!isEditingRoles ? (
                  <button className={`${styles.btnAction} ${styles.btnDark}`} onClick={handleEditRoles}>
                    <Pencil size={16} /> Editar
                  </button>
                ) : (
                  <>
                    <button className={`${styles.btnAction} ${styles.btnDanger}`} onClick={handleCancelRoles}>
                      <X size={16} /> Cancelar
                    </button>
                    <button className={`${styles.btnAction} ${styles.btnDark}`} onClick={handleSaveRoles}>
                      <Save size={16} /> Guardar
                    </button>
                  </>
                )}
              </div>
            </div>

            <div className={`${styles.rolesList} ${!isEditingRoles ? styles.rolesDisabled : ''}`}>
              {availableRoles.map(role => {
                const isSelected = tempRoles.includes(role.id);
                return (
                  <div key={role.id} onClick={() => toggleRole(role.id)}
                    className={`${styles.roleItem} ${isSelected ? styles.roleSelected : styles.roleUnselected}`}>
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

        {/* BLOQUE SEGURIDAD */}
        <div className={`${styles.card} ${styles.securityCard}`}>
          <div className={styles.securityTopActions}>
            <span className={styles.cardTitle}>Seguridad</span>

            {/* <-- 3. Rutas añadidas a los onClick de Seguridad --> */}
            <button
              className={`${styles.btnAction} ${styles.btnDark}`}
              onClick={() => navigate('/recuperar-password')}
            >
              <Key size={18} /> Cambiar Contraseña
            </button>

            <button
              className={`${styles.btnAction} ${isVerified ? styles.btnGray : styles.btnDark}`}
              disabled={isVerified}
              onClick={() => navigate('/reenviar-verificacion')}
            >
              <Mail size={18} /> Verificar Email
            </button>
          </div>

          <button
            className={`${styles.btnAction} ${styles.btnDanger}`}
            onClick={() => navigate('/remove-acc')}
          >
            <Trash2 size={18} /> Eliminar Cuenta
          </button>
        </div>
      </div>
    </div>
  );
};

export default UserProfile;