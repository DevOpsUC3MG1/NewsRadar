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

// Datos simulados (Se sustituirán por llamadas a la API o CatalogContext)
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
      id: '1', nombre: "Seguimiento Ibex 35", keyword: "Ibex",
      descriptores: ["bolsa", "mercado"], categorias: ["Economía"],
      information_sources_ids: ["src_elpais"], rss_channels_ids: ["ch_ep_eco"],
      periodicidad: "0 9 * * 1-5"
    },
  ]);

  const [isModalOpen, setIsModalOpen] = useState(false);
  const [editingAlert, setEditingAlert] = useState(null);
  const [showConfirmClose, setShowConfirmClose] = useState(false);
  const [showConfirmDelete, setShowConfirmDelete] = useState(null);
  const [errorMsg, setErrorMsg] = useState("");
  const [channelSearch, setChannelSearch] = useState("");

  const [form, setForm] = useState({
    nombre: '', keyword: '', periodicidad: '',
    descriptores: [], categorias: [],
    information_sources_ids: [], rss_channels_ids: []
  });

  const [suggestedDescriptors, setSuggestedDescriptors] = useState([]);

  // Validación básica de CRON
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
      setErrorMsg("La expresión cron no es válida.");
      return;
    }
    if (editingAlert) {
      setAlerts(alerts.map(a => a.id === editingAlert.id ? { ...form, id: a.id } : a));
    } else {
      setAlerts([...alerts, { ...form, id: Date.now().toString() }]);
    }
    setIsModalOpen(false);
  };

  const handleCloseAttempt = () => {
    const isDirty = form.nombre || form.keyword || form.categorias.length > 0;
    if (isDirty) setShowConfirmClose(true);
    else setIsModalOpen(false);
  };

  const handleToggleDescriptor = (desc) => {
    setForm(prev => ({
      ...prev,
      descriptores: prev.descriptores.includes(desc)
        ? prev.descriptores.filter(d => d !== desc)
        : [...prev.descriptores, desc]
    }));
  };

  // --- FILTRADO EN CASCADA ---
  const availableSources = useMemo(() => {
    return MOCK_SOURCES.filter(src => src.channels.some(ch => form.categorias.includes(ch.category)));
  }, [form.categorias]);

  const availableChannelsBySource = useMemo(() => {
    const grouped = {};
    MOCK_SOURCES.filter(src => form.information_sources_ids.includes(src.id)).forEach(source => {
      const validChannels = source.channels.filter(ch =>
        form.categorias.includes(ch.category) &&
        ch.name.toLowerCase().includes(channelSearch.toLowerCase())
      );
      if (validChannels.length > 0) grouped[source.name] = validChannels;
    });
    return grouped;
  }, [form.categorias, form.information_sources_ids, channelSearch]);

  const allAvailableChannelIds = useMemo(() => Object.values(availableChannelsBySource).flat().map(ch => ch.id), [availableChannelsBySource]);

  // --- TRADUCCIÓN DE IDs A NOMBRES PARA LA TABLA ---
  const getSourceNames = (ids) => ids.map(id => MOCK_SOURCES.find(s => s.id === id)?.name || id).join(", ");
  const getChannelNames = (ids) => {
    const all = MOCK_SOURCES.flatMap(s => s.channels);
    return ids.map(id => all.find(c => c.id === id)?.name || id).join(", ");
  };

  // --- ESTILOS DE BOTONES "PÍLDORA" ---
  const btnPillStyle = (type) => ({
    background: type === 'all' ? '#EEF2FF' : '#F7FAFC',
    border: `1px solid ${type === 'all' ? '#D0D7F6' : '#E2E8F0'}`,
    color: type === 'all' ? '#4B6A9B' : '#718096',
    fontSize: '0.75rem', fontWeight: '600', cursor: 'pointer',
    padding: '4px 12px', borderRadius: '20px', transition: 'all 0.2s ease',
  });

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
          setErrorMsg(""); setIsModalOpen(true);
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
                <th style={{ width: '20%' }}>NOMBRE</th>
                <th>FILTROS</th>
                <th style={{ width: '15%' }}>PERIODICIDAD</th>
                <th className={styles.actionsHeader} style={{ width: '10%' }}>ACCIONES</th>
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
                          <td style={{ padding: '12px 16px' }}>
                            <div style={{ fontSize: '0.85rem', color: '#555', lineHeight: '1.6' }}>
                              <div><strong>Palabra clave:</strong> <span style={{ fontWeight: '600', color: '#0E0E1D' }}>{alert.keyword}</span></div>
                              {alert.categorias.length > 0 && <div><strong>Categorías:</strong> {alert.categorias.join(", ")}</div>}
                              {alert.information_sources_ids.length > 0 && <div><strong>Fuentes:</strong> {getSourceNames(alert.information_sources_ids)}</div>}
                              {alert.rss_channels_ids.length > 0 && <div><strong>Canales:</strong> {getChannelNames(alert.rss_channels_ids)}</div>}
                            </div>
                          </td>
                          <td className={styles.cronText}>{alert.periodicidad}</td>
                          <td className={styles.actionsCell}>
                            <button className={styles.editBtn} onClick={() => {setEditingAlert(alert); setForm(alert); setIsModalOpen(true);}}><Pencil size={18} /></button>
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
                    <div className={styles.infoWrapper}>
                      <Info size={14} />
                      {/* FIX DEL TOOLTIP: Modificamos top, bottom, margin, left y transform para que baje */}
                      <div className={styles.tooltip} style={{
                        width: 'max-content',
                        maxWidth: '350px',
                        padding: '12px',
                        textAlign: 'left',
                        lineHeight: '1.5',
                        fontSize: '0.8rem',
                        fontWeight: 'normal',
                        zIndex: 100,
                        top: '100%',            /* Fuerza a que el recuadro empiece debajo del icono */
                        bottom: 'auto',         /* Anula el comportamiento normal de ir hacia arriba */
                        marginTop: '10px',      /* Separa el recuadro un poco del icono */
                        left: '0',              /* Lo alinea a la izquierda para no salirse de la pantalla */
                        transform: 'none'       /* Elimina centrados extraños */
                      }}>
                        <strong style={{ display: 'block', marginBottom: '8px', fontSize: '0.85rem' }}>Formato CRON (5 valores)</strong>
                        <div style={{ display: 'grid', gridTemplateColumns: '50px 1fr', gap: '4px', marginBottom: '8px' }}>
                          <strong>min:</strong> <span>0-59</span>
                          <strong>hora:</strong> <span>0-23</span>
                          <strong>día:</strong> <span>1-31</span>
                          <strong>mes:</strong> <span>1-12</span>
                          <strong>sem:</strong> <span>0-6 (0=Dom)</span>
                        </div>

                        <div style={{ borderTop: '1px solid rgba(255,255,255,0.2)', paddingTop: '8px', marginBottom: '8px' }}>
                          <strong style={{ display: 'block', marginBottom: '4px' }}>Caracteres especiales:</strong>
                          <div style={{ display: 'grid', gridTemplateColumns: '20px 1fr', gap: '4px' }}>
                            <strong style={{textAlign: 'center'}}>*</strong> <span>Cualquier valor</span>
                            <strong style={{textAlign: 'center'}}>,</strong> <span>Lista (ej. 1,15)</span>
                            <strong style={{textAlign: 'center'}}>-</strong> <span>Rango (ej. 1-5)</span>
                            <strong style={{textAlign: 'center'}}>/</strong> <span>Intervalo (ej. */15)</span>
                          </div>
                        </div>

                        <div style={{ borderTop: '1px solid rgba(255,255,255,0.2)', paddingTop: '8px' }}>
                          <strong>Estructura:</strong><br/>
                          <code style={{ background: 'rgba(0,0,0,0.2)', padding: '2px 4px', borderRadius: '4px', display: 'inline-block', marginBottom: '8px' }}>min hora día mes sem</code><br/>
                          <strong>Ejemplos rápidos:</strong><br/>
                          <code style={{ background: 'rgba(0,0,0,0.2)', padding: '2px 4px', borderRadius: '4px', marginRight: '6px' }}>* * * * *</code> Cada minuto<br/>
                          <code style={{ background: 'rgba(0,0,0,0.2)', padding: '2px 4px', borderRadius: '4px', marginRight: '6px' }}>0 9 * * 1-5</code> Lun-Vie a las 09:00
                        </div>
                      </div>
                    </div>
                  </label>
                  <input type="text" value={form.periodicidad} onChange={(e) => setForm({...form, periodicidad: e.target.value})} placeholder="* * * * *" />
                </div>
              </div>

              <div className={styles.sectionContainer}>
                <label>DESCRIPTORES GENERADOS (IA)</label>
                <div className={styles.tagsContainer}>
                  {suggestedDescriptors.map((desc, i) => (
                    <button type="button" key={i} className={form.descriptores.includes(desc) ? styles.tagSelected : styles.tagUnselected} onClick={() => handleToggleDescriptor(desc)}>
                      {desc}
                    </button>
                  ))}
                </div>
              </div>

              {/* CATEGORÍAS */}
              <div className={styles.sectionContainer}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '10px' }}>
                  <label style={{ margin: 0 }}>1. CATEGORÍAS (Requerido)</label>
                  <div style={{ display: 'flex', gap: '8px' }}>
                    <button type="button" style={btnPillStyle('all')} onClick={() => setForm({...form, categorias: CATEGORIAS_DISPONIBLES})}>Seleccionar todo</button>
                    <button type="button" style={btnPillStyle('none')} onClick={() => setForm({...form, categorias: []})}>Deseleccionar todo</button>
                  </div>
                </div>
                <div className={styles.checkboxGrid}>
                  {CATEGORIAS_DISPONIBLES.map(cat => (
                    <label key={cat} className={styles.customCheckboxContainer}>
                      <input type="checkbox" checked={form.categorias.includes(cat)} onChange={() => handleToggleCategory(cat)} className={styles.hiddenCheckbox} />
                      <span className={styles.checkmark}></span> {cat}
                    </label>
                  ))}
                </div>
              </div>

              {/* FUENTES */}
              <div className={styles.sectionContainer}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '10px' }}>
                  <label style={{ margin: 0 }}>2. FUENTES DISPONIBLES (Opcional)</label>
                  {form.categorias.length > 0 && availableSources.length > 0 && (
                    <div style={{ display: 'flex', gap: '8px' }}>
                      <button type="button" style={btnPillStyle('all')} onClick={() => setForm({...form, information_sources_ids: availableSources.map(s => s.id)})}>Seleccionar todo</button>
                      <button type="button" style={btnPillStyle('none')} onClick={() => setForm({...form, information_sources_ids: []})}>Deseleccionar todo</button>
                    </div>
                  )}
                </div>
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
                    {availableSources.map(s => (
                      <button type="button" key={s.id} className={form.information_sources_ids.includes(s.id) ? styles.tagSelected : styles.tagUnselected} onClick={() => handleToggleSource(s.id)}>{s.name}</button>
                    ))}
                  </div>
                )}
              </div>

              {/* CANALES */}
              <div className={styles.sectionContainer}>
                <div style={{ display: 'flex', flexDirection: 'column', gap: '10px', marginBottom: '15px' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <label style={{ margin: 0 }}>3. CANALES RSS ESPECÍFICOS</label>
                    {Object.keys(availableChannelsBySource).length > 0 && (
                      <div style={{ display: 'flex', gap: '8px' }}>
                        <button type="button" style={btnPillStyle('all')} onClick={() => setForm({...form, rss_channels_ids: allAvailableChannelIds})}>Seleccionar todo</button>
                        <button type="button" style={btnPillStyle('none')} onClick={() => setForm({...form, rss_channels_ids: []})}>Deseleccionar todo</button>
                      </div>
                    )}
                  </div>
                  <div className={styles.searchBox} style={{ width: '100%', maxWidth: '350px' }}>
                    <Search size={14} color="#888" />
                    <input type="text" placeholder="Buscar canal..." value={channelSearch} onChange={(e) => setChannelSearch(e.target.value)} disabled={form.information_sources_ids.length === 0} />
                  </div>
                </div>
                <div className={styles.channelsContainer}>
                  {form.information_sources_ids.length === 0 ? (
                    <div className={styles.emptyContainerBox} style={{ border: 'none', backgroundColor: 'transparent', padding: 0 }}>
                      <p className={styles.emptyStateText}>👆 Selecciona al menos una fuente para ver sus canales.</p>
                    </div>
                  ) : Object.keys(availableChannelsBySource).length === 0 ? (
                    <div className={styles.emptyContainerBox} style={{ border: 'none', backgroundColor: 'transparent', padding: 0 }}>
                      <p className={styles.emptyStateText}>No se encontraron canales con esos filtros.</p>
                    </div>
                  ) : (
                    Object.entries(availableChannelsBySource).map(([srcName, channels]) => (
                      <div key={srcName} className={styles.sourceCard}>
                        <h4 className={styles.sourceCardTitle}>{srcName}</h4>
                        <div className={styles.channelList}>
                          {channels.map(ch => (
                            <label key={ch.id} className={styles.customCheckboxContainer}>
                              <input type="checkbox" checked={form.rss_channels_ids.includes(ch.id)} onChange={() => handleToggleChannel(ch.id)} className={styles.hiddenCheckbox} />
                              <span className={styles.checkmark}></span> {ch.name} <span className={styles.channelCategoryBadge}>{ch.category}</span>
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
              <button className={styles.cancelBtn} onClick={handleCloseAttempt}><Ban size={18} /> CANCELAR</button>
              <button className={styles.saveBtn} onClick={handleSave}><Save size={18} /> GUARDAR</button>
            </div>
          </div>
        </div>
      )}

      {showConfirmClose && (
        <div className={styles.miniOverlay}>
          <div className={styles.confirmBox}>
            <AlertCircle size={40} color="#FFBB28" /><p>¿Cerrar sin guardar cambios?</p>
            <div className={styles.confirmActions}>
              <button className={styles.confirmBoxBtnDanger} onClick={() => {setShowConfirmClose(false); setIsModalOpen(false);}}>Descartar</button>
              <button className={styles.confirmBoxBtnSafe} onClick={() => setShowConfirmClose(false)}>Seguir</button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default Alerts;