// src/context/AuthContext.jsx
import { createContext, useState, useEffect, useCallback } from 'react';
import authService from '../services/authService';
import {
  getAllSourcesWithChannels,
  getWordcloudGlobal,
  getWordcloudCategory,
  createInformationSource,
  updateInformationSource,
  deleteInformationSource,
  createRSSChannel,
  updateRSSChannel,
  deleteRSSChannel,
  getUserAlerts,
  updateAlert,
  deleteAlert,
} from '../services/newsService';

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

  // ── Nube global ───────────────────────────────────────────────────────────
  // Llama al backend y devuelve [{ term, count }]
  const fetchNubeGlobal = useCallback(async (days = 30, limit = 20) => {
    const token = authService.getToken();
    return getWordcloudGlobal(token, days, limit);
  }, []);

  // ── Nube por categoría ────────────────────────────────────────────────────
  // categoria: 'culture' | 'politics' | ... (claves del backend)
  const fetchNubeCategoria = useCallback(async (categoria, days = 30, limit = 20) => {
    const token = authService.getToken();
    return getWordcloudCategory(categoria, token, days, limit);
  }, []);

  // ── CRUD: Fuentes ─────────────────────────────────────────────────────────
  // Tras cada mutación recargamos para que toda la UI vea los datos frescos.
  const createFuente = useCallback(async ({ name, url }) => {
    const token = authService.getToken();
    const res = await createInformationSource({ name, url }, token);
    await loadNewsData(token);
    return res.data;
  }, [loadNewsData]);

  const updateFuente = useCallback(async (sourceId, payload) => {
    const token = authService.getToken();
    const res = await updateInformationSource(sourceId, payload, token);
    await loadNewsData(token);
    return res.data;
  }, [loadNewsData]);

  const deleteFuente = useCallback(async (sourceId) => {
    const token = authService.getToken();
    await deleteInformationSource(sourceId, token);
    await loadNewsData(token);
  }, [loadNewsData]);

  // ── CRUD: Canales RSS ─────────────────────────────────────────────────────
  const createCanal = useCallback(async (sourceId, { url, category_id }) => {
    const token = authService.getToken();
    const res = await createRSSChannel(sourceId, { url, category_id }, token);
    await loadNewsData(token);
    return res.data;
  }, [loadNewsData]);

  const updateCanal = useCallback(async (sourceId, channelId, payload) => {
    const token = authService.getToken();
    const res = await updateRSSChannel(sourceId, channelId, payload, token);
    await loadNewsData(token);
    return res.data;
  }, [loadNewsData]);

  const deleteCanal = useCallback(async (sourceId, channelId) => {
    const token = authService.getToken();
    await deleteRSSChannel(sourceId, channelId, token);
    await loadNewsData(token);
  }, [loadNewsData]);

  // ── Alertas: lectura + mutaciones puntuales ───────────────────────────────
  // Estas funciones NO tocan el estado de fuentes/canales; las usamos sólo
  // para la cascada al borrar una fuente o un canal RSS.
  const fetchUserAlerts = useCallback(async () => {
    if (!user?.id) return [];
    const token = authService.getToken();
    const res = await getUserAlerts(user.id, token);
    return res.data;
  }, [user]);

  const updateAlertById = useCallback(async (alertId, payload) => {
    if (!user?.id) throw new Error('Usuario no disponible');
    const token = authService.getToken();
    const res = await updateAlert(user.id, alertId, payload, token);
    return res.data;
  }, [user]);

  const deleteAlertById = useCallback(async (alertId) => {
    if (!user?.id) throw new Error('Usuario no disponible');
    const token = authService.getToken();
    await deleteAlert(user.id, alertId, token);
  }, [user]);

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
        fetchNubeGlobal,
        fetchNubeCategoria,
        // CRUD Fuentes
        createFuente,
        updateFuente,
        deleteFuente,
        // CRUD Canales
        createCanal,
        updateCanal,
        deleteCanal,
        // Alertas (utilidades para cascada)
        fetchUserAlerts,
        updateAlertById,
        deleteAlertById,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
};