import React, { useState, useMemo, useContext, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import styles from './fuentes.module.css';
import { AuthContext } from '../../context/AuthContext';

// ─── ICONOS (SVG inline para no añadir dependencias) ─────────────────────────
const EditIcon = () => (
  <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor"
       strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
    <path d="M12 20h9" />
    <path d="M16.5 3.5a2.121 2.121 0 1 1 3 3L7 19l-4 1 1-4 12.5-12.5z" />
  </svg>
);

const TrashIcon = () => (
  <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor"
       strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
    <polyline points="3 6 5 6 21 6" />
    <path d="M19 6l-1 14a2 2 0 0 1-2 2H8a2 2 0 0 1-2-2L5 6" />
    <path d="M10 11v6" />
    <path d="M14 11v6" />
    <path d="M9 6V4a2 2 0 0 1 2-2h2a2 2 0 0 1 2 2v2" />
  </svg>
);

// ─── ESTILOS INLINE para los elementos nuevos (modal, botones, chips) ────────
// Los mantenemos aquí para no tocar el CSS module original.
const ui = {
  iconBtn: {
    background: 'transparent', border: '1px solid #e5e7eb', borderRadius: 6,
    padding: 6, cursor: 'pointer', display: 'inline-flex',
    alignItems: 'center', justifyContent: 'center', color: '#374151',
  },
  iconBtnDanger: { color: '#E02020' },
  rowActions:    { display: 'flex', gap: 6, marginLeft: 12 },
  addBtn: {
    background: '#1a73e8', color: '#fff', border: 'none', borderRadius: 6,
    padding: '8px 14px', fontWeight: 600, cursor: 'pointer', fontSize: 14,
    marginLeft: 'auto',
  },
  overlay: {
    position: 'fixed', inset: 0, background: 'rgba(0,0,0,.45)',
    display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 1000,
  },
  modal: {
    background: '#fff', borderRadius: 10, width: 460, maxWidth: '92vw',
    boxShadow: '0 12px 40px rgba(0,0,0,.18)',
    padding: '20px 22px', display: 'flex', flexDirection: 'column', gap: 14,
  },
  modalTitle: { fontSize: 18, fontWeight: 600, margin: 0, color: '#111' },
  modalLabel: { fontSize: 13, fontWeight: 600, color: '#374151', marginBottom: 4 },
  modalInput: {
    width: '100%', boxSizing: 'border-box',
    padding: '8px 10px', border: '1px solid #d1d5db', borderRadius: 6, fontSize: 14,
  },
  chipRow: {
    display: 'flex', flexWrap: 'wrap', gap: 6,
    maxHeight: 130, overflowY: 'auto',
    padding: 6, border: '1px solid #e5e7eb', borderRadius: 6, background: '#fafafa',
  },
  chip: {
    padding: '4px 10px', border: '1px solid #d1d5db', borderRadius: 999,
    fontSize: 13, cursor: 'pointer', background: '#fff', color: '#374151',
    userSelect: 'none',
  },
  chipActive: { background: '#1a73e8', color: '#fff', borderColor: '#1a73e8' },
  chipDisabled: { cursor: 'not-allowed', opacity: 0.55 },
  modalFooter: { display: 'flex', justifyContent: 'flex-end', gap: 8, marginTop: 6 },
  btnGhost: {
    background: 'transparent', border: '1px solid #d1d5db', color: '#374151',
    padding: '8px 14px', borderRadius: 6, cursor: 'pointer', fontWeight: 500, fontSize: 14,
  },
  btnPrimary: {
    background: '#1a73e8', border: 'none', color: '#fff',
    padding: '8px 14px', borderRadius: 6, cursor: 'pointer', fontWeight: 600, fontSize: 14,
  },
  btnDanger: {
    background: '#E02020', border: 'none', color: '#fff',
    padding: '8px 14px', borderRadius: 6, cursor: 'pointer', fontWeight: 600, fontSize: 14,
  },
  modalError: { color: '#E02020', fontSize: 13 },
  fieldGroup: { display: 'flex', flexDirection: 'column' },
};

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

// ─── ACCIONES POR FILA (botones editar/borrar) ───────────────────────────────
const RowActions = ({ onEdit, onDelete }) => {
  const { t } = useTranslation();
  return (
    <div style={ui.rowActions}>
      <button
        type="button"
        style={ui.iconBtn}
        onClick={onEdit}
        title={t('sources.actions.edit', { defaultValue: 'Editar' })}
        aria-label={t('sources.actions.edit', { defaultValue: 'Editar' })}
      >
        <EditIcon />
      </button>
      <button
        type="button"
        style={{ ...ui.iconBtn, ...ui.iconBtnDanger }}
        onClick={onDelete}
        title={t('sources.actions.delete', { defaultValue: 'Borrar' })}
        aria-label={t('sources.actions.delete', { defaultValue: 'Borrar' })}
      >
        <TrashIcon />
      </button>
    </div>
  );
};

// ─── FILA FUENTE ──────────────────────────────────────────────────────────────
const FuenteRow = ({ item, onEdit, onDelete }) => {
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
      <RowActions onEdit={() => onEdit(item)} onDelete={() => onDelete(item)} />
    </div>
  );
};

