// frontend/src/pages/resumen/nubes.jsx

import React, { useState, useEffect, useContext } from 'react';
import { useTranslation } from 'react-i18next';
import { Link } from 'react-router-dom';
import { Bell, RefreshCw } from 'lucide-react';
import { AuthContext } from '../../context/AuthContext';
import styles from './nubes.module.css';

// ─── COMPONENTE: NUBE DE PALABRAS ────────────────────────────────────────────
const WordCloud = ({ terminos, loading, minFontRem = 0.7, maxFontRem = 2.0, showCreateAlert = false }) => {
  const { t } = useTranslation();

  if (loading) {
    return (
      <div className={styles.cloudContent}>
        {[...Array(6)].map((_, i) => (
          <div
            key={i}
            className={styles.skeleton}
            style={{ width: `${55 + i * 18}px`, height: '16px', borderRadius: '4px', opacity: 0.35 }}
          />
        ))}
      </div>
    );
  }

  if (!terminos || terminos.length === 0) {
    return (
      <div className={styles.cloudEmpty} style={{ textAlign: 'center', padding: '20px' }}>
        <p style={{ marginBottom: '15px', color: '#888', lineHeight: '1.5' }}>
          {t('clouds.noData', 'No hay datos suficientes todavía. Si acabas de crear una alerta, espera unos segundos a que se procesen las noticias y pulsa Actualizar.')}
        </p>

        {showCreateAlert && (
          <div style={{ display: 'flex', justifyContent: 'center' }}>
            <Link to="/alerts" className={styles.createAlertBtn}>
              <Bell size={16} />
              {t('clouds.createAlert', 'Crear nueva alerta')}
            </Link>
          </div>
        )}
      </div>
    );
  }

  const maxCount = Math.max(...terminos.map((t) => t.count));

  return (
    <div className={styles.cloudContent}>
      {terminos.map((item, i) => {
        const ratio    = item.count / maxCount;
        const fontSize = minFontRem + ratio * (maxFontRem - minFontRem);
        const opacity  = 0.5 + ratio * 0.5;
        return (
          <span
            key={item.term}
            className={styles.cloudWord}
            style={{ fontSize: `${fontSize}rem`, opacity, animationDelay: `${i * 55}ms` }}
          >
            {item.term}
          </span>
        );
      })}
    </div>
  );
};

// ─── COMPONENTE: CARD DE CATEGORÍA ───────────────────────────────────────────
const CategoriaCloud = ({ categoriaSlug, categoriaTraduccionKey, refreshCount }) => {
  const { t } = useTranslation();
  const { fetchNubeCategoria } = useContext(AuthContext);

  const [terminos, setTerminos] = useState([]);
  const [loading,  setLoading]  = useState(true);
  const [error,    setError]    = useState(false);

  useEffect(() => {
    let cancelled = false;
    setLoading(true);
    setError(false);

    // Llamamos a la API usando el SLUG en inglés (ej: 'politics')
    fetchNubeCategoria(categoriaSlug)
      .then((data) => {
        if (!cancelled) { setTerminos(data); setLoading(false); }
      })
      .catch(() => {
        if (!cancelled) { setError(true); setLoading(false); }
      });
    return () => { cancelled = true; };
  }, [categoriaSlug, fetchNubeCategoria, refreshCount]);

  return (
    <div className={styles.catCard}>
      <h3 className={styles.catTitle}>
        <span className={styles.accentBar} />
        {/* Usamos la clave original (ej: 'Politica') para buscar en el JSON de traducción */}
        {t(`categorias.${categoriaTraduccionKey}`, { defaultValue: categoriaTraduccionKey }).toUpperCase()}
      </h3>
      {error
        ? <p className={styles.cloudEmpty} style={{ fontSize: '0.8rem' }}>{t('clouds.errorCategory')}</p>
        : <WordCloud
            terminos={terminos}
            loading={loading}
            minFontRem={0.65}
            maxFontRem={1.5}
            showCreateAlert={false}
          />
      }
    </div>
  );
};

