import React, { useState, useMemo, useContext } from 'react';
import { useTranslation } from 'react-i18next';
import styles from './fuentes.module.css';
import { AuthContext } from '../../context/AuthContext';

// ─── CHECKBOX ─────────────────────────────────────────────────────────────────
const FilterCheck = ({ label, checked, onToggle }) => (
  <div className={styles.catItem} onClick={onToggle}>
    <span className={`${styles.checkbox} ${checked ? styles.checkboxChecked : ''}`}>
      {checked && (
        <svg width="10" height="8" viewBox="0 0 10 8" fill="none">
          <path d="M1 4L3.5 6.5L9 1" stroke="white" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" />
        </svg>
      )}
    </span>
    <span className={styles.checkLabelText}>{label}</span>
  </div>
);

// ─── FILA FUENTE ──────────────────────────────────────────────────────────────
const FuenteRow = ({ item }) => {
  const { t } = useTranslation();
  return (
    <div className={styles.row}>
      <span className={styles.rowName}>{item.nombre}</span>
      <div className={styles.rowCats}>
        {item.categorias && item.categorias.map((c, idx) => (
          <span key={`${c}-${idx}`} className={styles.catBadge}>
            {t(`categorias.${c}`, { defaultValue: c })}
          </span>
        ))}
      </div>
    </div>
  );
};

// ─── FILA CANAL RSS ───────────────────────────────────────────────────────────
const CanalRow = ({ item }) => {
  const { t } = useTranslation();
  return (
    <div className={styles.row}>
      <span className={styles.rowName}>{item.nombre}</span>
      <div className={styles.rowCats}>
        <span className={styles.catBadge}>
          {t(`categorias.${item.categoria}`, { defaultValue: item.categoria })}
        </span>
      </div>
    </div>
  );
};