// ─── FILA CANAL RSS ───────────────────────────────────────────────────────────
const CanalRow = ({ item, onEdit, onDelete }) => {
  const { t } = useTranslation();
  return (
    <div className={styles.row}>
      <span className={styles.rowName}>{item.nombre}</span>
      <div className={styles.rowCats}>
        <span className={styles.catBadge}>
          {t(`categorias.${item.categoria}`, { defaultValue: item.categoria })}
        </span>
      </div>
      <RowActions onEdit={() => onEdit(item)} onDelete={() => onDelete(item)} />
    </div>
  );
};

// ─── MODAL GENÉRICO ───────────────────────────────────────────────────────────
const Modal = ({ open, title, onClose, children }) => {
  if (!open) return null;
  return (
    <div style={ui.overlay} onClick={onClose}>
      <div style={ui.modal} onClick={(e) => e.stopPropagation()}>
        <h3 style={ui.modalTitle}>{title}</h3>
        {children}
      </div>
    </div>
  );
};

// Extrae un mensaje legible del error de axios.
const extractError = (err, fallback) => {
  const detail = err?.response?.data?.detail;
  if (typeof detail === 'string') return detail;
  if (Array.isArray(detail) && detail[0]?.msg) return detail[0].msg;
  return fallback;
};

// ─── MODAL: CREAR / EDITAR FUENTE ─────────────────────────────────────────────
const SourceFormModal = ({ open, mode, initial, onClose, onSubmit }) => {
  const { t } = useTranslation();
  const [name,       setName]       = useState('');
  const [url,        setUrl]        = useState('');
  const [error,      setError]      = useState('');
  const [submitting, setSubmitting] = useState(false);

  useEffect(() => {
    if (open) {
      setName(initial?.nombre ?? '');
      setUrl(initial?.url ?? '');
      setError('');
      setSubmitting(false);
    }
  }, [open, initial]);

  const handleSubmit = async () => {
    if (!name.trim() || !url.trim()) {
      setError(t('sources.modal.required', { defaultValue: 'Todos los campos son obligatorios' }));
      return;
    }
    try {
      setSubmitting(true);
      await onSubmit({ name: name.trim(), url: url.trim() });
      onClose();
    } catch (e) {
      setError(extractError(e, t('sources.modal.error_save', { defaultValue: 'Error al guardar' })));
      setSubmitting(false);
    }
  };

  const isEdit = mode === 'edit';
  const title = isEdit
    ? t('sources.modal.edit_source_title',   { defaultValue: 'Editar fuente' })
    : t('sources.modal.create_source_title', { defaultValue: 'Nueva fuente' });

  return (
    <Modal open={open} title={title} onClose={onClose}>
      <div style={ui.fieldGroup}>
        <label style={ui.modalLabel}>
          {t('sources.modal.field_name', { defaultValue: 'Nombre' })}
        </label>
        <input
          type="text"
          style={ui.modalInput}
          value={name}
          onChange={(e) => setName(e.target.value)}
          placeholder="El País"
          autoFocus
        />
      </div>

      <div style={ui.fieldGroup}>
        <label style={ui.modalLabel}>
          {t('sources.modal.field_url', { defaultValue: 'URL' })}
        </label>
        <input
          type="url"
          style={ui.modalInput}
          value={url}
          onChange={(e) => setUrl(e.target.value)}
          placeholder="https://..."
        />
      </div>

      {error && <div style={ui.modalError}>{error}</div>}

      <div style={ui.modalFooter}>
        <button type="button" style={ui.btnGhost} onClick={onClose} disabled={submitting}>
          {t('sources.actions.cancel', { defaultValue: 'Cancelar' })}
        </button>
        <button type="button" style={ui.btnPrimary} onClick={handleSubmit} disabled={submitting}>
          {submitting
            ? '…'
            : isEdit
              ? t('sources.actions.save',   { defaultValue: 'Guardar' })
              : t('sources.actions.create', { defaultValue: 'Crear' })
          }
        </button>
      </div>
    </Modal>
  );
};

