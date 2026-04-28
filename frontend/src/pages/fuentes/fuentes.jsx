import React, { useState, useMemo } from 'react';
import styles from './fuentes.module.css';

// ─── DATOS ESTÁTICOS ─────────────────────────────────────────────────────────
const FUENTES = [
  { id: 1,  nombre: 'RTVE',                   url: 'https://www.rtve.es/rss/',                                                    categorias: ['Política', 'Cultura', 'Nacional'] },
  { id: 2,  nombre: 'El País',                url: 'https://elpais.com/info/rss/',                                                categorias: ['Política', 'Economía', 'Internacional'] },
  { id: 3,  nombre: 'ABC',                    url: 'https://www.abc.es/rss/',                                                     categorias: ['Nacional', 'Deportes', 'Cultura'] },
  { id: 4,  nombre: 'El Confidencial',        url: 'https://www.elconfidencial.com/rss/',                                        categorias: ['Economía', 'Tecnología', 'Política'] },
  { id: 5,  nombre: 'Marca',                  url: 'https://www.marca.com/rss.html',                                             categorias: ['Deportes'] },
  { id: 6,  nombre: 'EsDiario',               url: 'https://www.esdiario.com/rss.html',                                          categorias: ['Nacional', 'Política'] },
  { id: 7,  nombre: 'Antena 3',               url: 'https://www.antena3.com/rss/',                                               categorias: ['Entretenimiento', 'Nacional', 'Cultura'] },
  { id: 8,  nombre: 'DSCA',                   url: 'https://www.dsca.gob.es/es/consumo/canales-rss',                             categorias: ['Gobierno', 'Consumo'] },
  { id: 9,  nombre: 'Ministerio de Economía', url: 'https://portal.mineco.gob.es/es-es/ministerio/Paginas/Info_RSS.aspx',        categorias: ['Economía', 'Gobierno'] },
  { id: 10, nombre: 'La Moncloa',             url: 'https://www.lamoncloa.gob.es/paginas/varios/rss.aspx',                       categorias: ['Gobierno', 'Política', 'Nacional'] },
];

// Cada canal tiene UNA sola categoría
const CANALES = [
  { id: 1,  fuenteId: 1,  nombre: 'RTVE – Noticias',                 categoria: 'Nacional' },
  { id: 2,  fuenteId: 1,  nombre: 'RTVE – Cultura',                  categoria: 'Cultura' },
  { id: 3,  fuenteId: 2,  nombre: 'El País – Portada',               categoria: 'Política' },
  { id: 4,  fuenteId: 2,  nombre: 'El País – Economía',              categoria: 'Economía' },
  { id: 5,  fuenteId: 3,  nombre: 'ABC – España',                    categoria: 'Nacional' },
  { id: 6,  fuenteId: 3,  nombre: 'ABC – Deportes',                  categoria: 'Deportes' },
  { id: 7,  fuenteId: 4,  nombre: 'El Confidencial – Economía',      categoria: 'Economía' },
  { id: 8,  fuenteId: 4,  nombre: 'El Confidencial – Tech',          categoria: 'Tecnología' },
  { id: 9,  fuenteId: 4,  nombre: 'El Confidencial – Política',      categoria: 'Política' },
  { id: 10, fuenteId: 5,  nombre: 'Marca – Fútbol',                  categoria: 'Deportes' },
  { id: 11, fuenteId: 5,  nombre: 'Marca – Motor',                   categoria: 'Deportes' },
  { id: 12, fuenteId: 6,  nombre: 'EsDiario – Nacional',             categoria: 'Nacional' },
  { id: 13, fuenteId: 7,  nombre: 'Antena 3 – Noticias',             categoria: 'Nacional' },
  { id: 14, fuenteId: 7,  nombre: 'Antena 3 – Entretenimiento',      categoria: 'Entretenimiento' },
  { id: 15, fuenteId: 8,  nombre: 'DSCA – Consumo',                  categoria: 'Consumo' },
  { id: 16, fuenteId: 9,  nombre: 'Ministerio Economía – Novedades', categoria: 'Economía' },
  { id: 17, fuenteId: 10, nombre: 'La Moncloa – Actualidad',         categoria: 'Gobierno' },
  { id: 18, fuenteId: 10, nombre: 'La Moncloa – Presidencia',        categoria: 'Nacional' },
];

