// src/context/AuthContext.jsx
import { createContext, useState, useEffect, useCallback } from 'react';
import authService from '../services/authService';
import { getAllSourcesWithChannels } from '../services/newsService';

export const AuthContext = createContext();

export const AuthProvider = ({ children }) => {
  const [user, setUser]           = useState(null);
  const [loading, setLoading]     = useState(true);

  // ── Datos de fuentes/canales/categorías compartidos ───────────────────────
  const [fuentes,    setFuentes]    = useState([]);
  const [canales,    setCanales]    = useState([]);
  const [categorias, setCategorias] = useState([]);
  const [newsLoading, setNewsLoading] = useState(false);
  const [newsError,   setNewsError]   = useState(false);

  // ── Carga de fuentes + canales + categorías ───────────────────────────────
  const loadNewsData = useCallback(async (token) => {
    if (!token) return;
    setNewsLoading(true);
    setNewsError(false);
    try {
      const { fuentes, canales, categorias } = await getAllSourcesWithChannels(token);
      setFuentes(fuentes);
      setCanales(canales);
      setCategorias(categorias);
    } catch (err) {
      console.error('Error cargando fuentes/canales:', err);
      setNewsError(true);
    } finally {
      setNewsLoading(false);
    }
  }, []);

  // ── Al arrancar la app, restaurar sesión si hay token guardado ────────────
  useEffect(() => {
    const token      = authService.getToken();
    const storedUser = localStorage.getItem('user');

    if (token && storedUser) {
      const parsedUser = JSON.parse(storedUser);
      setUser(parsedUser);
      // Cargar datos de fuentes con el token existente
      loadNewsData(token);
    } else {
      authService.logout();
    }
    setLoading(false);
  }, [loadNewsData]);

  // ── Login ─────────────────────────────────────────────────────────────────
  const login = async (email, password) => {
    const data     = await authService.login(email, password);
    const userData = await authService.getUserByEmail(email, data.access_token);

    if (userData) {
      setUser(userData);
      localStorage.setItem('user', JSON.stringify(userData));
      // Cargar fuentes/canales justo después del login
      await loadNewsData(data.access_token);
    } else {
      throw new Error('No se pudo recuperar el perfil del usuario.');
    }
  };

  // ── Registro ──────────────────────────────────────────────────────────────
  const registerUser = async (userData) => {
    const newUser = await authService.register(userData);
    return newUser;
  };

  // ── Logout ────────────────────────────────────────────────────────────────
  const logout = () => {
    authService.logout();
    setUser(null);
    setFuentes([]);
    setCanales([]);
    setCategorias([]);
  };

  // ── Recarga manual (útil si el usuario quiere refrescar los datos) ────────
  const refreshNewsData = () => {
    const token = authService.getToken();
    return loadNewsData(token);
  };

  return (
    <AuthContext.Provider
      value={{
        // Auth
        user,
        loading,
        login,
        registerUser,
        logout,
        // Fuentes / Canales / Categorías
        fuentes,
        canales,
        categorias,
        newsLoading,
        newsError,
        refreshNewsData,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
};