// ─── MODAL: CREAR / EDITAR CANAL RSS ──────────────────────────────────────────
const ChannelFormModal = ({ open, mode, initial, fuentes, categorias, onClose, onSubmit }) => {
  const { t } = useTranslation();
  const [sourceId,   setSourceId]   = useState(null);
  const [categoryId, setCategoryId] = useState(null);
  const [url,        setUrl]        = useState('');
  const [error,      setError]      = useState('');
  const [submitting, setSubmitting] = useState(false);

  useEffect(() => {
    if (open) {
      setSourceId(initial?.fuenteId ?? null);
      setCategoryId(initial?.category_id ?? null);
      setUrl(initial?.url ?? '');
      setError('');
      setSubmitting(false);
    }
  }, [open, initial]);

  const isEdit = mode === 'edit';

  const handleSubmit = async () => {
    if (!sourceId || !categoryId || !url.trim()) {
      setError(t('sources.modal.required', { defaultValue: 'Todos los campos son obligatorios' }));
      return;
    }
    try {
      setSubmitting(true);
      await onSubmit({ sourceId, payload: { url: url.trim(), category_id: categoryId } });
      onClose();
    } catch (e) {
      setError(extractError(e, t('sources.modal.error_save', { defaultValue: 'Error al guardar' })));
      setSubmitting(false);
    }
  };

  const title = isEdit
    ? t('sources.modal.edit_channel_title',   { defaultValue: 'Editar canal RSS' })
    : t('sources.modal.create_channel_title', { defaultValue: 'Nuevo canal RSS' });

  // categorias del backend = [{ id, name }]
  const rawCats = (categorias || []).filter(c => c && typeof c === 'object' && c.id != null);

  return (
    <Modal open={open} title={title} onClose={onClose}>
      <div style={ui.fieldGroup}>
        <label style={ui.modalLabel}>
          {t('sources.modal.field_source', { defaultValue: 'Fuente' })}
        </label>
        <div style={ui.chipRow}>
          {(fuentes || []).length === 0 && (
            <span style={{ fontSize: 13, color: '#666' }}>
              {t('sources.modal.no_sources', { defaultValue: 'No hay fuentes. Crea una fuente primero.' })}
            </span>
          )}
          {(fuentes || []).map((f) => {
            const active = sourceId === f.id;
            // En edición no se puede mover el canal a otra fuente (el backend no lo permite)
            const disabled = isEdit && !active;
            const chipStyle = {
              ...ui.chip,
              ...(active ? ui.chipActive : {}),
              ...(disabled ? ui.chipDisabled : {}),
            };
            return (
              <span
                key={`fuente-${f.id}`}
                style={chipStyle}
                onClick={() => { if (!disabled) setSourceId(f.id); }}
              >
                {f.nombre}
              </span>
            );
          })}
        </div>
      </div>

      <div style={ui.fieldGroup}>
        <label style={ui.modalLabel}>
          {t('sources.modal.field_category', { defaultValue: 'Categoría' })}
        </label>
        <div style={ui.chipRow}>
          {rawCats.length === 0 && (
            <span style={{ fontSize: 13, color: '#666' }}>
              {t('sources.modal.no_categories', { defaultValue: 'No hay categorías disponibles.' })}
            </span>
          )}
          {rawCats.map((c) => {
            const active = categoryId === c.id;
            return (
              <span
                key={`cat-${c.id}`}
                style={{ ...ui.chip, ...(active ? ui.chipActive : {}) }}
                onClick={() => setCategoryId(c.id)}
              >
                {t(`categorias.${c.name}`, { defaultValue: c.name })}
              </span>
            );
          })}
        </div>
      </div>

      <div style={ui.fieldGroup}>
        <label style={ui.modalLabel}>
          {t('sources.modal.field_url', { defaultValue: 'URL' })}
        </label>
        <input
          type="url"
          style={ui.modalInput}
          value={url}
          onChange={(e) => setUrl(e.target.value)}
          placeholder="https://..."
        />
      </div>

      {error && <div style={ui.modalError}>{error}</div>}

      <div style={ui.modalFooter}>
        <button type="button" style={ui.btnGhost} onClick={onClose} disabled={submitting}>
          {t('sources.actions.cancel', { defaultValue: 'Cancelar' })}
        </button>
        <button type="button" style={ui.btnPrimary} onClick={handleSubmit} disabled={submitting}>
          {submitting
            ? '…'
            : isEdit
              ? t('sources.actions.save',   { defaultValue: 'Guardar' })
              : t('sources.actions.create', { defaultValue: 'Crear' })
          }
        </button>
      </div>
    </Modal>
  );
};

