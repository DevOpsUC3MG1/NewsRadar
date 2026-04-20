import axios from 'axios';

// AJUSTA ESTA URL a la ruta real de tu backend local (por ejemplo, http://localhost:8000/api)
const API_URL = 'http://localhost:8000/api'; 

const login = async (email, password) => {
  // Hacemos la petición POST al backend
  const response = await axios.post(`${API_URL}/v1/auth/login`, { email, password });
  
  // Si el backend nos devuelve el token, lo guardamos en el navegador
  if (response.data.access_token) {
    localStorage.setItem('token', response.data.access_token);
  }
  return response.data;
};

const register = async (userData) => {
  // userData debe coincidir con el esquema 'UserCreate' de FastAPI
  const response = await axios.post(`${API_URL}/v1/auth/register`, userData);
  return response.data;
};

const getUserByEmail = async (email, token) => {
  const response = await axios.get(`${API_URL}/v1/users`, {
    headers: {
      Authorization: `Bearer ${token}`
    }
  });
  
  // Filtramos la lista de usuarios para devolver solo el nuestro
  return response.data.find(user => user.email === email);
};

const logout = () => {
  // Para cerrar sesión, simplemente borramos el token
  localStorage.removeItem('token');
  localStorage.removeItem('user');
};

const getToken = () => {
  return localStorage.getItem('token');
};

export default { login, logout, register, getUserByEmail, getToken };