import React, { useState, useMemo } from 'react';
import styles from './fuentes.module.css';
import { AuthContext } from '../../context/AuthContext';

// ─── DATOS DEL JSON rss_sources.json ─────────────────────────────────────────
const FUENTES = [
  { id:  1, nombre: 'RTVE',              url: 'https://www.rtve.es',             categorias: ['Ciencia', 'Cultura', 'Deportes', 'Economia', 'Educacion', 'Internacional', 'Politica', 'Salud', 'Sociedad', 'Tecnologia'] },
  { id:  2, nombre: 'El País',           url: 'https://elpais.com',              categorias: ['Ciencia', 'Cultura', 'Deportes', 'Economia', 'Entretenimiento', 'Internacional', 'Politica', 'Sociedad', 'Tecnologia', 'Viajes'] },
  { id:  3, nombre: 'ABC',               url: 'https://www.abc.es',              categorias: ['Cultura', 'Deportes', 'Economia', 'Educacion', 'Internacional', 'Politica', 'Salud', 'Sociedad', 'Tecnologia', 'Viajes'] },
  { id:  4, nombre: 'El Mundo',          url: 'https://www.elmundo.es',          categorias: ['Ciencia', 'Cultura', 'Deportes', 'Economia', 'Internacional', 'Politica', 'Salud', 'Sociedad', 'Tecnologia'] },
  { id:  5, nombre: 'Marca',             url: 'https://www.marca.com',           categorias: ['Deportes', 'Sociedad'] },
  { id:  6, nombre: 'El Confidencial',   url: 'https://www.elconfidencial.com',  categorias: ['Cultura', 'Deportes', 'Economia', 'Internacional', 'Politica', 'Sociedad', 'Tecnologia'] },
  { id:  7, nombre: 'El Español',        url: 'https://www.elespanol.com',       categorias: ['Ciencia', 'Cultura', 'Deportes', 'Economia', 'Internacional', 'Politica', 'Sociedad'] },
  { id:  8, nombre: 'Antena 3',          url: 'https://www.antena3.com',         categorias: ['Cultura', 'Deportes', 'Economia', 'Entretenimiento', 'Internacional', 'Politica', 'Sociedad', 'Tecnologia'] },
  { id:  9, nombre: 'Es Diario',         url: 'https://www.esdiario.com',        categorias: ['Cultura', 'Deportes', 'Economia', 'Internacional', 'Politica', 'Salud', 'Tecnologia', 'Viajes'] },
  { id: 10, nombre: 'El Diario',         url: 'https://www.eldiario.es',         categorias: ['Cultura', 'Deportes', 'Economia', 'Internacional', 'Politica', 'Sociedad', 'Tecnologia'] },
  { id: 11, nombre: 'La Moncloa',        url: 'https://www.lamoncloa.gob.es',    categorias: ['Politica'] },
  { id: 12, nombre: 'Consumo - AECOSAN', url: 'https://www.consumo.gob.es',      categorias: ['Sociedad'] },
];

