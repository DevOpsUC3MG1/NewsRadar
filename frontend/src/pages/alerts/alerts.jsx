import React, { useState, useEffect } from 'react';
import {
  Pencil, Trash2, Plus, Info, X,
  AlertCircle, Save, Ban, GripVertical
} from 'lucide-react';
import { DragDropContext, Droppable, Draggable } from '@hello-pangea/dnd';
import styles from './alerts.module.css';

const CATEGORIAS_DISPONIBLES = [
  "Política", "Economía", "Salud", "Tecnología",
  "Seguridad", "Terrorismo", "Internacional", "Deportes"
];

const Alerts = () => {
  const [alerts, setAlerts] = useState([
    { id: '1', nombre: "Atentado en Madrid", keyword: "Atentado", descriptores: ["bomba", "policía"], categorias: ["Seguridad"], periodicidad: "0 0 * * *" },
  ]);

  const [isModalOpen, setIsModalOpen] = useState(false);
  const [editingAlert, setEditingAlert] = useState(null);
  const [showConfirmClose, setShowConfirmClose] = useState(false);
  const [showConfirmDelete, setShowConfirmDelete] = useState(null);
  const [errorMsg, setErrorMsg] = useState("");

  const [form, setForm] = useState({
    nombre: '',
    keyword: '',
    periodicidad: '',
    descriptores: [],
    categorias: []
  });

  const [suggestedDescriptors, setSuggestedDescriptors] = useState([]);

  // Validación de expresión cron
  const isValidCron = (cron) => {
    const cronRegex = /^(\*|([0-5]?\d)(-[0-5]?\d)?(,[0-5]?\d)*)(\s+(\*|([0-5]?\d)(-[0-5]?\d)?(,[0-5]?\d)*)){4}$/;
    return cronRegex.test(cron.trim());
  };

  const handleSave = () => {
    if (!form.nombre || !form.keyword || !form.periodicidad || form.categorias.length === 0 || form.descriptores.length === 0) {
      setErrorMsg("Todos los campos son obligatorios (incluyendo al menos una categoría y un descriptor).");
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

  // FUNCIÓN RECUPERADA PARA CONFIRMAR CIERRE
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

  useEffect(() => {
    if (form.keyword.length > 2) {
      setSuggestedDescriptors(["urgente", "oficial", "noticia", "relevante", "impacto", "suceso"]);
    }
  }, [form.keyword]);

  return (
    <div className={styles.alertsWrapper}>
      <div className={styles.header}>
        <div className={styles.titleGroup}>
          <h1 className={styles.pageTitle}>ALERTAS</h1>
          <span className={styles.counter}>{alerts.length} activas</span>
        </div>
        <button className={styles.newAlertBtn} onClick={() => { setEditingAlert(null); setForm({nombre:'', keyword:'', periodicidad:'', descriptores:[], categorias:[]}); setErrorMsg(""); setIsModalOpen(true); }}>
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
                <th>DESCRIPTORES</th>
                <th>CATEGORÍAS</th>
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
                            <span className={styles.keyword}>{alert.keyword}</span>,{" "}
                            <span className={styles.descriptorsList}>{alert.descriptores.join(", ")}</span>
                          </td>
                          <td className={styles.categoryCell}>{alert.categorias.join(", ")}</td>
                          <td className={styles.cronText}>{alert.periodicidad}</td>
                          <td className={styles.actionsCell}>
                            <button className={styles.editBtn} onClick={() => {setEditingAlert(alert); setForm(alert); setErrorMsg(""); setIsModalOpen(true);}}><Pencil size={18} /></button>
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
              {/* USAMOS handleCloseAttempt AQUI */}
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
                    <button
                      key={i}
                      className={form.descriptores.includes(desc) ? styles.tagSelected : styles.tagUnselected}
                      onClick={() => handleToggleDescriptor(desc)}
                    >
                      {desc}
                    </button>
                  ))}
                </div>
              </div>

              <div className={styles.sectionContainer}>
                <label>CATEGORÍAS</label>
                <div className={styles.checkboxGrid}>
                  {CATEGORIAS_DISPONIBLES.map((cat) => (
                    <label key={cat} className={styles.customCheckboxContainer}>
                      <input
                        type="checkbox"
                        checked={form.categorias.includes(cat)}
                        onChange={() => handleToggleCategory(cat)}
                        className={styles.hiddenCheckbox}
                      />
                      <span className={styles.checkmark}></span>
                      {cat}
                    </label>
                  ))}
                </div>
              </div>
            </div>

            <div className={styles.modalFooter}>
              {/* USAMOS handleCloseAttempt AQUI TAMBIEN */}
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

      {/* --- DIÁLOGOS DE CONFIRMACIÓN (RECUPERADOS) --- */}

      {/* Confirmar Cierre */}
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

      {/* Confirmar Borrado */}
      {showConfirmDelete && (
        <div className={styles.miniOverlay}>
          <div className={styles.confirmBox}>
            <Trash2 size={40} color="#E02020" />
            <p>¿Estás seguro de eliminar esta alerta permanentemente?</p>
            <div className={styles.confirmActions}>
              <button className={styles.confirmBoxBtnSafe} onClick={() => setShowConfirmDelete(null)}>No, mantener</button>
              <button className={styles.confirmBoxBtnDanger} onClick={() => {
                setAlerts(alerts.filter(a => a.id !== showConfirmDelete));
                setShowConfirmDelete(null);
              }}>Confirmar</button>
            </div>
          </div>
        </div>
      )}

    </div>
  );
};

export default Alerts;