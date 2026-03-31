import { createContext, useState, useEffect } from 'react';
import { jwtDecode } from 'jwt-decode';
import authService from '../services/authService';

// Creamos el contexto
export const AuthContext = createContext();

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  // Al cargar la app, comprobamos si ya hay un token guardado de antes
  useEffect(() => {
    const token = authService.getToken();
    if (token) {
      try {
        const decoded = jwtDecode(token);
        // Comprobamos si el token ha caducado ("exp" es expiration)
        if (decoded.exp * 1000 < Date.now()) {
          authService.logout();
          setUser(null);
        } else {
          // El token es válido, guardamos los datos del usuario (id, roles, etc)
          setUser(decoded);
        }
      } catch (error) {
        console.error("Token inválido");
        authService.logout();
      }
    }
    setLoading(false);
  }, []);

  // Función que usaremos desde el formulario de Login
  const login = async (username, password) => {
    const data = await authService.login(username, password);
    const decoded = jwtDecode(data.access_token);
    setUser(decoded);
  };

  const logout = () => {
    authService.logout();
    setUser(null);
  };

  return (
    <AuthContext.Provider value={{ user, login, logout, loading }}>
      {children}
    </AuthContext.Provider>
  );
};