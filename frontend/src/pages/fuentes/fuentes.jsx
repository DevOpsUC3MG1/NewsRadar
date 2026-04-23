import React, { useState, useMemo } from 'react';
import styles from './fuentes.module.css';

// ─── DATOS ESTÁTICOS ────────────────────────────────────────────────────────
const FUENTES = [
  {
    id: 1,
    nombre: 'RTVE',
    url: 'https://www.rtve.es/rss/',
    categorias: ['Política', 'Cultura', 'Nacional'],
  },
  {
    id: 2,
    nombre: 'El País',
    url: 'https://elpais.com/info/rss/',
    categorias: ['Política', 'Economía', 'Internacional'],
  },
  {
    id: 3,
    nombre: 'ABC',
    url: 'https://www.abc.es/rss/',
    categorias: ['Nacional', 'Deportes', 'Cultura'],
  },
  {
    id: 4,
    nombre: 'El Confidencial',
    url: 'https://www.elconfidencial.com/rss/',
    categorias: ['Economía', 'Tecnología', 'Política'],
  },
  {
    id: 5,
    nombre: 'Marca',
    url: 'https://www.marca.com/rss.html',
    categorias: ['Deportes'],
  },
  {
    id: 6,
    nombre: 'EsDiario',
    url: 'https://www.esdiario.com/rss.html',
    categorias: ['Nacional', 'Política'],
  },
  {
    id: 7,
    nombre: 'Antena 3',
    url: 'https://www.antena3.com/rss/',
    categorias: ['Entretenimiento', 'Nacional', 'Cultura'],
  },
  {
    id: 8,
    nombre: 'DSCA',
    url: 'https://www.dsca.gob.es/es/consumo/canales-rss',
    categorias: ['Gobierno', 'Consumo'],
  },
  {
    id: 9,
    nombre: 'Ministerio de Economía',
    url: 'https://portal.mineco.gob.es/es-es/ministerio/Paginas/Info_RSS.aspx',
    categorias: ['Economía', 'Gobierno'],
  },
  {
    id: 10,
    nombre: 'La Moncloa',
    url: 'https://www.lamoncloa.gob.es/paginas/varios/rss.aspx',
    categorias: ['Gobierno', 'Política', 'Nacional'],
  },
];

// Canales RSS derivados de las fuentes (múltiples canales por fuente)
const CANALES = [
  { id: 1, fuenteId: 1, nombre: 'RTVE – Noticias', categorias: ['Nacional', 'Política'] },
  { id: 2, fuenteId: 1, nombre: 'RTVE – Cultura', categorias: ['Cultura'] },
  { id: 3, fuenteId: 2, nombre: 'El País – Portada', categorias: ['Política', 'Internacional'] },
  { id: 4, fuenteId: 2, nombre: 'El País – Economía', categorias: ['Economía'] },
  { id: 5, fuenteId: 3, nombre: 'ABC – España', categorias: ['Nacional'] },
  { id: 6, fuenteId: 3, nombre: 'ABC – Deportes', categorias: ['Deportes'] },
  { id: 7, fuenteId: 4, nombre: 'El Confidencial – Economía', categorias: ['Economía'] },
  { id: 8, fuenteId: 4, nombre: 'El Confidencial – Tech', categorias: ['Tecnología'] },
  { id: 9, fuenteId: 4, nombre: 'El Confidencial – Política', categorias: ['Política'] },
  { id: 10, fuenteId: 5, nombre: 'Marca – Fútbol', categorias: ['Deportes'] },
  { id: 11, fuenteId: 5, nombre: 'Marca – Motor', categorias: ['Deportes'] },
  { id: 12, fuenteId: 6, nombre: 'EsDiario – Nacional', categorias: ['Nacional', 'Política'] },
  { id: 13, fuenteId: 7, nombre: 'Antena 3 – Noticias', categorias: ['Nacional'] },
  { id: 14, fuenteId: 7, nombre: 'Antena 3 – Entretenimiento', categorias: ['Entretenimiento'] },
  { id: 15, fuenteId: 8, nombre: 'DSCA – Consumo', categorias: ['Consumo', 'Gobierno'] },
  { id: 16, fuenteId: 9, nombre: 'Ministerio Economía – Novedades', categorias: ['Economía', 'Gobierno'] },
  { id: 17, fuenteId: 10, nombre: 'La Moncloa – Actualidad', categorias: ['Gobierno', 'Política'] },
  { id: 18, fuenteId: 10, nombre: 'La Moncloa – Presidencia', categorias: ['Gobierno', 'Nacional'] },
];

// Todas las categorías únicas
const ALL_CATEGORIAS = [
  'Cultura', 'Consumo', 'Deportes', 'Economía', 'Entretenimiento',
  'Gobierno', 'Internacional', 'Nacional', 'Política', 'Tecnología',
];

