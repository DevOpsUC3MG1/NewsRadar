import React, { useState, useEffect } from 'react';
import styles from './nubes.module.css';

// ─── CATEGORÍAS ──────────────────────────────────────────────────────────────
const ALL_CATEGORIAS = [
  'Cultura', 'Consumo', 'Deportes', 'Economía', 'Entretenimiento',
  'Gobierno', 'Internacional', 'Nacional', 'Política', 'Tecnología',
];

// ─── MOCK: nube global (todos los canales RSS) ───────────────────────────────
const fetchNubeGlobal = async () => {
  await new Promise((res) => setTimeout(res, 700));
  return [
    { term: 'INTELIGENCIA ARTIFICIAL', count: 98 },
    { term: 'SOSTENIBILIDAD', count: 74 },
    { term: 'ECONOMÍA CIRCULAR', count: 67 },
    { term: 'CIBERSEGURIDAD', count: 55 },
    { term: 'BLOCKCHAIN', count: 48 },
    { term: 'TELETRABAJO', count: 40 },
    { term: 'ELECCIONES', count: 38 },
    { term: 'ENERGÍA VERDE', count: 36 },
    { term: 'MACHINE LEARNING', count: 31 },
    { term: 'CLOUD COMPUTING', count: 29 },
    { term: 'INFLACIÓN', count: 25 },
    { term: 'STARTUP', count: 22 },
    { term: 'METAVERSO', count: 19 },
    { term: 'GEOPOLÍTICA', count: 16 },
    { term: 'PANDEMIA', count: 13 },
    { term: 'FINTECH', count: 11 },
    { term: 'REGULACIÓN', count: 9 },
    { term: 'DATOS MASIVOS', count: 7 },
  ];
};

// ─── MOCK: nube por categoría ─────────────────────────────────────────────────
const TERMINOS_POR_CATEGORIA = {
  Cultura: [
    { term: 'CINE', count: 80 }, { term: 'MÚSICA', count: 65 }, { term: 'ARTE', count: 50 },
    { term: 'TEATRO', count: 38 }, { term: 'LITERATURA', count: 30 }, { term: 'FESTIVAL', count: 22 },
  ],
  Consumo: [
    { term: 'PRECIOS', count: 75 }, { term: 'SUPERMERCADO', count: 60 }, { term: 'CESTA BÁSICA', count: 48 },
    { term: 'IPC', count: 35 }, { term: 'DERECHOS', count: 27 }, { term: 'FRAUDE', count: 18 },
  ],
  Deportes: [
    { term: 'FÚTBOL', count: 90 }, { term: 'CHAMPIONS', count: 72 }, { term: 'LIGA', count: 60 },
    { term: 'BALONCESTO', count: 40 }, { term: 'TENIS', count: 30 }, { term: 'FORMULA 1', count: 22 },
  ],
  Economía: [
    { term: 'INFLACIÓN', count: 85 }, { term: 'PIB', count: 68 }, { term: 'TIPOS DE INTERÉS', count: 55 },
    { term: 'BOLSA', count: 45 }, { term: 'DEUDA', count: 35 }, { term: 'STARTUP', count: 22 },
  ],
  Entretenimiento: [
    { term: 'STREAMING', count: 78 }, { term: 'SERIES', count: 62 }, { term: 'VIDEOJUEGOS', count: 50 },
    { term: 'REDES SOCIALES', count: 40 }, { term: 'INFLUENCER', count: 28 }, { term: 'PODCAST', count: 20 },
  ],
  Gobierno: [
    { term: 'PRESUPUESTOS', count: 82 }, { term: 'DECRETO', count: 65 }, { term: 'MINISTERIO', count: 52 },
    { term: 'SUBVENCIÓN', count: 40 }, { term: 'CONGRESO', count: 33 }, { term: 'SENADO', count: 22 },
  ],
  Internacional: [
    { term: 'UCRANIA', count: 88 }, { term: 'CHINA', count: 70 }, { term: 'ONU', count: 55 },
    { term: 'OTAN', count: 45 }, { term: 'EEUU', count: 38 }, { term: 'REFUGIADOS', count: 25 },
  ],
  Nacional: [
    { term: 'GOBIERNO', count: 84 }, { term: 'COMUNIDADES', count: 66 }, { term: 'IMPUESTOS', count: 53 },
    { term: 'DESEMPLEO', count: 42 }, { term: 'VIVIENDA', count: 34 }, { term: 'SANIDAD', count: 24 },
  ],
  Política: [
    { term: 'ELECCIONES', count: 91 }, { term: 'PARTIDO', count: 73 }, { term: 'COALICIÓN', count: 58 },
    { term: 'MOCIÓN', count: 44 }, { term: 'CAMPAÑA', count: 36 }, { term: 'VOTACIÓN', count: 25 },
  ],
  Tecnología: [
    { term: 'INTELIGENCIA ARTIFICIAL', count: 95 }, { term: 'CIBERSEGURIDAD', count: 75 },
    { term: 'BLOCKCHAIN', count: 58 }, { term: 'CLOUD', count: 45 },
    { term: 'MACHINE LEARNING', count: 35 }, { term: 'METAVERSO', count: 22 },
  ],
};