// ─── MODAL: CONFIRMAR BORRADO ─────────────────────────────────────────────────
const ConfirmDeleteModal = ({ open, message, onClose, onConfirm }) => {
  const { t } = useTranslation();
  const [submitting, setSubmitting] = useState(false);
  const [error,      setError]      = useState('');

  useEffect(() => {
    if (open) { setSubmitting(false); setError(''); }
  }, [open]);

  const handle = async () => {
    try {
      setSubmitting(true);
      await onConfirm();
      onClose();
    } catch (e) {
      setError(extractError(e, t('sources.modal.error_delete', { defaultValue: 'Error al borrar' })));
      setSubmitting(false);
    }
  };

  return (
    <Modal
      open={open}
      title={t('sources.modal.confirm_title', { defaultValue: 'Confirmar borrado' })}
      onClose={onClose}
    >
      <p style={{ margin: 0, fontSize: 14, color: '#374151', lineHeight: 1.5 }}>{message}</p>
      {error && <div style={ui.modalError}>{error}</div>}
      <div style={ui.modalFooter}>
        <button type="button" style={ui.btnGhost} onClick={onClose} disabled={submitting}>
          {t('sources.actions.cancel', { defaultValue: 'Cancelar' })}
        </button>
        <button type="button" style={ui.btnDanger} onClick={handle} disabled={submitting}>
          {submitting
            ? '…'
            : t('sources.actions.confirm_delete', { defaultValue: 'Borrar' })}
        </button>
      </div>
    </Modal>
  );
};

