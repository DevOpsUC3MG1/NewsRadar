import axios from 'axios';

// AJUSTA ESTA URL a la ruta real de tu backend local (por ejemplo, http://localhost:8000/api)
const API_URL = 'http://localhost:8000/api'; 

const login = async (username, password) => {
  // Hacemos la petición POST al backend
  const response = await axios.post(`${API_URL}/login`, { username, password });
  
  // Si el backend nos devuelve el token, lo guardamos en el navegador
  if (response.data.access_token) {
    localStorage.setItem('token', response.data.access_token);
  }
  return response.data;
};

const logout = () => {
  // Para cerrar sesión, simplemente borramos el token
  localStorage.removeItem('token');
};

const getToken = () => {
  return localStorage.getItem('token');
};

export default { login, logout, getToken };