// frontend/src/pages/alerts/alerts.jsx
import React, { useState, useEffect, useMemo } from 'react';
import {
  Pencil, Trash2, Plus, Info, X,
  AlertCircle, Save, Ban, GripVertical, Search
} from 'lucide-react';
import { DragDropContext, Droppable, Draggable } from '@hello-pangea/dnd';
import styles from './alerts.module.css';

const CATEGORIAS_DISPONIBLES = [
  "Política", "Economía", "Salud", "Tecnología",
  "Seguridad", "Terrorismo", "Internacional", "Deportes"
];

// Datos simulados para probar la cascada (En el futuro esto vendrá de tu API)
const MOCK_SOURCES = [
  {
    id: "src_elpais", name: "El País",
    channels: [
      { id: "ch_ep_pol", name: "Portada España", category: "Política" },
      { id: "ch_ep_eco", name: "Cinco Días", category: "Economía" },
      { id: "ch_ep_tec", name: "Tecnología", category: "Tecnología" }
    ]
  },
  {
    id: "src_rtve", name: "RTVE",
    channels: [
      { id: "ch_rtve_pol", name: "Temas España", category: "Política" },
      { id: "ch_rtve_eco", name: "Economía", category: "Economía" },
      { id: "ch_rtve_sal", name: "Salud", category: "Salud" }
    ]
  },
  {
    id: "src_marca", name: "Marca",
    channels: [
      { id: "ch_marca_fut", name: "Fútbol", category: "Deportes" },
      { id: "ch_marca_mot", name: "Motor", category: "Deportes" }
    ]
  }
];

