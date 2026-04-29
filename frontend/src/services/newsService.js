import axios from 'axios';

const API_URL = 'http://localhost:8000/api/v1';

export const getCategories = (token) => {
  return axios.get(`${API_URL}/categories`, {
    headers: { Authorization: `Bearer ${token}` }
  });
};

export const getInformationSources = (token) => {
  return axios.get(`${API_URL}/information-sources`, {
    headers: { Authorization: `Bearer ${token}` }
  });
};

export const getRSSChannels = (sourceId, token) => {
  return axios.get(`${API_URL}/information-sources/${sourceId}/rss-channels`, {
    headers: { Authorization: `Bearer ${token}` }
  });
};

export const getUserAlerts = (userId, token) => {
  return axios.get(`${API_URL}/users/${userId}/alerts`, {
    headers: { Authorization: `Bearer ${token}` }
  });
};

export const getAlertNotifications = (userId, alertId, token) => {
  return axios.get(`${API_URL}/users/${userId}/alerts/${alertId}/notifications`, {
    headers: { Authorization: `Bearer ${token}` }
  });
};