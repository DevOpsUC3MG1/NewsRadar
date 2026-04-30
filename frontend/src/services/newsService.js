// src/services/newsService.js
import axios from 'axios';

const API_URL = 'http://localhost:8000/api/v1';

// ─── Helpers básicos (sin cambios) ───────────────────────────────────────────
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

// ─── Función compuesta: fuentes + canales + categorías en una sola llamada ───
//
// Devuelve:
// {
//   fuentes:    [{ id, nombre, url, categorias: ['Politica', ...] }],
//   canales:    [{ id, fuenteId, nombre, categoria: 'Politica' }],
//   categorias: [{ id, name, source }],
// }
export const getAllSourcesWithChannels = async (token) => {
  // 1. Lanzar fuentes y categorías en paralelo
  const [sourcesRes, catsRes] = await Promise.all([
    getInformationSources(token),
    getCategories(token),
  ]);

  const rawSources = sourcesRes.data;          // [{ id, name, url }]
  const rawCats    = catsRes.data;             // [{ id, name, source }]

  // Mapa id → nombre de categoría para resolver category_id → string
  const catMap = Object.fromEntries(rawCats.map((c) => [c.id, c.name]));

  // 2. Para cada fuente obtener sus canales en paralelo
  const channelsPerSource = await Promise.all(
    rawSources.map((src) =>
      getRSSChannels(src.id, token)
        .then((res) => ({ sourceId: src.id, sourceName: src.name, channels: res.data }))
        .catch(() => ({ sourceId: src.id, sourceName: src.name, channels: [] }))
    )
  );

  // 3. Construir array plano de canales con nombre legible
  let canalId = 0;
  const canales = channelsPerSource.flatMap(({ sourceId, sourceName, channels }) =>
    channels.map((ch) => {
      // Derivar sección del canal a partir de la URL (último segmento útil)
      const urlPath = ch.url.toString().replace(/\/$/, '');
      const segments = urlPath.split('/').filter(Boolean);
      const lastSeg  = segments[segments.length - 1]
        .replace(/\.(xml|html|aspx)$/i, '')
        .replace(/[-_]/g, ' ')
        .replace(/\b\w/g, (l) => l.toUpperCase());

      const seccion = lastSeg && lastSeg.toLowerCase() !== 'rss' ? lastSeg : 'General';

      return {
        id:       ch.id ?? ++canalId,
        fuenteId: sourceId,
        nombre:   `${sourceName} – ${seccion}`,
        categoria: catMap[ch.category_id] ?? String(ch.category_id),
        // Guardamos el id original del backend por si se necesita para otras llamadas
        _backendId: ch.id,
      };
    })
  );

  // 4. Derivar categorías únicas por fuente (para el filtro lateral de fuentes.jsx)
  const fuentes = rawSources.map((src) => {
    const srcChannels = channelsPerSource.find((c) => c.sourceId === src.id)?.channels ?? [];
    const cats = [...new Set(srcChannels.map((ch) => catMap[ch.category_id]).filter(Boolean))].sort();
    return {
      id:         src.id,
      nombre:     src.name,
      url:        src.url,
      categorias: cats,
    };
  });

  return { fuentes, canales, categorias: rawCats };
};