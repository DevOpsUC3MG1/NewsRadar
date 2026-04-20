import { createContext, useState, useEffect } from 'react';
import authService from '../services/authService';

// Creamos el contexto
export const AuthContext = createContext();

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  // Al cargar la app, comprobamos si ya hay un token guardado de antes
  useEffect(() => {
    const token = authService.getToken();
    const storedUser = localStorage.getItem('user');

    // Comprobamos si hay token y datos de usuario guardados
    if (token && storedUser) {
      setUser(JSON.parse(storedUser));
    } else {
      authService.logout();
    }
    setLoading(false);
  }, []);

  // Función que usaremos desde login.jsx
  const login = async (email, password) => {
    // 1. Hacemos login en la API y conseguimos el token UUID
    const data = await authService.login(email, password);
    
    // 2. Con el token en mano, buscamos los datos del perfil usando el email
    const userData = await authService.getUserByEmail(email, data.access_token);
    
    if (userData) {
      // 3. Guardamos el usuario en el estado y en LocalStorage
      setUser(userData);
      localStorage.setItem('user', JSON.stringify(userData));
    } else {
      // Si por algún motivo no encontramos el usuario, forzamos error
      throw new Error("No se pudo recuperar el perfil del usuario.");
    }
  };

  const registerUser = async (userData) => {
    // Registramos en la API
    const newUser = await authService.register(userData);
    
    // Auto-login silencioso para conseguir el token
    await authService.login(userData.email, userData.password);

    // Guardamos el usuario
    setUser(newUser);
    localStorage.setItem('user', JSON.stringify(newUser));
    return newUser;
  };

  const logout = () => {
    authService.logout();
    setUser(null);
  };

  return (
    <AuthContext.Provider value={{ user, login, registerUser, logout, loading }}>
      {children}
    </AuthContext.Provider>
  );
};