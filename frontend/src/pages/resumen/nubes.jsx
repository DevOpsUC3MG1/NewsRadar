import React, { useState, useEffect, useContext } from 'react';
import { useTranslation } from 'react-i18next';
import { Link } from 'react-router-dom';
import { Bell } from 'lucide-react';
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
      <div className={styles.cloudEmpty}>
        <p>{t('clouds.noData')}</p>
        
        {showCreateAlert && (
          <Link to="/alerts" className={styles.createAlertBtn}>
            <Bell size={16} />
            {t('clouds.createAlert', 'Crear nueva alerta')}
          </Link>
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
const CategoriaCloud = ({ categoria }) => {
  const { t } = useTranslation();
  const { fetchNubeCategoria } = useContext(AuthContext);

  const [terminos, setTerminos] = useState([]);
  const [loading,  setLoading]  = useState(true);
  const [error,    setError]    = useState(false);

  useEffect(() => {
    let cancelled = false;
    setLoading(true);
    setError(false);
    
    // categoria viene como string (ej. 'culture', 'economy'), que es lo que espera el backend
    fetchNubeCategoria(categoria)
      .then((data) => {
        if (!cancelled) { setTerminos(data); setLoading(false); }
      })
      .catch(() => {
        if (!cancelled) { setError(true); setLoading(false); }
      });
    return () => { cancelled = true; };
  }, [categoria, fetchNubeCategoria]);

  return (
    <div className={styles.catCard}>
      <h3 className={styles.catTitle}>
        <span className={styles.accentBar} />
        {/* Traducimos el nombre de la categoría, usando el propio nombre dinámico como fallback */}
        {t(`clouds.categories.${categoria}`, { defaultValue: categoria }).toUpperCase()}
      </h3>
      {error
        ? <p className={styles.cloudEmpty} style={{ fontSize: '0.8rem' }}>{t('clouds.errorCategory')}</p>
        : <WordCloud 
            terminos={terminos} 
            loading={loading} 
            minFontRem={0.65} 
            maxFontRem={1.5} 
            showCreateAlert={true} 
          />
      }
    </div>
  );
};

// ─── PÁGINA PRINCIPAL ─────────────────────────────────────────────────────────
const Nubes = () => {
  const { t } = useTranslation();
  // 1. Añadimos 'categorias' y 'newsLoading' a la desestructuración del AuthContext
  const { fetchNubeGlobal, categorias, newsLoading } = useContext(AuthContext);

  const [globalTerminos, setGlobalTerminos] = useState([]);
  const [globalLoading,  setGlobalLoading]  = useState(true);
  const [globalError,    setGlobalError]    = useState(false);

  useEffect(() => {
    setGlobalLoading(true);
    setGlobalError(false);
    fetchNubeGlobal()
      .then((data) => { setGlobalTerminos(data); setGlobalLoading(false); })
      .catch(() => { setGlobalError(true); setGlobalLoading(false); });
  }, [fetchNubeGlobal]);

  return (
    <div className={styles.wrapper}>
      <h1 className={styles.pageTitle}>{t('clouds.pageTitle')}</h1>

      {/* ── NUBE GLOBAL ── */}
      <section className={styles.globalSection}>
        <div className={styles.globalCard}>
          <h2 className={styles.globalTitle}>
            <span className={styles.accentBar} />
            {t('clouds.globalTitle')}
          </h2>
          {globalError
            ? <p style={{ color: '#e74c3c', fontSize: '0.85rem' }}>{t('clouds.errorGlobal')}</p>
            : <WordCloud
                terminos={globalTerminos}
                loading={globalLoading}
                minFontRem={0.75}
                maxFontRem={2.2}
                showCreateAlert={true}
              />
          }
        </div>
      </section>

      {/* ── NUBES POR CATEGORÍA ── */}
      <section className={styles.catsSection}>
        <h2 className={styles.sectionTitle}>{t('clouds.categoriesTitle')}</h2>
        
        {/* 2. Añadimos manejo del estado de carga general de las categorías */}
        {newsLoading ? (
          <div className={styles.cloudEmpty}>
            <p>{t('clouds.loadingCategories', 'Cargando categorías...')}</p>
          </div>
        ) : (
          <div className={styles.catsGrid}>
            {/* 3. Mapeamos las categorías dinámicas del backend */}
            {categorias && categorias.length > 0 ? (
              categorias.map((cat) => (
                // Asumiendo que tus objetos de categoría del backend tienen propiedades id y name
                <CategoriaCloud key={cat.id} categoria={cat.name} />
              ))
            ) : (
              <div className={styles.cloudEmpty}>
                <p>{t('clouds.noCategories', 'No se encontraron categorías disponibles.')}</p>
              </div>
            )}
          </div>
        )}
      </section>
    </div>
  );
};

export default Nubes;