const Alerts = () => {
  const [alerts, setAlerts] = useState([
    {
      id: '1', nombre: "Atentado en Madrid", keyword: "Atentado",
      descriptores: ["bomba", "policía"], categorias: ["Seguridad"],
      information_sources_ids: [], rss_channels_ids: [],
      periodicidad: "0 0 * * *"
    },
  ]);

  const [isModalOpen, setIsModalOpen] = useState(false);
  const [editingAlert, setEditingAlert] = useState(null);
  const [showConfirmClose, setShowConfirmClose] = useState(false);
  const [showConfirmDelete, setShowConfirmDelete] = useState(null);
  const [errorMsg, setErrorMsg] = useState("");

  // Estado para el buscador de canales
  const [channelSearch, setChannelSearch] = useState("");

  const [form, setForm] = useState({
    nombre: '',
    keyword: '',
    periodicidad: '',
    descriptores: [],
    categorias: [],
    information_sources_ids: [],
    rss_channels_ids: []
  });

  const [suggestedDescriptors, setSuggestedDescriptors] = useState([]);

  // Validación de expresión cron
  const isValidCron = (cron) => {
    const cronRegex = /^(\*|([0-5]?\d)(-[0-5]?\d)?(,[0-5]?\d)*)(\s+(\*|([0-5]?\d)(-[0-5]?\d)?(,[0-5]?\d)*)){4}$/;
    return cronRegex.test(cron.trim());
  };

  const handleSave = () => {
    if (!form.nombre || !form.keyword || !form.periodicidad || form.categorias.length === 0) {
      setErrorMsg("Nombre, keyword, periodicidad y al menos una categoría son obligatorios.");
      return;
    }
    if (!isValidCron(form.periodicidad)) {
      setErrorMsg("La expresión cron no es válida. Ejemplo: * * * * *");
      return;
    }

    setErrorMsg("");

    if (editingAlert) {
      setAlerts(alerts.map(a => a.id === editingAlert.id ? { ...form, id: a.id } : a));
    } else {
      const newAlert = { ...form, id: Date.now().toString() };
      setAlerts([...alerts, newAlert]);
    }
    setIsModalOpen(false);
  };

  const handleCloseAttempt = () => {
    if (form.nombre || form.keyword || form.periodicidad || form.descriptores.length > 0 || form.categorias.length > 0) {
      setShowConfirmClose(true);
    } else {
      setIsModalOpen(false);
    }
  };

  const handleToggleDescriptor = (desc) => {
    const current = form.descriptores;
    setForm({ ...form, descriptores: current.includes(desc) ? current.filter(d => d !== desc) : [...current, desc] });
  };

  const handleToggleCategory = (cat) => {
    const current = form.categorias;
    setForm({ ...form, categorias: current.includes(cat) ? current.filter(c => c !== cat) : [...current, cat] });
  };

  const handleToggleSource = (sourceId) => {
    const current = form.information_sources_ids;
    setForm({ ...form, information_sources_ids: current.includes(sourceId) ? current.filter(id => id !== sourceId) : [...current, sourceId] });
  };

  const handleToggleChannel = (channelId) => {
    const current = form.rss_channels_ids;
    setForm({ ...form, rss_channels_ids: current.includes(channelId) ? current.filter(id => id !== channelId) : [...current, channelId] });
  };

  useEffect(() => {
    if (form.keyword.length > 2) {
      setSuggestedDescriptors(["urgente", "oficial", "noticia", "relevante", "impacto", "suceso"]);
    }
  }, [form.keyword]);

  // --- LÓGICA DE FILTRADO EN CASCADA ---
  // 1. Fuentes disponibles basadas en las categorías seleccionadas
  const availableSources = useMemo(() => {
    return MOCK_SOURCES.filter(source =>
      source.channels.some(ch => form.categorias.includes(ch.category))
    );
  }, [form.categorias]);

  // 2. Canales disponibles agrupados por fuente, basados en categorías, fuentes y búsqueda
  const availableChannelsBySource = useMemo(() => {
    const grouped = {};
    MOCK_SOURCES.filter(src => form.information_sources_ids.includes(src.id)).forEach(source => {
      const validChannels = source.channels.filter(ch =>
        form.categorias.includes(ch.category) &&
        ch.name.toLowerCase().includes(channelSearch.toLowerCase())
      );
      if (validChannels.length > 0) {
        grouped[source.name] = validChannels;
      }
    });
    return grouped;
  }, [form.categorias, form.information_sources_ids, channelSearch]);

  return (
    <div className={styles.alertsWrapper}>
      <div className={styles.header}>
        <div className={styles.titleGroup}>
          <h1 className={styles.pageTitle}>ALERTAS</h1>
          <span className={styles.counter}>{alerts.length} activas</span>
        </div>
        <button className={styles.newAlertBtn} onClick={() => {
          setEditingAlert(null);
          setForm({nombre:'', keyword:'', periodicidad:'', descriptores:[], categorias:[], information_sources_ids:[], rss_channels_ids:[]});
          setChannelSearch("");
          setErrorMsg("");
          setIsModalOpen(true);
        }}>
          <Plus size={18} /> NUEVA ALERTA
        </button>
      </div>

      <div className={styles.tableContainer}>
        <DragDropContext onDragEnd={(result) => {
          if (!result.destination) return;
          const items = Array.from(alerts);
          const [reorderedItem] = items.splice(result.source.index, 1);
          items.splice(result.destination.index, 0, reorderedItem);
          setAlerts(items);
        }}>
          <table className={styles.alertsTable}>
            <thead>
              <tr>
                <th style={{ width: '40px' }}></th>
                <th>NOMBRE</th>
                <th>FILTROS</th>
                <th>PERIODICIDAD</th>
                <th className={styles.actionsHeader}>ACCIONES</th>
              </tr>
            </thead>
            <Droppable droppableId="alerts-list">
              {(provided) => (
                <tbody {...provided.droppableProps} ref={provided.innerRef}>
                  {alerts.map((alert, index) => (
                    <Draggable key={alert.id} draggableId={alert.id} index={index}>
                      {(provided) => (
                        <tr ref={provided.innerRef} {...provided.draggableProps}>
                          <td {...provided.dragHandleProps} className={styles.dragCell}><GripVertical size={18} color="#ccc" /></td>
                          <td className={styles.alertName}>{alert.nombre}</td>
                          <td>
                            <div style={{fontSize: '0.8rem', color: '#666', lineHeight: '1.4'}}>
                              <strong>Categorías:</strong> {alert.categorias.join(", ")} <br/>
                              <strong>Fuentes:</strong> {alert.information_sources_ids.length} selec. <br/>
                              <strong>Canales:</strong> {alert.rss_channels_ids.length} selec.
                            </div>
                          </td>
                          <td className={styles.cronText}>{alert.periodicidad}</td>
                          <td className={styles.actionsCell}>
                            <button className={styles.editBtn} onClick={() => {setEditingAlert(alert); setForm(alert); setChannelSearch(""); setErrorMsg(""); setIsModalOpen(true);}}><Pencil size={18} /></button>
                            <button className={styles.deleteBtn} onClick={() => setShowConfirmDelete(alert.id)}><Trash2 size={18} /></button>
                          </td>
                        </tr>
                      )}
                    </Draggable>
                  ))}
                  {provided.placeholder}
                </tbody>
              )}
            </Droppable>
          </table>
        </DragDropContext>
      </div>

      {/* --- MODAL CREACIÓN / EDICIÓN --- */}
      {isModalOpen && (
        <div className={styles.modalOverlay}>
          <div className={styles.modalContent}>
            <div className={styles.modalHeader}>
              <h2>{editingAlert ? 'EDITAR ALERTA' : 'CREAR NUEVA ALERTA'}</h2>
              <button onClick={handleCloseAttempt} className={styles.closeIcon}><X /></button>
            </div>

            <div className={styles.formBody}>
              {errorMsg && <div className={styles.errorBanner}>{errorMsg}</div>}

              <div className={styles.inputGroupFull}>
                <label>NOMBRE DE LA ALERTA</label>
                <input type="text" value={form.nombre} onChange={(e) => setForm({...form, nombre: e.target.value})} placeholder="Nombre..." />
              </div>

              <div className={styles.row}>
                <div className={styles.inputGroup}>
                  <label>PALABRA CLAVE</label>
                  <input type="text" value={form.keyword} onChange={(e) => setForm({...form, keyword: e.target.value})} placeholder="Keyword..." />
                </div>
                <div className={styles.inputGroup}>
                  <label className={styles.labelWithInfo}>
                    PERIODICIDAD
                    <div className={styles.infoWrapper}><Info size={14} /><span className={styles.tooltip}>Formato: min hora día mes sem</span></div>
                  </label>
                  <input type="text" value={form.periodicidad} onChange={(e) => setForm({...form, periodicidad: e.target.value})} placeholder="* * * * *" />
                </div>
              </div>

              <div className={styles.sectionContainer}>
                <label>DESCRIPTORES GENERADOS (IA)</label>
                <div className={styles.tagsContainer}>
                  {suggestedDescriptors.map((desc, i) => (
                    <button key={i} className={form.descriptores.includes(desc) ? styles.tagSelected : styles.tagUnselected} onClick={() => handleToggleDescriptor(desc)}>
                      {desc}
                    </button>
                  ))}
                </div>
              </div>

              <div className={styles.sectionContainer}>
                <label>1. CATEGORÍAS (Requerido)</label>
                <div className={styles.checkboxGrid}>
                  {CATEGORIAS_DISPONIBLES.map((cat) => (
                    <label key={cat} className={styles.customCheckboxContainer}>
                      <input type="checkbox" checked={form.categorias.includes(cat)} onChange={() => handleToggleCategory(cat)} className={styles.hiddenCheckbox} />
                      <span className={styles.checkmark}></span>
                      {cat}
                    </label>
                  ))}
                </div>
              </div>

              {/* PASO 2: FUENTES EN CASCADA (SIEMPRE VISIBLE) */}
              <div className={styles.sectionContainer}>
                <label>2. FUENTES DISPONIBLES (Opcional)</label>

                {form.categorias.length === 0 ? (
                  <div className={styles.emptyContainerBox}>
                    <p className={styles.emptyStateText}>👆 Selecciona al menos una categoría para ver las fuentes.</p>
                  </div>
                ) : availableSources.length === 0 ? (
                  <div className={styles.emptyContainerBox}>
                    <p className={styles.emptyStateText}>No hay fuentes para las categorías seleccionadas.</p>
                  </div>
                ) : (
                  <div className={styles.tagsContainer}>
                    {availableSources.map(source => (
                      <button
                        key={source.id}
                        className={form.information_sources_ids.includes(source.id) ? styles.tagSelected : styles.tagUnselected}
                        onClick={() => handleToggleSource(source.id)}
                      >
                        {source.name}
                      </button>
                    ))}
                  </div>
                )}
              </div>

              {/* PASO 3: CANALES EN CASCADA (SIEMPRE VISIBLE) */}
              <div className={styles.sectionContainer}>
                <div className={styles.labelWithSearch}>
                  <label>3. CANALES RSS ESPECÍFICOS</label>
                  <div className={styles.searchBox}>
                    <Search size={14} color="#888" />
                    <input
                      type="text"
                      placeholder="Buscar canal..."
                      value={channelSearch}
                      onChange={(e) => setChannelSearch(e.target.value)}
                      disabled={form.information_sources_ids.length === 0}
                    />
                  </div>
                </div>

                <div className={styles.channelsContainer}>
                  {form.information_sources_ids.length === 0 ? (
                    <div className={styles.emptyContainerBox} style={{ border: 'none', backgroundColor: 'transparent' }}>
                      <p className={styles.emptyStateText}>👆 Selecciona al menos una fuente para ver sus canales.</p>
                    </div>
                  ) : Object.keys(availableChannelsBySource).length === 0 ? (
                    <div className={styles.emptyContainerBox} style={{ border: 'none', backgroundColor: 'transparent' }}>
                      <p className={styles.emptyStateText}>No se encontraron canales con esos filtros.</p>
                    </div>
                  ) : (
                    Object.entries(availableChannelsBySource).map(([sourceName, channels]) => (
                      <div key={sourceName} className={styles.sourceCard}>
                        <h4 className={styles.sourceCardTitle}>{sourceName}</h4>
                        <div className={styles.channelList}>
                          {channels.map(ch => (
                            <label key={ch.id} className={styles.customCheckboxContainer}>
                              <input
                                type="checkbox"
                                checked={form.rss_channels_ids.includes(ch.id)}
                                onChange={() => handleToggleChannel(ch.id)}
                                className={styles.hiddenCheckbox}
                              />
                              <span className={styles.checkmark}></span>
                              {ch.name} <span className={styles.channelCategoryBadge}>{ch.category}</span>
                            </label>
                          ))}
                        </div>
                      </div>
                    ))
                  )}
                </div>
              </div>

            </div>

            <div className={styles.modalFooter}>
              <button className={styles.cancelBtn} onClick={handleCloseAttempt}>
                <Ban size={18} /> CANCELAR
              </button>
              <button className={styles.saveBtn} onClick={handleSave}>
                <Save size={18} /> GUARDAR
              </button>
            </div>
          </div>
        </div>
      )}

      {/* --- DIÁLOGOS DE CONFIRMACIÓN --- */}
      {showConfirmClose && (
        <div className={styles.miniOverlay}>
          <div className={styles.confirmBox}>
            <AlertCircle size={40} color="#FFBB28" />
            <p>¿Estás seguro de cerrar la edición? Perderás los cambios no guardados.</p>
            <div className={styles.confirmActions}>
              <button className={styles.confirmBoxBtnDanger} onClick={() => {setShowConfirmClose(false); setIsModalOpen(false);}}>Descartar</button>
              <button className={styles.confirmBoxBtnSafe} onClick={() => setShowConfirmClose(false)}>Seguir editando</button>
            </div>
          </div>
        </div>
      )}
      {showConfirmDelete && (
        <div className={styles.miniOverlay}>
          <div className={styles.confirmBox}>
            <Trash2 size={40} color="#E02020" />
            <p>¿Estás seguro de eliminar esta alerta permanentemente?</p>
            <div className={styles.confirmActions}>
              <button className={styles.confirmBoxBtnSafe} onClick={() => setShowConfirmDelete(null)}>No, mantener</button>
              <button className={styles.confirmBoxBtnDanger} onClick={() => { setAlerts(alerts.filter(a => a.id !== showConfirmDelete)); setShowConfirmDelete(null); }}>Confirmar</button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default Alerts;