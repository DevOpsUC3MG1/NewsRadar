import React, { useState, useEffect, useCallback } from 'react';
import styles from './resumen.module.css';

// --- DATOS INICIALES ---
const CATEGORIAS_DATA = {
  tecnologia: {
    label: 'TECNOLOGÍA',
    tags: ['IA', 'Nube', 'SaaS', 'Hardware', 'Software', 'Frontend'],
  },
  economia: {
    label: 'ECONOMÍA',
    tags: ['Inflación', 'PIB', 'Mercados', 'Bolsa', 'Deuda', 'Startup'],
  },
  politica: {
    label: 'POLÍTICA',
    tags: ['Elecciones', 'Ley', 'Gobierno', 'Tratado', 'Cumbre', 'Voto'],
  },
  salud: {
    label: 'SALUD',
    tags: ['Vacuna', 'Virus', 'Hospital', 'Dieta', 'Medicina', 'Genoma'],
  },
};

// --- MOCK: simula el backend que devuelve términos con ocurrencias ---
const fetchDescriptores = async (selectedTagsMap) => {
  await new Promise((res) => setTimeout(res, 600));

  const allSelected = Object.values(selectedTagsMap).flat();
  if (allSelected.length === 0) return [];

  const pool = [
    { term: 'INTELIGENCIA ARTIFICIAL', count: 98 },
    { term: 'SOSTENIBILIDAD', count: 74 },
    { term: 'ECONOMÍA CIRCULAR', count: 67 },
    { term: 'CIBERSEGURIDAD', count: 55 },
    { term: 'BLOCKCHAIN', count: 48 },
    { term: 'TELETRABAJO', count: 40 },
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
    { term: 'OPEN SOURCE', count: 8 },
    { term: 'DATOS MASIVOS', count: 7 },
  ];

  // Retornamos un subconjunto variable según cuántas etiquetas hay seleccionadas
  const count = Math.min(pool.length, 5 + allSelected.length * 2);
  return pool.slice(0, count);
};

// --- NUBE DE DESCRIPTORES ---
const NubeDescriptores = ({ terminos, loading }) => {
  if (loading) {
    return (
      <div className={styles.nubeContent}>
        {[...Array(8)].map((_, i) => (
          <div
            key={i}
            className={`${styles.skeleton} ${styles.skeletonWord}`}
            style={{ width: `${60 + Math.random() * 80}px`, height: '20px', opacity: 0.4 }}
          />
        ))}
      </div>
    );
  }

  if (terminos.length === 0) {
    return (
      <div className={styles.nubeEmpty}>
        <p>Selecciona categorías para ver los descriptores más relevantes</p>
      </div>
    );
  }

  const maxCount = Math.max(...terminos.map((t) => t.count));

  return (
    <div className={styles.nubeContent}>
      {terminos.map((t, i) => {
        const ratio = t.count / maxCount;
        const fontSize = 0.75 + ratio * 1.5; // rem: 0.75 → 2.25
        const opacity = 0.55 + ratio * 0.45;
        return (
          <span
            key={t.term}
            className={styles.nubeWord}
            style={{
              fontSize: `${fontSize}rem`,
              opacity,
              animationDelay: `${i * 60}ms`,
            }}
          >
            {t.term}
          </span>
        );
      })}
    </div>
  );
};

// --- CARD DE CATEGORÍA ---
const CategoriaCard = ({ id, label, tags, selectedTags, onToggle }) => {
  return (
    <div className={styles.categoriaCard}>
      <h3 className={styles.categoriaTitle}>
        <span className={styles.accentBar} />
        {label}
      </h3>
      <div className={styles.tagsWrapper}>
        {tags.map((tag) => {
          const isSelected = selectedTags.includes(tag);
          return (
            <button
              key={tag}
              className={`${styles.tag} ${isSelected ? styles.tagSelected : ''}`}
              onClick={() => onToggle(id, tag)}
            >
              {tag}
            </button>
          );
        })}
      </div>
    </div>
  );
};

// --- PÁGINA PRINCIPAL ---
const Resumen = () => {
  // selectedTags: { tecnologia: ['IA'], economia: ['Inflación'], ... }
  const [selectedTags, setSelectedTags] = useState({
    tecnologia: ['IA'],
    economia: ['Inflación'],
    politica: ['Elecciones'],
    salud: ['Vacuna'],
  });
  const [descriptores, setDescriptores] = useState([]);
  const [loadingNube, setLoadingNube] = useState(false);

  const handleToggle = (categoriaId, tag) => {
    setSelectedTags((prev) => {
      const current = prev[categoriaId] || [];
      const updated = current.includes(tag)
        ? current.filter((t) => t !== tag)
        : [...current, tag];
      return { ...prev, [categoriaId]: updated };
    });
  };

  // Re-fetcha cada vez que cambian las selecciones
  useEffect(() => {
    let cancelled = false;
    const load = async () => {
      setLoadingNube(true);
      const result = await fetchDescriptores(selectedTags);
      if (!cancelled) {
        setDescriptores(result);
        setLoadingNube(false);
      }
    };
    load();
    return () => { cancelled = true; };
  }, [selectedTags]);

  return (
    <div className={styles.resumenWrapper}>

      {/* TÍTULO */}
      <h1 className={styles.pageTitle}>RESUMEN</h1>

      {/* NUBE GLOBAL */}
      <section className={styles.nubeSection}>
        <div className={styles.nubeCard}>
          <h2 className={styles.nubeTitle}>
            <span className={styles.accentBar} />
            NUBE GLOBAL DE DESCRIPTORES
          </h2>
          <NubeDescriptores terminos={descriptores} loading={loadingNube} />
        </div>
      </section>

      {/* CATEGORÍAS */}
      <section className={styles.categoriasSection}>
        <h2 className={styles.sectionTitle}>CATEGORÍAS</h2>
        <div className={styles.categoriasGrid}>
          {Object.entries(CATEGORIAS_DATA).map(([id, { label, tags }]) => (
            <CategoriaCard
              key={id}
              id={id}
              label={label}
              tags={tags}
              selectedTags={selectedTags[id] || []}
              onToggle={handleToggle}
            />
          ))}
        </div>
      </section>

    </div>
  );
};

export default Resumen;