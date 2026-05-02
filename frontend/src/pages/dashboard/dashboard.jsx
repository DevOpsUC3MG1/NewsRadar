import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
  Cell, PieChart, Pie, Legend
} from 'recharts';
import { ChevronRight, Loader2 } from 'lucide-react';
import authService from '../../services/authService';
import styles from './dashboard.module.css';

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const Dashboard = () => {
  const { t, i18n } = useTranslation();
  const navigate = useNavigate();
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(false);
  const [newsFilter, setNewsFilter] = useState('7D');

  const fetchDashboardData = async () => {
    setLoading(true);
    setError(false);
    try {
      const token = authService.getToken();
      if (!token) throw new Error("No hay token disponible");

      const days = newsFilter === '1D' ? 1 : 7;

      const response = await fetch(`${API_BASE}/api/v1/dashboard?days=${days}`, {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Accept': 'application/json',
          'Accept-Language': i18n.language || navigator.language || 'es'
        }
      });

      if (!response.ok) {
        throw new Error(`HTTP Error: ${response.status}`);
      }

      const backendData = await response.json();

      // --- DICCIONARIOS DE NORMALIZACIÓN ---
      // Evita los errores de "missingKey" de i18next traduciendo del backend a tu JSON
      const dayMap = { lun: 'mon', mar: 'tue', mie: 'wed', jue: 'thu', vie: 'fri', sab: 'sat', dom: 'sun' };
      const catMap = { politica: 'politics', economia: 'economy', salud: 'health', tecnologia: 'tech', tecno: 'tech' };

      const translatedData = {
        ...backendData,
        evolucion: backendData.evolucion?.map(item => {
          const rawName = item.name?.toLowerCase() || '';
          const mappedKey = dayMap[rawName] || rawName;
          return {
            ...item,
            name: t(`dashboard.days.${mappedKey}`, { defaultValue: item.name })
          };
        }) || [],
        categorias: backendData.categorias?.map(item => {
          const rawName = item.name?.toLowerCase() || '';
          const mappedKey = catMap[rawName] || rawName;
          return {
            ...item,
            name: t(`dashboard.categories.${mappedKey}`, { defaultValue: item.name })
          };
        }) || []
      };

      setData(translatedData);
    } catch (err) {
      console.error("Error al cargar datos del dashboard:", err);
      setError(true);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchDashboardData();
  }, [t, newsFilter]);

  const CustomPieTooltip = ({ active, payload }) => {
    if (active && payload && payload.length) {
      return (
        <div className={styles.customTooltip}>
          <p className={styles.tooltipLabel}>{`${payload[0].name}`}</p>
          <p className={styles.tooltipValue}>{`${t('dashboard.charts.newsLabel')}${payload[0].value}`}</p>
        </div>
      );
    }
    return null;
  };

  if (error) {
    return (
      <div className={styles.dashboardWrapper}>
        <div className={styles.errorContainer}>
          <h2>{t('dashboard.errorTitle')}</h2>
          <button className={styles.retryButton} onClick={fetchDashboardData}>
            {t('dashboard.retryBtn')}
          </button>
        </div>
      </div>
    );
  }

  if (loading || !data) {
    return (
      <div className={styles.dashboardWrapper}>
        <div className={styles.loadingOverlay}>
          <Loader2 className={styles.spinner} size={48} />
          <p>{t('dashboard.loading')}</p>
        </div>
      </div>
    );
  }

  return (
    <div className={styles.dashboardWrapper}>
      <h1 className={styles.pageTitle}>{t('dashboard.title')}</h1>

      <div className={styles.topRow}>
        <div className={styles.card}>
          <span className={styles.cardTitle}>{t('dashboard.sourcesCard.title')}</span>
          <div className={styles.sourcesList}>
            <div className={styles.sourceItem}>
              <span>{t('dashboard.sourcesCard.active')}</span>
              <span className={styles.sourceValue}>{data.fuentes?.activas || 0}</span>
            </div>
            <div className={styles.sourceItem}>
              <span>{t('dashboard.sourcesCard.rss')}</span>
              <span className={styles.sourceValue}>{data.fuentes?.rss || 0}</span>
            </div>
          </div>
          <button className={styles.btnNavigate} onClick={() => navigate('/fuentes')}>
            {t('dashboard.sourcesCard.goBtn')} <ChevronRight size={14} />
          </button>
        </div>

        <div className={styles.card}>
          <span className={styles.cardTitle}>{t('dashboard.newsCard.title')}</span>
          <span className={styles.metricValue}>
            {newsFilter === '1D' ? (data.noticias?.hoy || 0) : (data.noticias?.semana || 0)}
          </span>
          <div className={styles.filterContainer}>
            <button
              className={newsFilter === '1D' ? styles.filterBtnActive : styles.filterBtnInactive}
              onClick={() => setNewsFilter('1D')}
            >1D</button>
            <button
              className={newsFilter === '7D' ? styles.filterBtnActive : styles.filterBtnInactive}
              onClick={() => setNewsFilter('7D')}
            >7D</button>
          </div>
        </div>

        <div className={styles.card}>
          <span className={styles.cardTitle}>{t('dashboard.alertsCard.title')}</span>
          <span className={styles.metricValue}>{data.alertas || 0}</span>
          <button className={styles.btnNavigate} onClick={() => navigate('/alerts')}>
            {t('dashboard.alertsCard.goBtn')} <ChevronRight size={14} />
          </button>
        </div>
      </div>

      <div className={styles.bottomRow}>
        <div className={`${styles.card} ${styles.largeCard}`}>
          <span className={styles.cardTitle}>{t('dashboard.charts.evolutionTitle')}</span>
          <div className={styles.chartContainer} style={{ width: '100%', height: '300px', minHeight: '300px' }}>
            {/* SOLUCIÓN AL WARNING: minWidth={1} y minHeight={1} obligan a recharts a no leer valores negativos iniciales */}
            <ResponsiveContainer width="100%" height="100%" minWidth={1} minHeight={1}>
              <BarChart data={data.evolucion}>
                <CartesianGrid strokeDasharray="3 3" vertical={false} />
                <XAxis dataKey="name" axisLine={false} tickLine={false} />
                <YAxis axisLine={false} tickLine={false} />
                <Tooltip cursor={{fill: '#f0f0f0'}} />
                <Bar dataKey="noticias" name={t('dashboard.charts.news')} fill="#0088FE" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        <div className={`${styles.card} ${styles.largeCard}`}>
          <span className={styles.cardTitle}>{t('dashboard.charts.categoriesTitle')}</span>
          <div className={styles.chartContainer} style={{ width: '100%', height: '300px', minHeight: '300px' }}>
             {/* SOLUCIÓN AL WARNING */}
            <ResponsiveContainer width="100%" height="100%" minWidth={1} minHeight={1}>
              <PieChart>
                <Pie
                  data={data.categorias}
                  innerRadius={60}
                  outerRadius={85}
                  paddingAngle={5}
                  dataKey="value"
                >
                  {data.categorias?.map((entry, index) => (
                    <Cell key={index} fill={['#0E0E1D', '#4CC9F0', '#B5179E', '#7209B7'][index % 4]} />
                  ))}
                </Pie>
                <Tooltip content={<CustomPieTooltip />} />
                <Legend verticalAlign="bottom" />
              </PieChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;