// ─── PÁGINA PRINCIPAL ─────────────────────────────────────────────────────────
const Fuentes = () => {
  const { t } = useTranslation();
  const {
    fuentes, canales, categorias, newsLoading, newsError,
    createFuente, updateFuente, deleteFuente,
    createCanal,  updateCanal,  deleteCanal,
  } = useContext(AuthContext);

  const [activeTab, setActiveTab]       = useState('fuentes');
  const [searchText, setSearchText]     = useState('');
  const [selectedCats, setSelectedCats] = useState([]);
  const [selectedFts, setSelectedFts]   = useState([]);

  // ── Estado de modales ──────────────────────────────────────────────────────
  // kind: 'fuente' | 'canal' | null
  // mode: 'create' | 'edit' | 'delete' | null
  // item: el elemento sobre el que actuamos (en create es null)
  const [modal, setModal] = useState({ kind: null, mode: null, item: null });
  const closeModal = () => setModal({ kind: null, mode: null, item: null });

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

  // ── Handlers de los botones ────────────────────────────────────────────────
  const openCreate = () =>
    setModal({ kind: isFuentesTab ? 'fuente' : 'canal', mode: 'create', item: null });

  const openEditFuente = (item) => setModal({ kind: 'fuente', mode: 'edit',   item });
  const openEditCanal  = (item) => setModal({ kind: 'canal',  mode: 'edit',   item });
  const openDelFuente  = (item) => setModal({ kind: 'fuente', mode: 'delete', item });
  const openDelCanal   = (item) => setModal({ kind: 'canal',  mode: 'delete', item });

  // ── Submit handlers (lanzan al backend vía AuthContext) ────────────────────
  const submitFuenteForm = async ({ name, url }) => {
    if (modal.mode === 'edit') {
      await updateFuente(modal.item.id, { name, url });
    } else {
      await createFuente({ name, url });
    }
  };

  const submitCanalForm = async ({ sourceId, payload }) => {
    if (modal.mode === 'edit') {
      // El backend no permite cambiar la fuente de un canal por PUT,
      // así que usamos siempre la fuenteId original del canal.
      const channelId = modal.item._backendId ?? modal.item.id;
      await updateCanal(modal.item.fuenteId, channelId, payload);
    } else {
      await createCanal(sourceId, payload);
    }
  };

  const confirmDelete = async () => {
    if (!modal.item) return;
    if (modal.kind === 'fuente') {
      await deleteFuente(modal.item.id);
    } else {
      const channelId = modal.item._backendId ?? modal.item.id;
      await deleteCanal(modal.item.fuenteId, channelId);
    }
  };

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

  // Mensaje de confirmación de borrado, según el tipo
  const deleteMessage = modal.mode === 'delete'
    ? (modal.kind === 'fuente'
        ? t('sources.modal.delete_source_confirm', {
            defaultValue: '¿Seguro que quieres borrar la fuente "{{name}}"? Se borrarán también todos sus canales RSS asociados.',
            name: modal.item?.nombre ?? '',
          })
        : t('sources.modal.delete_channel_confirm', {
            defaultValue: '¿Seguro que quieres borrar el canal RSS "{{name}}"?',
            name: modal.item?.nombre ?? '',
          })
      )
    : '';

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

          {/* Botón "+ Fuente" / "+ Canal RSS" según pestaña activa */}
          <button type="button" style={ui.addBtn} onClick={openCreate}>
            {isFuentesTab
              ? t('sources.actions.add_source',  { defaultValue: '+ Fuente' })
              : t('sources.actions.add_channel', { defaultValue: '+ Canal RSS' })}
          </button>
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
                  : filteredFuentes.map((item) => (
                      <FuenteRow
                        key={`f-row-${item.id}`}
                        item={item}
                        onEdit={openEditFuente}
                        onDelete={openDelFuente}
                      />
                    ))
              ) : (
                filteredCanales.length === 0
                  ? <div className={styles.emptyState}>{t('sources.empty.channels')}</div>
                  : filteredCanales.map((item) => (
                      <CanalRow
                        key={`c-row-${item.id}`}
                        item={item}
                        onEdit={openEditCanal}
                        onDelete={openDelCanal}
                      />
                    ))
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

      {/* ── MODALES ──────────────────────────────────────────────────────── */}
      <SourceFormModal
        open={modal.kind === 'fuente' && (modal.mode === 'create' || modal.mode === 'edit')}
        mode={modal.mode}
        initial={modal.item}
        onClose={closeModal}
        onSubmit={submitFuenteForm}
      />

      <ChannelFormModal
        open={modal.kind === 'canal' && (modal.mode === 'create' || modal.mode === 'edit')}
        mode={modal.mode}
        initial={modal.item}
        fuentes={safeFuentes}
        categorias={categorias}
        onClose={closeModal}
        onSubmit={submitCanalForm}
      />

      <ConfirmDeleteModal
        open={modal.mode === 'delete'}
        message={deleteMessage}
        onClose={closeModal}
        onConfirm={confirmDelete}
      />
    </div>
  );
};

export default Fuentes;