// ─── COMPONENTE: CHECKBOX DE CATEGORÍA ──────────────────────────────────────
const CategoriaCheck = ({ label, checked, onChange }) => (
  <label className={styles.checkLabel}>
    <span className={`${styles.checkbox} ${checked ? styles.checkboxChecked : ''}`}>
      {checked && (
        <svg width="10" height="8" viewBox="0 0 10 8" fill="none">
          <path d="M1 4L3.5 6.5L9 1" stroke="white" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" />
        </svg>
      )}
    </span>
    {label}
  </label>
);

// ─── COMPONENTE: FILA DE FUENTE ──────────────────────────────────────────────
const FuenteRow = ({ item, onEdit, onDelete }) => (
  <div className={styles.row}>
    <span className={styles.rowName}>{item.nombre}</span>
    <div className={styles.rowCats}>
      {item.categorias.map((c) => (
        <span key={c} className={styles.catBadge}>{c}</span>
      ))}
    </div>
    <div className={styles.rowActions}>
      <button className={styles.actionBtn} onClick={() => onEdit(item)} title="Editar">
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
          <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7" />
          <path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z" />
        </svg>
      </button>
      <button className={`${styles.actionBtn} ${styles.actionBtnDelete}`} onClick={() => onDelete(item)} title="Eliminar">
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
          <line x1="18" y1="6" x2="6" y2="18" />
          <line x1="6" y1="6" x2="18" y2="18" />
        </svg>
      </button>
    </div>
  </div>
);

// ─── PÁGINA PRINCIPAL ────────────────────────────────────────────────────────
const Fuentes = () => {
  const [activeTab, setActiveTab] = useState('fuentes'); // 'fuentes' | 'canales'
  const [searchText, setSearchText] = useState('');
  const [selectedCats, setSelectedCats] = useState([]);

  const toggleCat = (cat) => {
    setSelectedCats((prev) =>
      prev.includes(cat) ? prev.filter((c) => c !== cat) : [...prev, cat]
    );
  };

  // Datos filtrados según tab, búsqueda y categorías
  const filteredItems = useMemo(() => {
    const source = activeTab === 'fuentes' ? FUENTES : CANALES;
    return source.filter((item) => {
      const matchSearch =
        searchText.trim() === '' ||
        item.nombre.toLowerCase().includes(searchText.toLowerCase());
      const matchCats =
        selectedCats.length === 0 ||
        selectedCats.some((c) => item.categorias.includes(c));
      return matchSearch && matchCats;
    });
  }, [activeTab, searchText, selectedCats]);

  const totalFuentes = FUENTES.length;
  const totalCanales = CANALES.length;

  const handleEdit = (item) => {
    alert(`Editar: ${item.nombre}\n(Aquí conectarías con tu modal de edición)`);
  };
  const handleDelete = (item) => {
    if (window.confirm(`¿Eliminar "${item.nombre}"?`)) {
      // En producción actualizarías el estado/backend
    }
  };

  return (
    <div className={styles.wrapper}>
      <h1 className={styles.pageTitle}>Fuente y RSS – Gestión de fuentes</h1>

      <div className={styles.mainCard}>
        {/* ── HEADER: título + tabs ── */}
        <div className={styles.cardHeader}>
          <span className={styles.cardHeaderTitle}>Fuentes e información</span>
          <div className={styles.tabs}>
            <button
              className={`${styles.tab} ${activeTab === 'fuentes' ? styles.tabActive : ''}`}
              onClick={() => setActiveTab('fuentes')}
            >
              Fuentes
            </button>
            <button
              className={`${styles.tab} ${activeTab === 'canales' ? styles.tabActive : ''}`}
              onClick={() => setActiveTab('canales')}
            >
              Canales RSS
            </button>
          </div>
        </div>

        {/* ── BODY: sidebar + lista ── */}
        <div className={styles.cardBody}>
          {/* SIDEBAR FILTROS */}
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
                <div
                  key={cat}
                  className={styles.catItem}
                  onClick={() => toggleCat(cat)}
                >
                  <CategoriaCheck
                    label={cat}
                    checked={selectedCats.includes(cat)}
                    onChange={() => toggleCat(cat)}
                  />
                </div>
              ))}
            </div>
          </aside>

          {/* LISTA */}
          <div className={styles.listPanel}>
            <div className={styles.listScroll}>
              {filteredItems.length === 0 ? (
                <div className={styles.emptyState}>
                  No se encontraron {activeTab === 'fuentes' ? 'fuentes' : 'canales'} con los filtros actuales.
                </div>
              ) : (
                filteredItems.map((item) => (
                  <FuenteRow
                    key={item.id}
                    item={item}
                    onEdit={handleEdit}
                    onDelete={handleDelete}
                  />
                ))
              )}
            </div>

            {/* FOOTER CONTADOR */}
            <div className={styles.listFooter}>
              Mostrando {filteredItems.length} de {totalFuentes} fuentes – {totalCanales} canales RSS totales
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Fuentes;