const fetchNubeCategoria = async (categoria) => {
  await new Promise((res) => setTimeout(res, 400 + Math.random() * 300));
  return TERMINOS_POR_CATEGORIA[categoria] || [];
};

// ─── COMPONENTE: NUBE DE PALABRAS ────────────────────────────────────────────
const WordCloud = ({ terminos, loading, minFontRem = 0.7, maxFontRem = 2.0 }) => {
  if (loading) {
    return (
      <div className={styles.cloudContent}>
        {[...Array(6)].map((_, i) => (
          <div
            key={i}
            className={`${styles.skeleton}`}
            style={{
              width: `${55 + i * 18}px`,
              height: '16px',
              borderRadius: '4px',
              opacity: 0.35,
            }}
          />
        ))}
      </div>
    );
  }

  if (!terminos || terminos.length === 0) {
    return (
      <div className={styles.cloudEmpty}>
        <p>Sin datos disponibles</p>
      </div>
    );
  }

  const maxCount = Math.max(...terminos.map((t) => t.count));

  return (
    <div className={styles.cloudContent}>
      {terminos.map((t, i) => {
        const ratio = t.count / maxCount;
        const fontSize = minFontRem + ratio * (maxFontRem - minFontRem);
        const opacity = 0.5 + ratio * 0.5;
        return (
          <span
            key={t.term}
            className={styles.cloudWord}
            style={{ fontSize: `${fontSize}rem`, opacity, animationDelay: `${i * 55}ms` }}
          >
            {t.term}
          </span>
        );
      })}
    </div>
  );
};

// ─── COMPONENTE: CARD DE CATEGORÍA ───────────────────────────────────────────
const CategoriaCloud = ({ categoria }) => {
  const [terminos, setTerminos] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let cancelled = false;
    setLoading(true);
    fetchNubeCategoria(categoria).then((data) => {
      if (!cancelled) { setTerminos(data); setLoading(false); }
    });
    return () => { cancelled = true; };
  }, [categoria]);

  return (
    <div className={styles.catCard}>
      <h3 className={styles.catTitle}>
        <span className={styles.accentBar} />
        {categoria.toUpperCase()}
      </h3>
      <WordCloud terminos={terminos} loading={loading} minFontRem={0.65} maxFontRem={1.5} />
    </div>
  );
};

// ─── PÁGINA PRINCIPAL ─────────────────────────────────────────────────────────
const Nubes = () => {
  const [globalTerminos, setGlobalTerminos] = useState([]);
  const [globalLoading, setGlobalLoading] = useState(true);

  useEffect(() => {
    fetchNubeGlobal().then((data) => {
      setGlobalTerminos(data);
      setGlobalLoading(false);
    });
  }, []);

  return (
    <div className={styles.wrapper}>
      <h1 className={styles.pageTitle}>NUBES</h1>

      {/* ── NUBE GLOBAL ── */}
      <section className={styles.globalSection}>
        <div className={styles.globalCard}>
          <h2 className={styles.globalTitle}>
            <span className={styles.accentBar} />
            NUBE GLOBAL DE DESCRIPTORES
          </h2>
          <WordCloud
            terminos={globalTerminos}
            loading={globalLoading}
            minFontRem={0.75}
            maxFontRem={2.2}
          />
        </div>
      </section>

      {/* ── NUBES POR CATEGORÍA ── */}
      <section className={styles.catsSection}>
        <h2 className={styles.sectionTitle}>CATEGORÍAS</h2>
        <div className={styles.catsGrid}>
          {ALL_CATEGORIAS.map((cat) => (
            <CategoriaCloud key={cat} categoria={cat} />
          ))}
        </div>
      </section>
    </div>
  );
};

export default Nubes;