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