// ─── PÁGINA PRINCIPAL ─────────────────────────────────────────────────────────
const Fuentes = () => {
  const { t } = useTranslation();
  const { fuentes, canales, categorias, newsLoading, newsError } = useContext(AuthContext);

  const [activeTab, setActiveTab]       = useState('fuentes');
  const [searchText, setSearchText]     = useState('');
  const [selectedCats, setSelectedCats] = useState([]);
  const [selectedFts, setSelectedFts]   = useState([]);

  // ─── NORMALIZACIÓN DE DATOS ─────────────────────────────────────────────────
  const safeCategorias = useMemo(() => {
    const cats = categorias || [];
    return [...new Set(cats.map(c => typeof c === 'object' && c !== null ? c.name : c))].filter(Boolean);
  }, [categorias]);

  const safeFuentes = useMemo(() => {
    return (fuentes || []).map(f => ({
      ...f,
      categorias: (f.categorias || []).map(c => typeof c === 'object' && c !== null ? c.name : c).filter(Boolean)
    }));
  }, [fuentes]);

  const safeCanales = useMemo(() => {
    return (canales || []).map(c => ({
      ...c,
      categoria: typeof c.categoria === 'object' && c.categoria !== null ? c.categoria.name : (c.categoria || 'General')
    }));
  }, [canales]);

  // ─── LÓGICA DE INTERFAZ ─────────────────────────────────────────────────────
  const toggleCat = (cat) =>
    setSelectedCats((prev) => prev.includes(cat) ? prev.filter((c) => c !== cat) : [...prev, cat]);

  const toggleFt = (id) =>
    setSelectedFts((prev) => prev.includes(id) ? prev.filter((f) => f !== id) : [...prev, id]);

  const handleTabChange = (tab) => {
    setActiveTab(tab);
    setSearchText('');
    setSelectedCats([]);
    setSelectedFts([]);
  };

  const isFuentesTab = activeTab === 'fuentes';

  const filteredFuentes = useMemo(() =>
    safeFuentes.filter((item) => {
      const matchSearch = !searchText.trim() || item.nombre.toLowerCase().includes(searchText.toLowerCase());
      const matchCats   = !selectedCats.length || selectedCats.some((c) => item.categorias.includes(c));
      return matchSearch && matchCats;
    }),
  [safeFuentes, searchText, selectedCats]);

  const filteredCanales = useMemo(() =>
    safeCanales.filter((item) => {
      const matchSearch = !searchText.trim() || item.nombre.toLowerCase().includes(searchText.toLowerCase());
      const matchCats   = !selectedCats.length || selectedCats.includes(item.categoria);
      const matchFts    = !selectedFts.length  || selectedFts.includes(item.fuenteId);
      return matchSearch && matchCats && matchFts;
    }),
  [safeCanales, searchText, selectedCats, selectedFts]);

  // ─── PANTALLAS DE CARGA Y ERROR ──────────────────────────────────────────────
  if (newsLoading) {
    return (
      <div className={styles.wrapper}>
        <div style={{ padding: '40px', textAlign: 'center', color: '#666' }}>
          {t('sources.loading')}
        </div>
      </div>
    );
  }

  if (newsError) {
    return (
      <div className={styles.wrapper}>
        <div style={{ padding: '40px', textAlign: 'center', color: '#E02020' }}>
          {t('sources.error')}
        </div>
      </div>
    );
  }

  // ─── RENDER PRINCIPAL ────────────────────────────────────────────────────────
  return (
    <div className={styles.wrapper}>
      <h1 className={styles.pageTitle}>{t('sources.title')}</h1>

      <div className={styles.mainCard}>
        <div className={styles.cardHeader}>
          <span className={styles.cardHeaderTitle}>{t('sources.cardTitle')}</span>
          <div className={styles.tabs}>
            <button
              className={`${styles.tab} ${isFuentesTab ? styles.tabActive : ''}`}
              onClick={() => handleTabChange('fuentes')}
            >
              {t('sources.tabs.sources')}
            </button>
            <button
              className={`${styles.tab} ${!isFuentesTab ? styles.tabActive : ''}`}
              onClick={() => handleTabChange('canales')}
            >
              {t('sources.tabs.channels')}
            </button>
          </div>
        </div>

        <div className={styles.cardBody}>
          <aside className={styles.sidebar}>
            <input
              type="text"
              className={styles.searchInput}
              placeholder={t('sources.sidebar.search')}
              value={searchText}
              onChange={(e) => setSearchText(e.target.value)}
            />

            <p className={styles.sidebarSection}>{t('sources.sidebar.categories')}</p>
            <div className={styles.catList}>
              {safeCategorias.map((cat, idx) => (
                <FilterCheck
                  key={`cat-${idx}`}
                  // Traducimos el texto que ve el usuario
                  label={t(`categorias.${cat}`, { defaultValue: cat })}
                  // Comparamos usando el valor original
                  checked={selectedCats.includes(cat)}
                  onToggle={() => toggleCat(cat)}
                />
              ))}
            </div>

            {!isFuentesTab && (
              <>
                <p className={styles.sidebarSection}>{t('sources.sidebar.sources')}</p>
                <div className={styles.catList}>
                  {safeFuentes.map((f) => (
                    <FilterCheck
                      key={`ft-${f.id}`}
                      label={f.nombre}
                      checked={selectedFts.includes(f.id)}
                      onToggle={() => toggleFt(f.id)}
                    />
                  ))}
                </div>
              </>
            )}
          </aside>

          <div className={styles.listPanel}>
            <div className={styles.listScroll}>
              {isFuentesTab ? (
                filteredFuentes.length === 0
                  ? <div className={styles.emptyState}>{t('sources.empty.sources')}</div>
                  : filteredFuentes.map((item) => <FuenteRow key={`f-row-${item.id}`} item={item} />)
              ) : (
                filteredCanales.length === 0
                  ? <div className={styles.emptyState}>{t('sources.empty.channels')}</div>
                  : filteredCanales.map((item) => <CanalRow key={`c-row-${item.id}`} item={item} />)
              )}
            </div>

            <div className={styles.listFooter}>
              {isFuentesTab
                ? t('sources.footer.sources', {
                    filtered: filteredFuentes.length,
                    total: safeFuentes.length,
                    channels: safeCanales.length
                  })
                : t('sources.footer.channels', {
                    filtered: filteredCanales.length,
                    total: safeCanales.length,
                    sources: safeFuentes.length
                  })
              }
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Fuentes;