const ALL_CATEGORIAS = [
  'Cultura', 'Consumo', 'Deportes', 'Economía', 'Entretenimiento',
  'Gobierno', 'Internacional', 'Nacional', 'Política', 'Tecnología',
];

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

// ─── FILA FUENTE — solo lectura ───────────────────────────────────────────────
const FuenteRow = ({ item }) => (
  <div className={styles.row}>
    <span className={styles.rowName}>{item.nombre}</span>
    <div className={styles.rowCats}>
      {item.categorias.map((c) => (
        <span key={c} className={styles.catBadge}>{c}</span>
      ))}
    </div>
  </div>
);

// ─── FILA CANAL RSS — solo lectura, una categoría ─────────────────────────────
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
  const [activeTab, setActiveTab]         = useState('fuentes');
  const [searchText, setSearchText]       = useState('');
  const [selectedCats, setSelectedCats]   = useState([]);
  const [selectedFts, setSelectedFts]     = useState([]); // ids de fuentes (solo en tab canales)

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
    FUENTES.filter((item) => {
      const matchSearch = !searchText.trim() || item.nombre.toLowerCase().includes(searchText.toLowerCase());
      const matchCats   = !selectedCats.length || selectedCats.some((c) => item.categorias.includes(c));
      return matchSearch && matchCats;
    }),
  [searchText, selectedCats]);

  const filteredCanales = useMemo(() =>
    CANALES.filter((item) => {
      const matchSearch = !searchText.trim() || item.nombre.toLowerCase().includes(searchText.toLowerCase());
      const matchCats   = !selectedCats.length || selectedCats.includes(item.categoria);
      const matchFts    = !selectedFts.length  || selectedFts.includes(item.fuenteId);
      return matchSearch && matchCats && matchFts;
    }),
  [searchText, selectedCats, selectedFts]);

  return (
    <div className={styles.wrapper}>
      <h1 className={styles.pageTitle}>Fuente y RSS – Gestión de fuentes</h1>

      <div className={styles.mainCard}>

        {/* ── HEADER ── */}
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

        {/* ── BODY ── */}
        <div className={styles.cardBody}>

          {/* SIDEBAR */}
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
              {ALL_CATEGORIAS.map((cat) => (
                <FilterCheck
                  key={cat}
                  label={cat}
                  checked={selectedCats.includes(cat)}
                  onToggle={() => toggleCat(cat)}
                />
              ))}
            </div>

            {/* Filtro por fuente — solo visible en Canales RSS */}
            {!isFuentesTab && (
              <>
                <p className={styles.sidebarSection}>Fuentes</p>
                <div className={styles.catList}>
                  {FUENTES.map((f) => (
                    <FilterCheck
                      key={f.id}
                      label={f.nombre}
                      checked={selectedFts.includes(f.id)}
                      onToggle={() => toggleFt(f.id)}
                    />
                  ))}
                </div>
              </>
            )}
          </aside>

          {/* LISTA */}
          <div className={styles.listPanel}>
            <div className={styles.listScroll}>
              {isFuentesTab ? (
                filteredFuentes.length === 0
                  ? <div className={styles.emptyState}>No se encontraron fuentes con los filtros actuales.</div>
                  : filteredFuentes.map((item) => <FuenteRow key={item.id} item={item} />)
              ) : (
                filteredCanales.length === 0
                  ? <div className={styles.emptyState}>No se encontraron canales con los filtros actuales.</div>
                  : filteredCanales.map((item) => (
                      <CanalRow key={item.id} item={item} />
                    ))
              )}
            </div>

            {/* FOOTER */}
            <div className={styles.listFooter}>
              {isFuentesTab
                ? `Mostrando ${filteredFuentes.length} de ${FUENTES.length} fuentes – ${CANALES.length} canales RSS totales`
                : `Mostrando ${filteredCanales.length} de ${CANALES.length} canales – ${FUENTES.length} fuentes totales`}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Fuentes;