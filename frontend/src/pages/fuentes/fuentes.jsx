import React, { useState, useMemo, useContext } from 'react';
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
const FuenteRow = ({ item }) => (
  <div className={styles.row}>
    <span className={styles.rowName}>{item.nombre}</span>
    <div className={styles.rowCats}>
      {item.categorias && item.categorias.map((c, idx) => (
        <span key={`${c}-${idx}`} className={styles.catBadge}>{c}</span>
      ))}
    </div>
  </div>
);

// ─── FILA CANAL RSS ───────────────────────────────────────────────────────────
const CanalRow = ({ item }) => (
  <div className={styles.row}>
    <span className={styles.rowName}>{item.nombre}</span>
    <div className={styles.rowCats}>
      <span className={styles.catBadge}>{item.categoria}</span>
    </div>
  </div>
);

// ─── PÁGINA PRINCIPAL ─────────────────────────────────────────────────────────
const Fuentes = () => {
  const { fuentes, canales, categorias, newsLoading, newsError } = useContext(AuthContext);

  const [activeTab, setActiveTab]       = useState('fuentes');
  const [searchText, setSearchText]     = useState('');
  const [selectedCats, setSelectedCats] = useState([]);
  const [selectedFts, setSelectedFts]   = useState([]);

  // ─── NORMALIZACIÓN DE DATOS (Solución al pantallazo en blanco) ──────────────
  // Extraemos solo los "nombres" (strings) por si el backend nos envía objetos enteros
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

  // Filtramos usando las listas seguras (safe...)
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
          Cargando fuentes y canales desde el servidor...
        </div>
      </div>
    );
  }

  if (newsError) {
    return (
      <div className={styles.wrapper}>
        <div style={{ padding: '40px', textAlign: 'center', color: '#E02020' }}>
          Ocurrió un error al cargar la información. Inténtalo de nuevo más tarde.
        </div>
      </div>
    );
  }

  // ─── RENDER PRINCIPAL ────────────────────────────────────────────────────────
  return (
    <div className={styles.wrapper}>
      <h1 className={styles.pageTitle}>Fuente y RSS – Gestión de fuentes</h1>

      <div className={styles.mainCard}>
        <div className={styles.cardHeader}>
          <span className={styles.cardHeaderTitle}>Fuentes e información</span>
          <div className={styles.tabs}>
            <button
              className={`${styles.tab} ${isFuentesTab ? styles.tabActive : ''}`}
              onClick={() => handleTabChange('fuentes')}
            >
              Fuentes
            </button>
            <button
              className={`${styles.tab} ${!isFuentesTab ? styles.tabActive : ''}`}
              onClick={() => handleTabChange('canales')}
            >
              Canales RSS
            </button>
          </div>
        </div>

        <div className={styles.cardBody}>
          <aside className={styles.sidebar}>
            <input
              type="text"
              className={styles.searchInput}
              placeholder="Buscar..."
              value={searchText}
              onChange={(e) => setSearchText(e.target.value)}
            />

            <p className={styles.sidebarSection}>Categorías</p>
            <div className={styles.catList}>
              {safeCategorias.map((cat, idx) => (
                <FilterCheck
                  key={`cat-${idx}`}
                  label={cat}
                  checked={selectedCats.includes(cat)}
                  onToggle={() => toggleCat(cat)}
                />
              ))}
            </div>

            {!isFuentesTab && (
              <>
                <p className={styles.sidebarSection}>Fuentes</p>
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
                  ? <div className={styles.emptyState}>No se encontraron fuentes con los filtros actuales.</div>
                  : filteredFuentes.map((item) => <FuenteRow key={`f-row-${item.id}`} item={item} />)
              ) : (
                filteredCanales.length === 0
                  ? <div className={styles.emptyState}>No se encontraron canales con los filtros actuales.</div>
                  : filteredCanales.map((item) => <CanalRow key={`c-row-${item.id}`} item={item} />)
              )}
            </div>

            <div className={styles.listFooter}>
              {isFuentesTab
                ? `Mostrando ${filteredFuentes.length} de ${safeFuentes.length} fuentes – ${safeCanales.length} canales RSS totales`
                : `Mostrando ${filteredCanales.length} de ${safeCanales.length} canales – ${safeFuentes.length} fuentes totales`}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Fuentes;