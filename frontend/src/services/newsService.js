// src/services/newsService.js
import axios from 'axios';

const API_URL = 'http://localhost:8000/api/v1';

// ─── Helpers básicos ──────────────────────────────────────────────────────────
export const getCategories = (token) =>
  axios.get(`${API_URL}/categories`, {
    headers: { Authorization: `Bearer ${token}` },
  });

export const getInformationSources = (token) =>
  axios.get(`${API_URL}/information-sources`, {
    headers: { Authorization: `Bearer ${token}` },
  });

export const getRSSChannels = (sourceId, token) =>
  axios.get(`${API_URL}/information-sources/${sourceId}/rss-channels`, {
    headers: { Authorization: `Bearer ${token}` },
  });

export const getUserAlerts = (userId, token) =>
  axios.get(`${API_URL}/users/${userId}/alerts`, {
    headers: { Authorization: `Bearer ${token}` },
  });

export const getAlertNotifications = (userId, alertId, token) =>
  axios.get(`${API_URL}/users/${userId}/alerts/${alertId}/notifications`, {
    headers: { Authorization: `Bearer ${token}` },
  });

// ─── Nubes de palabras ────────────────────────────────────────────────────────

// Nube global: términos más frecuentes de las noticias del usuario
// Devuelve: [{ term: string, count: number }]
export const getWordcloudGlobal = (token, days = 30, limit = 20) =>
  axios.get(`${API_URL}/resumen/clouds/global`, {
    params: { days, limit },
    headers: {
      Authorization: `Bearer ${token}`,
      'Accept-Language': navigator.language || 'es',
    },
  }).then((res) => res.data);

// Nube por categoría
// categoria: 'culture' | 'consumption' | 'sports' | 'economy' | 'entertainment'
//            'government' | 'international' | 'national' | 'politics' | 'technology'
// Devuelve: [{ term: string, count: number }]
export const getWordcloudCategory = (categoria, token, days = 30, limit = 20) =>
  axios.get(`${API_URL}/resumen/clouds/${categoria}`, {
    params: { days, limit },
    headers: {
      Authorization: `Bearer ${token}`,
      'Accept-Language': navigator.language || 'es',
    },
  }).then((res) => res.data);

// ─── Función compuesta: fuentes + canales + categorías ───────────────────────
export const getAllSourcesWithChannels = async (token) => {
  const [sourcesRes, catsRes] = await Promise.all([
    getInformationSources(token),
    getCategories(token),
  ]);

  const rawSources = sourcesRes.data;
  const rawCats    = catsRes.data;
  const catMap = Object.fromEntries(rawCats.map((c) => [c.id, c.name]));

  const channelsPerSource = await Promise.all(
    rawSources.map((src) =>
      getRSSChannels(src.id, token)
        .then((res) => ({ sourceId: src.id, sourceName: src.name, channels: res.data }))
        .catch(() => ({ sourceId: src.id, sourceName: src.name, channels: [] }))
    )
  );

  let canalId = 0;
  const canales = channelsPerSource.flatMap(({ sourceId, sourceName, channels }) =>
    channels.map((ch) => {
      const urlPath  = ch.url.toString().replace(/\/$/, '');
      const segments = urlPath.split('/').filter(Boolean);
      const lastSeg  = segments[segments.length - 1]
        .replace(/\.(xml|html|aspx)$/i, '')
        .replace(/[-_]/g, ' ')
        .replace(/\b\w/g, (l) => l.toUpperCase());
      const seccion = lastSeg && lastSeg.toLowerCase() !== 'rss' ? lastSeg : 'General';
      return {
        id:         ch.id ?? ++canalId,
        fuenteId:   sourceId,
        nombre:     `${sourceName} – ${seccion}`,
        categoria:  catMap[ch.category_id] ?? String(ch.category_id),
        _backendId: ch.id,
      };
    })
  );

  const fuentes = rawSources.map((src) => {
    const srcChannels = channelsPerSource.find((c) => c.sourceId === src.id)?.channels ?? [];
    const cats = [...new Set(srcChannels.map((ch) => catMap[ch.category_id]).filter(Boolean))].sort();
    return { id: src.id, nombre: src.name, url: src.url, categorias: cats };
  });

  return { fuentes, canales, categorias: rawCats };
};