import React, { useState, useEffect, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import {
  Tooltip, ResponsiveContainer, Cell, PieChart, Pie, Legend
} from 'recharts';
import { ChevronRight, Loader2 } from 'lucide-react';
import authService from '../../services/authService';
import styles from './dashboard.module.css';

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000';
const PIE_COLORS = ['#0E0E1D', '#4CC9F0', '#B5179E', '#2A9D8F', '#F77F00', '#6C757D'];

const Dashboard = () => {
  const { t, i18n } = useTranslation();
  const navigate = useNavigate();
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(false);

  const fetchDashboardData = useCallback(async () => {
    setLoading(true);
    setError(false);
    try {
      const token = authService.getToken();
      if (!token) throw new Error('No hay token disponible');

      const response = await fetch(`${API_BASE}/api/v1/dashboard?days=7`, {
        headers: {
          Authorization: `Bearer ${token}`,
          Accept: 'application/json',
          'Accept-Language': i18n.language || navigator.language || 'es',
        },
      });

      if (!response.ok) {
        throw new Error(`HTTP Error: ${response.status}`);
      }

      const backendData = await response.json();
      setData({
        ...backendData,
        categorias: (backendData.categorias || []).map((item) => ({
          ...item,
          name: t(`categorias.${item.name}`, { defaultValue: item.name }),
        })),
      });
    } catch (err) {
      console.error('Error al cargar datos del dashboard:', err);
      setError(true);
    } finally {
      setLoading(false);
    }
  }, [i18n.language, t]);

  useEffect(() => {
    fetchDashboardData();
  }, [fetchDashboardData]);

  const CustomPieTooltip = ({ active, payload }) => {
    if (active && payload && payload.length) {
      return (
        <div className={styles.customTooltip}>
          <p className={styles.tooltipLabel}>{payload[0].name}</p>
          <p className={styles.tooltipValue}>{`${t('dashboard.charts.newsLabel')}${payload[0].value}`}</p>
          <p className={styles.tooltipValue}>
            {`${t('dashboard.charts.alertsLabel', { defaultValue: 'Alertas: ' })}${payload[0].payload?.alertas || 0}`}
          </p>
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
            {data.noticias?.semana || 0}
          </span>
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
          <span className={styles.cardTitle}>
            {t('dashboard.charts.categoryCountersTitle', { defaultValue: 'RESUMEN POR CATEGORIA' })}
          </span>
          <div className={styles.categoryStatsList}>
            {(data.categorias || []).length === 0 ? (
              <div className={styles.emptyStats}>
                {t('dashboard.charts.noCategoryData', { defaultValue: 'Sin datos por categoria' })}
              </div>
            ) : (
              data.categorias.map((item) => (
                <div className={styles.categoryStatRow} key={item.key}>
                  <span className={styles.categoryName}>{item.name}</span>
                  <span className={styles.categoryMetric}>
                    <strong>{item.value || 0}</strong> {t('dashboard.charts.news', { defaultValue: 'Noticias' })}
                  </span>
                  <span className={styles.categoryMetric}>
                    <strong>{item.alertas || 0}</strong> {t('dashboard.charts.alerts', { defaultValue: 'Alertas' })}
                  </span>
                </div>
              ))
            )}
          </div>
        </div>

        <div className={`${styles.card} ${styles.largeCard}`}>
          <span className={styles.cardTitle}>{t('dashboard.charts.categoriesTitle')}</span>
          <div className={styles.chartContainer}>
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
                    <Cell key={entry.key} fill={PIE_COLORS[index % PIE_COLORS.length]} />
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
