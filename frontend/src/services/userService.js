// frontend/src/services/userService.js
import axios from 'axios';

const API_URL = 'http://localhost:8000/api/v1';

export const checkVerificationStatus = async (email, token) => {
  try {
    const response = await axios.get(`${API_URL}/users/email/${email}/verification-status`, {
      headers: {
        Authorization: `Bearer ${token}`
      }
    });
    return response.data.is_verified;
  } catch (error) {
    console.error('Error al comprobar la verificación:', error);
    return false;
  }
};

// NUEVA FUNCIÓN: Eliminar cuenta de usuario
export const deleteUserAccount = async (userId, token) => {
  try {
    const response = await axios.delete(`${API_URL}/users/${userId}`, {
      headers: {
        Authorization: `Bearer ${token}`
      }
    });
    return response.data;
  } catch (error) {
    console.error('Error al eliminar la cuenta:', error);
    throw error; // Lanzamos el error para capturarlo en el componente
  }
};