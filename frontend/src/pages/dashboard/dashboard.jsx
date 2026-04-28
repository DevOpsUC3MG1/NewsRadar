import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
  Cell, PieChart, Pie, Legend
} from 'recharts';
import { ChevronRight, Loader2 } from 'lucide-react';
import styles from './dashboard.module.css';

const Dashboard = () => {
  const { t } = useTranslation();
  const navigate = useNavigate();
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(false);
  const [newsFilter, setNewsFilter] = useState('7D');

  const fetchDashboardData = async () => {
    setLoading(true);
    setError(false);
    try {
      // Simulación de carga
      await new Promise(resolve => setTimeout(resolve, 1500));

      // Aplicamos traducciones a los datos simulados para las gráficas
      const response = {
        fuentes: { activas: 12, rss: 104 },
        noticias: { hoy: 145, semana: "1,420" },
        alertas: 8,
        evolucion: [
          { name: t('dashboard.days.mon'), noticias: 45 }, { name: t('dashboard.days.tue'), noticias: 52 },
          { name: t('dashboard.days.wed'), noticias: 38 }, { name: t('dashboard.days.thu'), noticias: 65 },
          { name: t('dashboard.days.fri'), noticias: 48 }, { name: t('dashboard.days.sat'), noticias: 20 },
          { name: t('dashboard.days.sun'), noticias: 15 }
        ],
        categorias: [
          { name: t('dashboard.categories.politics'), value: 400 }, { name: t('dashboard.categories.economy'), value: 300 },
          { name: t('dashboard.categories.health'), value: 200 }, { name: t('dashboard.categories.tech'), value: 100 }
        ]
      };

      setData(response);
    } catch (err) {
      setError(true);
    } finally {
      setLoading(false);
    }
  };

  // Añadimos 't' a las dependencias para que recargue el mock si se cambia el idioma sobre la marcha
  useEffect(() => {
    fetchDashboardData();
  }, [t]);

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

  // PANTALLA DE ERROR
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

  // PANTALLA DE CARGA (Aparece mientras loading es true)
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

  // RENDERIZADO PRINCIPAL
  return (
    <div className={styles.dashboardWrapper}>
      {/* TÍTULO DE LA PÁGINA */}
      <h1 className={styles.pageTitle}>{t('dashboard.title')}</h1>

      {/* FILA 1: KPIs */}
      <div className={styles.topRow}>
        {/* FUENTES */}
        <div className={styles.card}>
          <span className={styles.cardTitle}>{t('dashboard.sourcesCard.title')}</span>
          <div className={styles.sourcesList}>
            <div className={styles.sourceItem}>
              <span>{t('dashboard.sourcesCard.active')}</span>
              <span className={styles.sourceValue}>{data.fuentes.activas}</span>
            </div>
            <div className={styles.sourceItem}>
              <span>{t('dashboard.sourcesCard.rss')}</span>
              <span className={styles.sourceValue}>{data.fuentes.rss}</span>
            </div>
          </div>
          <button className={styles.btnNavigate} onClick={() => navigate('/fuentes')}>
            {t('dashboard.sourcesCard.goBtn')} <ChevronRight size={14} />
          </button>
        </div>

        {/* NOTICIAS DETECTADAS */}
        <div className={styles.card}>
          <span className={styles.cardTitle}>{t('dashboard.newsCard.title')}</span>
          <span className={styles.metricValue}>
            {newsFilter === '1D' ? data.noticias.hoy : data.noticias.semana}
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

        {/* ALERTAS */}
        <div className={styles.card}>
          <span className={styles.cardTitle}>{t('dashboard.alertsCard.title')}</span>
          <span className={styles.metricValue}>{data.alertas}</span>
          <button className={styles.btnNavigate} onClick={() => navigate('/alertas')}>
            {t('dashboard.alertsCard.goBtn')} <ChevronRight size={14} />
          </button>
        </div>
      </div>

      {/* FILA 2: GRÁFICAS */}
      <div className={styles.bottomRow}>
        <div className={`${styles.card} ${styles.largeCard}`}>
          <span className={styles.cardTitle}>{t('dashboard.charts.evolutionTitle')}</span>
          <div className={styles.chartContainer}>
            <ResponsiveContainer width="100%" height="100%">
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
          <div className={styles.chartContainer}>
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={data.categorias}
                  innerRadius={60}
                  outerRadius={85}
                  paddingAngle={5}
                  dataKey="value"
                >
                  {data.categorias.map((entry, index) => (
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