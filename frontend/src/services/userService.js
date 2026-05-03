// frontend/src/services/userService.js
import axios from 'axios';

const API_URL = import.meta.env.VITE_API_URL
  ? `${import.meta.env.VITE_API_URL}/api/v1`
  : 'http://localhost:8000/api/v1';

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
    throw error;
  }
};

// NUEVA FUNCIÓN: Actualizar datos del usuario
export const updateUser = async (userId, userData, token) => {
  try {
    const response = await axios.put(`${API_URL}/users/${userId}`, userData, {
      headers: {
        Authorization: `Bearer ${token}`
      }
    });
    return response.data;
  } catch (error) {
    console.error('Error al actualizar el usuario:', error);
    throw error;
  }
};