const CANALES = [
  // RTVE
  { id:   1, fuenteId:  1, nombre: 'RTVE – Noticias',         categoria: 'Politica'       },
  { id:   2, fuenteId:  1, nombre: 'RTVE – España',           categoria: 'Politica'       },
  { id:   3, fuenteId:  1, nombre: 'RTVE – Economía',         categoria: 'Economia'       },
  { id:   4, fuenteId:  1, nombre: 'RTVE – Tecnología',       categoria: 'Tecnologia'     },
  { id:   5, fuenteId:  1, nombre: 'RTVE – Sociedad',         categoria: 'Sociedad'       },
  { id:   6, fuenteId:  1, nombre: 'RTVE – Cultura',          categoria: 'Cultura'        },
  { id:   7, fuenteId:  1, nombre: 'RTVE – Deportes',         categoria: 'Deportes'       },
  { id:   8, fuenteId:  1, nombre: 'RTVE – Internacional',    categoria: 'Internacional'  },
  { id:   9, fuenteId:  1, nombre: 'RTVE – Ciencia',          categoria: 'Ciencia'        },
  { id:  10, fuenteId:  1, nombre: 'RTVE – Salud',            categoria: 'Salud'          },
  { id:  11, fuenteId:  1, nombre: 'RTVE – Medioambiente',    categoria: 'Ciencia'        },
  { id:  12, fuenteId:  1, nombre: 'RTVE – Educación',        categoria: 'Educacion'      },
  // El País
  { id:  13, fuenteId:  2, nombre: 'El País – España',        categoria: 'Politica'       },
  { id:  14, fuenteId:  2, nombre: 'El País – Opinión',       categoria: 'Politica'       },
  { id:  15, fuenteId:  2, nombre: 'El País – Economía',      categoria: 'Economia'       },
  { id:  16, fuenteId:  2, nombre: 'El País – Tecnología',    categoria: 'Tecnologia'     },
  { id:  17, fuenteId:  2, nombre: 'El País – Sociedad',      categoria: 'Sociedad'       },
  { id:  18, fuenteId:  2, nombre: 'El País – Cultura',       categoria: 'Cultura'        },
  { id:  19, fuenteId:  2, nombre: 'El País – Deportes',      categoria: 'Deportes'       },
  { id:  20, fuenteId:  2, nombre: 'El País – Internacional', categoria: 'Internacional'  },
  { id:  21, fuenteId:  2, nombre: 'El País – Viajes',        categoria: 'Viajes'         },
  { id:  22, fuenteId:  2, nombre: 'El País – Buscavidas',    categoria: 'Sociedad'       },
  { id:  23, fuenteId:  2, nombre: 'El País – Clima',         categoria: 'Ciencia'        },
  { id:  24, fuenteId:  2, nombre: 'El País – Televisión',    categoria: 'Entretenimiento'},
  { id:  25, fuenteId:  2, nombre: 'El País – Estilo',        categoria: 'Sociedad'       },
  { id:  26, fuenteId:  2, nombre: 'El País – Cinco Días',    categoria: 'Economia'       },
  // ABC
  { id:  27, fuenteId:  3, nombre: 'ABC – España',            categoria: 'Politica'       },
  { id:  28, fuenteId:  3, nombre: 'ABC – Opinión',           categoria: 'Politica'       },
  { id:  29, fuenteId:  3, nombre: 'ABC – Internacional',     categoria: 'Internacional'  },
  { id:  30, fuenteId:  3, nombre: 'ABC – Economía',          categoria: 'Economia'       },
  { id:  31, fuenteId:  3, nombre: 'ABC – Tecnología',        categoria: 'Tecnologia'     },
  { id:  32, fuenteId:  3, nombre: 'ABC – Sociedad',          categoria: 'Sociedad'       },
  { id:  33, fuenteId:  3, nombre: 'ABC – Cultura',           categoria: 'Cultura'        },
  { id:  34, fuenteId:  3, nombre: 'ABC – Deportes',          categoria: 'Deportes'       },
  { id:  35, fuenteId:  3, nombre: 'ABC – Educación',         categoria: 'Educacion'      },
  { id:  36, fuenteId:  3, nombre: 'ABC – Viajes',            categoria: 'Viajes'         },
  { id:  37, fuenteId:  3, nombre: 'ABC – Estilo',            categoria: 'Sociedad'       },
  { id:  38, fuenteId:  3, nombre: 'ABC – Salud',             categoria: 'Salud'          },
  // El Mundo
  { id:  39, fuenteId:  4, nombre: 'El Mundo – Portada',      categoria: 'Politica'       },
  { id:  40, fuenteId:  4, nombre: 'El Mundo – España',       categoria: 'Politica'       },
  { id:  41, fuenteId:  4, nombre: 'El Mundo – Internacional',categoria: 'Internacional'  },
  { id:  42, fuenteId:  4, nombre: 'El Mundo – Economía',     categoria: 'Economia'       },
  { id:  43, fuenteId:  4, nombre: 'El Mundo – Tecnología',   categoria: 'Tecnologia'     },
  { id:  44, fuenteId:  4, nombre: 'El Mundo – Cultura',      categoria: 'Cultura'        },
  { id:  45, fuenteId:  4, nombre: 'El Mundo – Sociedad',     categoria: 'Sociedad'       },
  { id:  46, fuenteId:  4, nombre: 'El Mundo – Ciencia',      categoria: 'Ciencia'        },
  { id:  47, fuenteId:  4, nombre: 'El Mundo – Salud',        categoria: 'Salud'          },
  { id:  48, fuenteId:  4, nombre: 'El Mundo – Deportes',     categoria: 'Deportes'       },
  // Marca
  { id:  49, fuenteId:  5, nombre: 'Marca – Portada',         categoria: 'Deportes'       },
  { id:  50, fuenteId:  5, nombre: 'Marca – Fútbol',          categoria: 'Deportes'       },
  { id:  51, fuenteId:  5, nombre: 'Marca – Baloncesto',      categoria: 'Deportes'       },
  { id:  52, fuenteId:  5, nombre: 'Marca – Tenis',           categoria: 'Deportes'       },
  { id:  53, fuenteId:  5, nombre: 'Marca – Motor',           categoria: 'Deportes'       },
  { id:  54, fuenteId:  5, nombre: 'Marca – Ciclismo',        categoria: 'Deportes'       },
  { id:  55, fuenteId:  5, nombre: 'Marca – Atletismo',       categoria: 'Deportes'       },
  { id:  56, fuenteId:  5, nombre: 'Marca – Golf',            categoria: 'Deportes'       },
  { id:  57, fuenteId:  5, nombre: 'Marca – Olimpiadas',      categoria: 'Deportes'       },
  { id:  58, fuenteId:  5, nombre: 'Marca – Curiosidades',    categoria: 'Sociedad'       },
  // El Confidencial
  { id:  59, fuenteId:  6, nombre: 'El Confidencial – España',       categoria: 'Politica'     },
  { id:  60, fuenteId:  6, nombre: 'El Confidencial – El Confidente',categoria: 'Politica'     },
  { id:  61, fuenteId:  6, nombre: 'El Confidencial – Comunicación', categoria: 'Politica'     },
  { id:  62, fuenteId:  6, nombre: 'El Confidencial – Mercados',     categoria: 'Economia'     },
  { id:  63, fuenteId:  6, nombre: 'El Confidencial – Empresas',     categoria: 'Economia'     },
  { id:  64, fuenteId:  6, nombre: 'El Confidencial – Vivienda',     categoria: 'Economia'     },
  { id:  65, fuenteId:  6, nombre: 'El Confidencial – Tecnología',   categoria: 'Tecnologia'   },
  { id:  66, fuenteId:  6, nombre: 'El Confidencial – Sociedad',     categoria: 'Sociedad'     },
  { id:  67, fuenteId:  6, nombre: 'El Confidencial – Internacional',categoria: 'Internacional'},
  { id:  68, fuenteId:  6, nombre: 'El Confidencial – Cultura',      categoria: 'Cultura'      },
  { id:  69, fuenteId:  6, nombre: 'El Confidencial – Deportes',     categoria: 'Deportes'     },
  // El Español
  { id:  70, fuenteId:  7, nombre: 'El Español – España',        categoria: 'Politica'      },
  { id:  71, fuenteId:  7, nombre: 'El Español – Opinión',       categoria: 'Politica'      },
  { id:  72, fuenteId:  7, nombre: 'El Español – Internacional', categoria: 'Internacional' },
  { id:  73, fuenteId:  7, nombre: 'El Español – Economía',      categoria: 'Economia'      },
  { id:  74, fuenteId:  7, nombre: 'El Español – Sociedad',      categoria: 'Sociedad'      },
  { id:  75, fuenteId:  7, nombre: 'El Español – Deportes',      categoria: 'Deportes'      },
  { id:  76, fuenteId:  7, nombre: 'El Español – Cultura',       categoria: 'Cultura'       },
  { id:  77, fuenteId:  7, nombre: 'El Español – Ciencia',       categoria: 'Ciencia'       },
  // Antena 3
  { id:  78, fuenteId:  8, nombre: 'Antena 3 – Portada',        categoria: 'Politica'      },
  { id:  79, fuenteId:  8, nombre: 'Antena 3 – España',         categoria: 'Politica'      },
  { id:  80, fuenteId:  8, nombre: 'Antena 3 – Internacional',  categoria: 'Internacional' },
  { id:  81, fuenteId:  8, nombre: 'Antena 3 – Economía',       categoria: 'Economia'      },
  { id:  82, fuenteId:  8, nombre: 'Antena 3 – Tecnología',     categoria: 'Tecnologia'    },
  { id:  83, fuenteId:  8, nombre: 'Antena 3 – Cultura',        categoria: 'Cultura'       },
  { id:  84, fuenteId:  8, nombre: 'Antena 3 – Deportes',       categoria: 'Deportes'      },
  { id:  85, fuenteId:  8, nombre: 'Antena 3 – Sociedad',       categoria: 'Sociedad'      },
  { id:  86, fuenteId:  8, nombre: 'Antena 3 – Programas',      categoria: 'Entretenimiento'},
  { id:  87, fuenteId:  8, nombre: 'Antena 3 – Gente',          categoria: 'Sociedad'      },
  // Es Diario
  { id:  88, fuenteId:  9, nombre: 'Es Diario – Portada',       categoria: 'Politica'      },
  { id:  89, fuenteId:  9, nombre: 'Es Diario – Nacional',      categoria: 'Politica'      },
  { id:  90, fuenteId:  9, nombre: 'Es Diario – Opinión',       categoria: 'Politica'      },
  { id:  91, fuenteId:  9, nombre: 'Es Diario – Economía',      categoria: 'Economia'      },
  { id:  92, fuenteId:  9, nombre: 'Es Diario – Cultura',       categoria: 'Cultura'       },
  { id:  93, fuenteId:  9, nombre: 'Es Diario – Internacional', categoria: 'Internacional' },
  { id:  94, fuenteId:  9, nombre: 'Es Diario – Motor',         categoria: 'Tecnologia'    },
  { id:  95, fuenteId:  9, nombre: 'Es Diario – Viajes',        categoria: 'Viajes'        },
  { id:  96, fuenteId:  9, nombre: 'Es Diario – Deportes',      categoria: 'Deportes'      },
  { id:  97, fuenteId:  9, nombre: 'Es Diario – Salud',         categoria: 'Salud'         },
  // El Diario
  { id:  98, fuenteId: 10, nombre: 'El Diario – Portada',       categoria: 'Politica'      },
  { id:  99, fuenteId: 10, nombre: 'El Diario – Política',      categoria: 'Politica'      },
  { id: 100, fuenteId: 10, nombre: 'El Diario – Economía',      categoria: 'Economia'      },
  { id: 101, fuenteId: 10, nombre: 'El Diario – Sociedad',      categoria: 'Sociedad'      },
  { id: 102, fuenteId: 10, nombre: 'El Diario – Cultura',       categoria: 'Cultura'       },
  { id: 103, fuenteId: 10, nombre: 'El Diario – Internacional', categoria: 'Internacional' },
  { id: 104, fuenteId: 10, nombre: 'El Diario – Tecnología',    categoria: 'Tecnologia'    },
  { id: 105, fuenteId: 10, nombre: 'El Diario – Deportes',      categoria: 'Deportes'      },
  // La Moncloa
  { id: 106, fuenteId: 11, nombre: 'La Moncloa – General',      categoria: 'Politica'      },
  { id: 107, fuenteId: 11, nombre: 'La Moncloa – Noticias',     categoria: 'Politica'      },
  { id: 108, fuenteId: 11, nombre: 'La Moncloa – Agenda',       categoria: 'Politica'      },
  { id: 109, fuenteId: 11, nombre: 'La Moncloa – Presidencia',  categoria: 'Politica'      },
  // Consumo - AECOSAN
  { id: 110, fuenteId: 12, nombre: 'Consumo – Noticias',        categoria: 'Sociedad'      },
  { id: 111, fuenteId: 12, nombre: 'Consumo – Publicaciones',   categoria: 'Sociedad'      },
];

const ALL_CATEGORIAS = [
  'Ciencia', 'Cultura', 'Deportes', 'Economia', 'Educacion',
  'Entretenimiento', 'Internacional', 'Politica', 'Salud',
  'Sociedad', 'Tecnologia', 'Viajes',
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

// ─── FILA FUENTE ──────────────────────────────────────────────────────────────
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
  const [activeTab, setActiveTab]       = useState('fuentes');
  const [searchText, setSearchText]     = useState('');
  const [selectedCats, setSelectedCats] = useState([]);
  const [selectedFts, setSelectedFts]   = useState([]);

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
        {/* HEADER */}
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

        {/* BODY */}
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
                  : filteredCanales.map((item) => <CanalRow key={item.id} item={item} />)
              )}
            </div>

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