// ─── PÁGINA PRINCIPAL ─────────────────────────────────────────────────────────
const Nubes = () => {
  const { t } = useTranslation();
  const { fetchNubeGlobal, categorias, newsLoading } = useContext(AuthContext);

  const [globalTerminos, setGlobalTerminos] = useState([]);
  const [globalLoading,  setGlobalLoading]  = useState(true);
  const [globalError,    setGlobalError]    = useState(false);
  const [refreshCount,   setRefreshCount]   = useState(0);

  const loadGlobalData = () => {
    setGlobalLoading(true);
    setGlobalError(false);
    fetchNubeGlobal()
      .then((data) => { setGlobalTerminos(data); setGlobalLoading(false); })
      .catch(() => { setGlobalError(true); setGlobalLoading(false); });
  };

  useEffect(() => {
    loadGlobalData();
  }, [fetchNubeGlobal, refreshCount]);

  // MAPEO DE SEGURIDAD: Mapeamos los nombres/IDs que vienen de la DB a los Slugs del Backend
  const getBackendSlug = (cat) => {
    const name = cat.name || cat;
    // Normalizamos quitando acentos por si vienen de la DB con ellos
    const normalized = name.normalize("NFD").replace(/[\u0300-\u036f]/g, "");
    
    const map = {
      "Politica": "politics",
      "Economia": "economy",
      "Tecnologia": "technology",
      "Deportes": "sports",
      "Cultura": "culture",
      "Sociedad": "society",
      "Internacional": "international",
      "Salud": "health",
      "Educacion": "education",
      "Ciencia": "science",
      "Viajes": "travel",
      "Entretenimiento": "entertainment",
      "General": "general"
    };

    return map[normalized] || normalized.toLowerCase();
  };

  return (
    <div className={styles.wrapper}>
      {/* ── CABECERA CON TÍTULO Y BOTÓN DE ACTUALIZAR ── */}
      <div style={{ 
        display: 'flex', 
        justifyContent: 'space-between', 
        alignItems: 'center', 
        marginBottom: '25px' 
      }}>
        <h1 className={styles.pageTitle} style={{ margin: 0 }}>{t('clouds.pageTitle', 'Nubes de Palabras')}</h1>
        
        <button 
          onClick={() => setRefreshCount(prev => prev + 1)}
          style={{
            background: '#4e8df5', color: '#fff', border: 'none', padding: '10px 20px',
            borderRadius: '8px', cursor: 'pointer', fontWeight: 'bold', display: 'flex',
            alignItems: 'center', gap: '8px', transition: 'all 0.2s ease',
            boxShadow: '0 2px 4px rgba(0,0,0,0.1)'
          }}
          onMouseOver={(e) => e.currentTarget.style.backgroundColor = '#3b71ca'}
          onMouseOut={(e) => e.currentTarget.style.backgroundColor = '#4e8df5'}
        >
          <RefreshCw size={18} className={globalLoading ? styles.spinning : ''} />
          {t('clouds.refreshBtn', 'Actualizar')}
        </button>
      </div>

      {/* ── NUBE GLOBAL ── */}
      <section className={styles.globalSection}>
        <div className={styles.globalCard}>
          <h2 className={styles.globalTitle}>
            <span className={styles.accentBar} />
            {t('clouds.globalTitle', 'Términos Globales')}
          </h2>
          {globalError
            ? <p style={{ color: '#e74c3c', fontSize: '0.85rem' }}>{t('clouds.errorGlobal')}</p>
            : <WordCloud
                terminos={globalTerminos}
                loading={globalLoading}
                minFontRem={0.8}
                maxFontRem={2.5}
                showCreateAlert={true}
              />
          }
        </div>
      </section>

      {/* ── NUBES POR CATEGORÍA ── */}
      <section className={styles.catsSection}>
        <h2 className={styles.sectionTitle}>{t('clouds.categoriesTitle', 'Nubes por Categoría')}</h2>

        {newsLoading ? (
          <div className={styles.cloudEmpty}>
            <p>{t('clouds.loadingCategories', 'Cargando categorías...')}</p>
          </div>
        ) : (
          <div className={styles.catsGrid}>
            {categorias && categorias.length > 0 ? (
              categorias.map((cat) => (
                <CategoriaCloud 
                  key={cat.id || cat.name || cat} 
                  categoriaSlug={getBackendSlug(cat)} // Envía 'politics' al backend
                  categoriaTraduccionKey={cat.name || cat} // Usa 'Politica' para el t()
                  refreshCount={refreshCount} 
                />
              ))
            ) : (
              <div className={styles.cloudEmpty}>
                <p>{t('clouds.noCategories', 'No hay categorías disponibles.')}</p>
              </div>
            )}
          </div>
        )}
      </section>

      {/* Estilos locales rápidos para la animación del botón */}
      <style>{`
        @keyframes spin { from { transform: rotate(0deg); } to { transform: rotate(360deg); } }
        .${styles.spinning} { animation: spin 1s linear infinite; }
      `}</style>
    </div>
  );
};

export default Nubes;