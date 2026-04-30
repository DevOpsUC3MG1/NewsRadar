// frontend/src/pages/alerts/alerts.jsx
import React, { useState, useEffect, useMemo, useContext } from 'react';
import { useTranslation } from 'react-i18next';
import {
  Pencil, Trash2, Plus, Info, X,
  AlertCircle, Save, Ban, GripVertical, Search, Sparkles, Loader2
} from 'lucide-react';
import { DragDropContext, Droppable, Draggable } from '@hello-pangea/dnd';
import axios from 'axios';
import { AuthContext } from '../../context/AuthContext';
import authService from '../../services/authService';
import styles from './alerts.module.css';

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const Alerts = () => {
  const { t } = useTranslation();
  const { user, fuentes, canales, categorias } = useContext(AuthContext);

  const [alerts, setAlerts] = useState([]);
  const [loadingAlerts, setLoadingAlerts] = useState(true);

  const [isModalOpen, setIsModalOpen] = useState(false);
  const [editingAlert, setEditingAlert] = useState(null);
  const [showConfirmClose, setShowConfirmClose] = useState(false);
  const [showConfirmDelete, setShowConfirmDelete] = useState(null);
  const [errorMsg, setErrorMsg] = useState("");
  const [channelSearch, setChannelSearch] = useState("");

  const [isGeneratingIA, setIsGeneratingIA] = useState(false);
  const [suggestedDescriptors, setSuggestedDescriptors] = useState([]);

  const [form, setForm] = useState({
    nombre: '', keyword: '', periodicidad: '',
    descriptores: [], categorias: [],
    information_sources_ids: [], rss_channels_ids: []
  });

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

  const fetchAlerts = async () => {
    if (!user?.id) return;
    setLoadingAlerts(true);
    try {
      const token = authService.getToken();
      const res = await axios.get(`${API_BASE}/api/v1/users/${user.id}/alerts`, {
        headers: { Authorization: `Bearer ${token}` }
      });

      const formattedAlerts = res.data.map(a => {
        const keyword = a.descriptors && a.descriptors.length > 0 ? a.descriptors[0] : "";
        const descriptoresRestantes = a.descriptors && a.descriptors.length > 1 ? a.descriptors.slice(1) : [];

        return {
          id: a.id,
          nombre: a.name,
          keyword: keyword,
          periodicidad: a.cron_expression,
          descriptores: descriptoresRestantes,
          categorias: (a.categories || []).map(c => c.label),
          information_sources_ids: (a.information_sources_ids || []).map(String),
          rss_channels_ids: (a.rss_channels_ids || []).map(String)
        };
      });
      setAlerts(formattedAlerts);
    } catch (err) {
      console.error(t('alerts.errors.fetch'), err);
    } finally {
      setLoadingAlerts(false);
    }
  };

  useEffect(() => {
    fetchAlerts();
  }, [user]);

  const isValidCron = (cron) => {
    const cronRegex = /^(\*|([0-5]?\d)(-[0-5]?\d)?(,[0-5]?\d)*)(\s+(\*|([0-5]?\d)(-[0-5]?\d)?(,[0-5]?\d)*)){4}$/;
    return cronRegex.test(cron.trim());
  };

  const handleSave = async () => {
    if (!form.nombre || !form.keyword.trim() || !form.periodicidad || form.categorias.length === 0) {
      setErrorMsg(t('alerts.errors.missingFields'));
      return;
    }
    if (!isValidCron(form.periodicidad)) {
      setErrorMsg(t('alerts.errors.invalidCron'));
      return;
    }

    setErrorMsg("");
    const token = authService.getToken();

    const finalDescriptors = [...new Set([form.keyword.trim(), ...form.descriptores])].filter(Boolean);

    const finalCategories = form.categorias.map(cat => ({
      code: cat.normalize("NFD").replace(/[\u0300-\u036f]/g, "").toLowerCase().replace(/\s+/g, '_'),
      label: cat
    }));

    const payload = {
      name: form.nombre,
      descriptors: finalDescriptors,
      categories: finalCategories,
      information_sources_ids: form.information_sources_ids.map(String),
      rss_channels_ids: form.rss_channels_ids.map(String),
      cron_expression: form.periodicidad
    };

    try {
      if (editingAlert) {
        await axios.put(`${API_BASE}/api/v1/users/${user.id}/alerts/${editingAlert.id}`, payload, {
          headers: { Authorization: `Bearer ${token}` }
        });
      } else {
        await axios.post(`${API_BASE}/api/v1/users/${user.id}/alerts`, payload, {
          headers: { Authorization: `Bearer ${token}` }
        });
      }
      setIsModalOpen(false);
      fetchAlerts();
    } catch (err) {
      console.error(t('alerts.errors.save'), err);
      if (err.response?.status === 422) {
        console.error("Fallo de validación detallado:", err.response.data);
      }
      setErrorMsg(t('alerts.errors.serverSave'));
    }
  };

  const handleDelete = async () => {
    try {
      const token = authService.getToken();
      await axios.delete(`${API_BASE}/api/v1/users/${user.id}/alerts/${showConfirmDelete}`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setShowConfirmDelete(null);
      fetchAlerts();
    } catch (err) {
      console.error(t('alerts.errors.delete'), err);
      alert(t('alerts.errors.cantDelete'));
    }
  };

  const handleGenerateIA = async () => {
    if (!form.keyword.trim()) {
      setErrorMsg(t('alerts.errors.missingKeywordIA'));
      return;
    }

    setIsGeneratingIA(true);
    setErrorMsg("");

    try {
      const token = authService.getToken();
      const res = await axios.post(`${API_BASE}/api/v1/alerts/suggest-synonyms`,
        { keywords: [form.keyword] },
        { headers: { Authorization: `Bearer ${token}` } }
      );

      const newSynonyms = res.data.suggested_synonyms || [];
      if (newSynonyms.length === 0) {
        setErrorMsg(t('alerts.errors.noIAData'));
      } else {
        setSuggestedDescriptors(newSynonyms);
      }
    } catch (err) {
      console.error(t('alerts.errors.iaCall'), err);
      setErrorMsg(t('alerts.errors.iaConfig'));
    } finally {
      setIsGeneratingIA(false);
    }
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

  const handleToggleCategory = (cat) => {
    setForm(prev => ({
      ...prev,
      categorias: prev.categorias.includes(cat)
        ? prev.categorias.filter(c => c !== cat)
        : [...prev.categorias, cat]
    }));
  };

  const handleToggleSource = (id) => {
    const strId = String(id);
    setForm(prev => ({
      ...prev,
      information_sources_ids: prev.information_sources_ids.includes(strId)
        ? prev.information_sources_ids.filter(s => s !== strId)
        : [...prev.information_sources_ids, strId]
    }));
  };

  const handleToggleChannel = (id) => {
    const strId = String(id);
    setForm(prev => ({
      ...prev,
      rss_channels_ids: prev.rss_channels_ids.includes(strId)
        ? prev.rss_channels_ids.filter(c => c !== strId)
        : [...prev.rss_channels_ids, strId]
    }));
  };

  const availableSources = useMemo(() => {
    return safeFuentes.filter(src => src.categorias.some(cat => form.categorias.includes(cat)));
  }, [safeFuentes, form.categorias]);

  const availableChannelsBySource = useMemo(() => {
    const grouped = {};
    safeFuentes.filter(src => form.information_sources_ids.includes(String(src.id))).forEach(source => {
      const validChannels = safeCanales.filter(ch =>
        ch.fuenteId === source.id &&
        form.categorias.includes(ch.categoria) &&
        ch.nombre.toLowerCase().includes(channelSearch.toLowerCase())
      );
      if (validChannels.length > 0) grouped[source.nombre] = validChannels;
    });
    return grouped;
  }, [safeFuentes, safeCanales, form.categorias, form.information_sources_ids, channelSearch]);

  const allAvailableChannelIds = useMemo(() => Object.values(availableChannelsBySource).flat().map(ch => String(ch.id)), [availableChannelsBySource]);

  const getSourceNames = (ids) => ids.map(id => safeFuentes.find(s => String(s.id) === String(id))?.nombre || id).join(", ");
  const getChannelNames = (ids) => ids.map(id => safeCanales.find(c => String(c.id) === String(id))?.nombre || id).join(", ");

  const btnPillStyle = (type) => ({
    background: type === 'all' ? '#EEF2FF' : '#F7FAFC',
    border: `1px solid ${type === 'all' ? '#D0D7F6' : '#E2E8F0'}`,
    color: type === 'all' ? '#4B6A9B' : '#718096',
    fontSize: '0.75rem', fontWeight: '600', cursor: 'pointer',
    padding: '4px 12px', borderRadius: '20px', transition: 'all 0.2s ease',
  });

  if (loadingAlerts) {
    return <div className={styles.alertsWrapper}><p style={{padding:'20px'}}>{t('alerts.loading')}</p></div>;
  }

  return (
    <div className={styles.alertsWrapper}>
      <div className={styles.header}>
        <div className={styles.titleGroup}>
          <h1 className={styles.pageTitle}>{t('alerts.title')}</h1>
          <span className={styles.counter}>{alerts.length} {t('alerts.active')}</span>
        </div>
        <button className={styles.newAlertBtn} onClick={() => {
          setEditingAlert(null);
          setForm({nombre:'', keyword:'', periodicidad:'', descriptores:[], categorias:[], information_sources_ids:[], rss_channels_ids:[]});
          setSuggestedDescriptors([]);
          setErrorMsg("");
          setIsModalOpen(true);
        }}>
          <Plus size={18} /> {t('alerts.newAlert')}
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
                <th style={{ width: '20%' }}>{t('alerts.table.name')}</th>
                <th>{t('alerts.table.filters')}</th>
                <th style={{ width: '15%' }}>{t('alerts.table.periodicity')}</th>
                <th className={styles.actionsHeader} style={{ width: '10%' }}>{t('alerts.table.actions')}</th>
              </tr>
            </thead>
            <Droppable droppableId="alerts-list">
              {(provided) => (
                <tbody {...provided.droppableProps} ref={provided.innerRef}>
                  {alerts.map((alert, index) => (
                    <Draggable key={alert.id} draggableId={String(alert.id)} index={index}>
                      {(provided) => (
                        <tr ref={provided.innerRef} {...provided.draggableProps}>
                          <td {...provided.dragHandleProps} className={styles.dragCell}><GripVertical size={18} color="#ccc" /></td>
                          <td className={styles.alertName}>{alert.nombre}</td>
                          <td style={{ padding: '12px 16px' }}>
                            <div style={{ fontSize: '0.85rem', color: '#555', lineHeight: '1.6' }}>
                              <div><strong>{t('alerts.table.keyword')}:</strong> <span style={{ fontWeight: '600', color: '#0E0E1D' }}>{alert.keyword}</span></div>
                              {alert.descriptores?.length > 0 && <div><strong>{t('alerts.table.descriptors')}:</strong> {alert.descriptores.join(", ")}</div>}

                              {/* RENDERIZADO DE CATEGORÍAS TRADUCIDAS EN TABLA */}
                              {alert.categorias?.length > 0 && (
                                <div>
                                  <strong>{t('alerts.table.categories')}:</strong> {alert.categorias.map(c => t(`categorias.${c}`, { defaultValue: c })).join(", ")}
                                </div>
                              )}

                              {alert.information_sources_ids?.length > 0 && <div><strong>{t('alerts.table.sources')}:</strong> {getSourceNames(alert.information_sources_ids)}</div>}
                              {alert.rss_channels_ids?.length > 0 && <div><strong>{t('alerts.table.channels')}:</strong> {getChannelNames(alert.rss_channels_ids)}</div>}
                            </div>
                          </td>
                          <td className={styles.cronText}>{alert.periodicidad}</td>
                          <td className={styles.actionsCell}>
                            <button className={styles.editBtn} onClick={() => {
                              setEditingAlert(alert);
                              setForm(alert);
                              setSuggestedDescriptors([]);
                              setIsModalOpen(true);
                            }}><Pencil size={18} /></button>
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
              <h2>{editingAlert ? t('alerts.modal.editTitle') : t('alerts.modal.createTitle')}</h2>
              <button onClick={handleCloseAttempt} className={styles.closeIcon}><X /></button>
            </div>

            <div className={styles.formBody}>
              {errorMsg && <div className={styles.errorBanner}>{errorMsg}</div>}

              <div className={styles.inputGroupFull}>
                <label>{t('alerts.form.nameLabel')}</label>
                <input type="text" value={form.nombre} onChange={(e) => setForm({...form, nombre: e.target.value})} placeholder={t('alerts.form.namePlaceholder')} />
              </div>

              <div className={styles.row}>
                <div className={styles.inputGroup}>
                  <label>{t('alerts.form.keywordLabel')}</label>
                  <div style={{ display: 'flex', gap: '8px' }}>
                    <input
                      type="text"
                      value={form.keyword}
                      onChange={(e) => setForm({...form, keyword: e.target.value})}
                      placeholder={t('alerts.form.keywordPlaceholder')}
                      style={{ flex: 1 }}
                    />
                    <button
                      type="button"
                      onClick={handleGenerateIA}
                      disabled={isGeneratingIA || !form.keyword.trim()}
                      style={{
                        backgroundColor: '#6A00FF', color: 'white', border: 'none', borderRadius: '8px',
                        padding: '0 12px', cursor: (isGeneratingIA || !form.keyword.trim()) ? 'not-allowed' : 'pointer',
                        display: 'flex', alignItems: 'center', gap: '6px', fontSize: '0.8rem', fontWeight: 'bold',
                        opacity: (isGeneratingIA || !form.keyword.trim()) ? 0.6 : 1
                      }}
                    >
                      {isGeneratingIA ? <Loader2 size={16} className={styles.spinner} /> : <Sparkles size={16} />}
                      {t('alerts.form.iaBtn')}
                    </button>
                  </div>
                </div>

                <div className={styles.inputGroup}>
                  <label className={styles.labelWithInfo}>
                    {t('alerts.form.cronLabel')}
                    <div className={styles.infoWrapper}>
                      <Info size={14} />
                      <div className={styles.tooltip} style={{
                        width: 'max-content', maxWidth: '350px', padding: '12px', textAlign: 'left',
                        lineHeight: '1.5', fontSize: '0.8rem', fontWeight: 'normal', zIndex: 100,
                        top: '100%', bottom: 'auto', marginTop: '10px', left: '0', transform: 'none'
                      }}>
                        <strong style={{ display: 'block', marginBottom: '8px', fontSize: '0.85rem' }}>{t('alerts.tooltip.title')}</strong>
                        <div style={{ display: 'grid', gridTemplateColumns: '50px 1fr', gap: '4px', marginBottom: '8px' }}>
                          <strong>{t('alerts.tooltip.min')}:</strong> <span>0-59</span>
                          <strong>{t('alerts.tooltip.hour')}:</strong> <span>0-23</span>
                          <strong>{t('alerts.tooltip.day')}:</strong> <span>1-31</span>
                          <strong>{t('alerts.tooltip.month')}:</strong> <span>1-12</span>
                          <strong>{t('alerts.tooltip.week')}:</strong> <span>0-6 (0={t('alerts.tooltip.sun')})</span>
                        </div>
                        <div style={{ borderTop: '1px solid rgba(255,255,255,0.2)', paddingTop: '8px', marginBottom: '8px' }}>
                          <strong style={{ display: 'block', marginBottom: '4px' }}>{t('alerts.tooltip.special')}:</strong>
                          <div style={{ display: 'grid', gridTemplateColumns: '20px 1fr', gap: '4px' }}>
                            <strong style={{textAlign: 'center'}}>*</strong> <span>{t('alerts.tooltip.any')}</span>
                            <strong style={{textAlign: 'center'}}>,</strong> <span>{t('alerts.tooltip.list')} (ej. 1,15)</span>
                            <strong style={{textAlign: 'center'}}>-</strong> <span>{t('alerts.tooltip.range')} (ej. 1-5)</span>
                            <strong style={{textAlign: 'center'}}>/</strong> <span>{t('alerts.tooltip.interval')} (ej. */15)</span>
                          </div>
                        </div>
                        <div style={{ borderTop: '1px solid rgba(255,255,255,0.2)', paddingTop: '8px' }}>
                          <strong>{t('alerts.tooltip.structure')}:</strong><br/>
                          <code style={{ background: 'rgba(0,0,0,0.2)', padding: '2px 4px', borderRadius: '4px', display: 'inline-block', marginBottom: '8px' }}>min hora día mes sem</code><br/>
                          <strong>{t('alerts.tooltip.examples')}:</strong><br/>
                          <code style={{ background: 'rgba(0,0,0,0.2)', padding: '2px 4px', borderRadius: '4px' }}>* * * * *</code> {t('alerts.tooltip.exMin')}<br/>
                          <code style={{ background: 'rgba(0,0,0,0.2)', padding: '2px 4px', borderRadius: '4px' }}>0 9 * * 1-5</code> {t('alerts.tooltip.exWork')}
                        </div>
                      </div>
                    </div>
                  </label>
                  <input type="text" value={form.periodicidad} onChange={(e) => setForm({...form, periodicidad: e.target.value})} placeholder="* * * * *" />
                </div>
              </div>

              <div className={styles.sectionContainer}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-end', marginBottom: '10px' }}>
                  <label style={{ margin: 0 }}>{t('alerts.form.descriptorsLabel')}</label>
                  {suggestedDescriptors.length > 0 && (
                    <span style={{ fontSize: '0.75rem', color: '#6A00FF', fontWeight: 'bold' }}>{t('alerts.form.iaSuccess')}</span>
                  )}
                </div>
                <div className={styles.tagsContainer}>
                  {form.descriptores.filter(d => !suggestedDescriptors.includes(d)).map((desc, i) => (
                    <button type="button" key={`sel-${i}`} className={styles.tagSelected} onClick={() => handleToggleDescriptor(desc)}>
                      {desc}
                    </button>
                  ))}

                  {suggestedDescriptors.map((desc, i) => (
                    <button type="button" key={`sug-${i}`} className={form.descriptores.includes(desc) ? styles.tagSelected : styles.tagUnselected} onClick={() => handleToggleDescriptor(desc)}>
                      {desc}
                    </button>
                  ))}

                  {suggestedDescriptors.length === 0 && form.descriptores.length === 0 && (
                    <p className={styles.emptyStateText} style={{ margin: 0, fontStyle: 'italic', fontSize: '0.85rem' }}>{t('alerts.form.iaHint')}</p>
                  )}
                </div>
              </div>

              <div className={styles.sectionContainer}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '10px' }}>
                  <label style={{ margin: 0 }}>{t('alerts.form.catLabel')}</label>
                  <div style={{ display: 'flex', gap: '8px' }}>
                    <button type="button" style={btnPillStyle('all')} onClick={() => setForm({...form, categorias: safeCategorias})}>{t('alerts.form.selectAll')}</button>
                    <button type="button" style={btnPillStyle('none')} onClick={() => setForm({...form, categorias: []})}>{t('alerts.form.unselectAll')}</button>
                  </div>
                </div>
                <div className={styles.checkboxGrid}>
                  {safeCategorias.map(cat => (
                    <label key={cat} className={styles.customCheckboxContainer}>
                      <input type="checkbox" checked={form.categorias.includes(cat)} onChange={() => handleToggleCategory(cat)} className={styles.hiddenCheckbox} />

                      {/* RENDERIZADO DE CATEGORÍAS TRADUCIDAS EN CHECKBOXES */}
                      <span className={styles.checkmark}></span> {t(`categorias.${cat}`, { defaultValue: cat })}
                    </label>
                  ))}
                </div>
              </div>

              <div className={styles.sectionContainer}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '10px' }}>
                  <label style={{ margin: 0 }}>{t('alerts.form.srcLabel')}</label>
                  {form.categorias.length > 0 && availableSources.length > 0 && (
                    <div style={{ display: 'flex', gap: '8px' }}>
                      <button type="button" style={btnPillStyle('all')} onClick={() => setForm({...form, information_sources_ids: availableSources.map(s => String(s.id))})}>{t('alerts.form.selectAll')}</button>
                      <button type="button" style={btnPillStyle('none')} onClick={() => setForm({...form, information_sources_ids: []})}>{t('alerts.form.unselectAll')}</button>
                    </div>
                  )}
                </div>
                {form.categorias.length === 0 ? (
                  <div className={styles.emptyContainerBox}>
                    <p className={styles.emptyStateText}>{t('alerts.form.srcHintCat')}</p>
                  </div>
                ) : availableSources.length === 0 ? (
                  <div className={styles.emptyContainerBox}>
                    <p className={styles.emptyStateText}>{t('alerts.form.srcHintEmpty')}</p>
                  </div>
                ) : (
                  <div className={styles.tagsContainer}>
                    {availableSources.map(s => (
                      <button type="button" key={s.id} className={form.information_sources_ids.includes(String(s.id)) ? styles.tagSelected : styles.tagUnselected} onClick={() => handleToggleSource(s.id)}>{s.nombre}</button>
                    ))}
                  </div>
                )}
              </div>

              <div className={styles.sectionContainer}>
                <div style={{ display: 'flex', flexDirection: 'column', gap: '10px', marginBottom: '15px' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <label style={{ margin: 0 }}>{t('alerts.form.chanLabel')}</label>
                    {Object.keys(availableChannelsBySource).length > 0 && (
                      <div style={{ display: 'flex', gap: '8px' }}>
                        <button type="button" style={btnPillStyle('all')} onClick={() => setForm({...form, rss_channels_ids: allAvailableChannelIds})}>{t('alerts.form.selectAll')}</button>
                        <button type="button" style={btnPillStyle('none')} onClick={() => setForm({...form, rss_channels_ids: []})}>{t('alerts.form.unselectAll')}</button>
                      </div>
                    )}
                  </div>
                  <div className={styles.searchBox} style={{ width: '100%', maxWidth: '350px' }}>
                    <Search size={14} color="#888" />
                    <input type="text" placeholder={t('alerts.form.searchChannel')} value={channelSearch} onChange={(e) => setChannelSearch(e.target.value)} disabled={form.information_sources_ids.length === 0} />
                  </div>
                </div>
                <div className={styles.channelsContainer}>
                  {form.information_sources_ids.length === 0 ? (
                    <div className={styles.emptyContainerBox} style={{ border: 'none', backgroundColor: 'transparent', padding: 0 }}>
                      <p className={styles.emptyStateText}>{t('alerts.form.chanHintSrc')}</p>
                    </div>
                  ) : Object.keys(availableChannelsBySource).length === 0 ? (
                    <div className={styles.emptyContainerBox} style={{ border: 'none', backgroundColor: 'transparent', padding: 0 }}>
                      <p className={styles.emptyStateText}>{t('alerts.form.chanHintEmpty')}</p>
                    </div>
                  ) : (
                    Object.entries(availableChannelsBySource).map(([srcName, channels]) => (
                      <div key={srcName} className={styles.sourceCard}>
                        <h4 className={styles.sourceCardTitle}>{srcName}</h4>
                        <div className={styles.channelList}>
                          {channels.map(ch => (
                            <label key={ch.id} className={styles.customCheckboxContainer}>
                              <input type="checkbox" checked={form.rss_channels_ids.includes(String(ch.id))} onChange={() => handleToggleChannel(ch.id)} className={styles.hiddenCheckbox} />

                              {/* RENDERIZADO DE CATEGORÍAS TRADUCIDAS EN LOS BADGES DE CANALES */}
                              <span className={styles.checkmark}></span> {ch.nombre} <span className={styles.channelCategoryBadge}>{t(`categorias.${ch.categoria}`, { defaultValue: ch.categoria })}</span>
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
              <button className={styles.cancelBtn} onClick={handleCloseAttempt}><Ban size={18} /> {t('alerts.modal.cancelBtn')}</button>
              <button className={styles.saveBtn} onClick={handleSave}><Save size={18} /> {t('alerts.modal.saveBtn')}</button>
            </div>
          </div>
        </div>
      )}

      {showConfirmClose && (
        <div className={styles.miniOverlay}>
          <div className={styles.confirmBox}>
            <AlertCircle size={40} color="#FFBB28" /><p>{t('alerts.modal.confirmCloseMsg')}</p>
            <div className={styles.confirmActions}>
              <button className={styles.confirmBoxBtnDanger} onClick={() => {setShowConfirmClose(false); setIsModalOpen(false);}}>{t('alerts.modal.discardBtn')}</button>
              <button className={styles.confirmBoxBtnSafe} onClick={() => setShowConfirmClose(false)}>{t('alerts.modal.continueBtn')}</button>
            </div>
          </div>
        </div>
      )}

      {showConfirmDelete && (
        <div className={styles.miniOverlay}>
          <div className={styles.confirmBox}>
            <Trash2 size={40} color="#E02020" />
            <p>{t('alerts.modal.confirmDeleteMsg')}</p>
            <div className={styles.confirmActions}>
              <button className={styles.confirmBoxBtnSafe} onClick={() => setShowConfirmDelete(null)}>{t('alerts.modal.keepBtn')}</button>
              <button className={styles.confirmBoxBtnDanger} onClick={handleDelete}>{t('alerts.modal.deleteBtn')}</button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default Alerts;