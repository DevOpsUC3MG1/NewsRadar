// frontend/src/pages/notificaciones/notificaciones.jsx
import React, { useState, useEffect, useContext, useCallback } from 'react';
import {
  MailOpen, ChevronUp, ChevronDown, Minus,
  Trash2, MailCheck, Mail, ExternalLink, RefreshCw, BellRing, Loader2,
} from 'lucide-react';
import styles from './notificaciones.module.css';
import { AuthContext } from '../../context/AuthContext';
import authService from '../../services/authService';
import { getAllNotificationsForUser } from '../../services/newsService';

// ─── Helpers de fecha ─────────────────────────────────────────────────────────
const formatDate = (raw) => {
  if (!raw) return '—';
  try {
    return new Date(raw).toLocaleString('es-ES', {
      day:    '2-digit',
      month:  '2-digit',
      year:   'numeric',
      hour:   '2-digit',
      minute: '2-digit',
    });
  } catch {
    return String(raw);
  }
};

// ─── LocalStorage helpers ─────────────────────────────────────────────────────
const LS_READ_KEY    = (uid) => `nr_notif_read_${uid}`;
const LS_DELETED_KEY = (uid) => `nr_notif_deleted_${uid}`;

const loadReadMap = (uid) => {
  try { return JSON.parse(localStorage.getItem(LS_READ_KEY(uid)) ?? '{}'); }
  catch { return {}; }
};

const saveReadMap = (uid, map) => {
  localStorage.setItem(LS_READ_KEY(uid), JSON.stringify(map));
};

const loadDeletedSet = (uid) => {
  try { return new Set(JSON.parse(localStorage.getItem(LS_DELETED_KEY(uid)) ?? '[]')); }
  catch { return new Set(); }
};

const saveDeletedSet = (uid, set) => {
  localStorage.setItem(LS_DELETED_KEY(uid), JSON.stringify([...set]));
};

// ─── Mapeo backend → UI ───────────────────────────────────────────────────────
const mapNotification = (raw, readMap, deletedSet) => {
  if (deletedSet.has(raw.id)) return null;

  const news = (raw.news ?? []).map((item, idx) => ({
    id:         `${raw.id}-${idx}`,
    rssChannel: item.source_name ?? '—',
    category:   item.category   ?? '—',
    title:      item.title      ?? '(Sin título)',
    subtitle:   '',
    date:       formatDate(item.published),
    url:        item.link       ?? '#',
  }));

  return {
    id:         raw.id,
    alertId:    raw.alertId,
    alertName:  raw.alertName,
    date:       formatDate(raw.timestamp),
    isRead:     readMap[raw.id] ?? false,
    isExpanded: false,
    news,
  };
};

// ─── Modal de confirmación ────────────────────────────────────────────────────
const ConfirmModal = ({ title, text, confirmLabel, onConfirm, onCancel }) => (
  <div className={styles.modalOverlay} onClick={onCancel}>
    <div className={styles.modalBox} onClick={e => e.stopPropagation()}>
      <h3 className={styles.modalTitle}>{title}</h3>
      <p className={styles.modalText}>{text}</p>
      <div className={styles.modalActions}>
        <button className={styles.modalCancel} onClick={onCancel}>Cancelar</button>
        <button className={styles.modalConfirm} onClick={onConfirm}>{confirmLabel}</button>
      </div>
    </div>
  </div>
);

// ─── Tarjeta de noticia individual ───────────────────────────────────────────
const NewsCard = ({ item }) => (
  <div className={styles.newsCard}>
    <div className={styles.newsCardBody}>
      <span className={styles.newsSource}>
        {item.rssChannel} - CATEGORÍA: {item.category}
      </span>
      <div className={styles.newsTitleRow}>
        <h4 className={styles.newsTitle}>{item.title}</h4>
        <span className={styles.newsDate}>{item.date}</span>
      </div>
      {item.subtitle && <p className={styles.newsSubtitle}>{item.subtitle}</p>}
    </div>
    <a
      href={item.url}
      target="_blank"
      rel="noopener noreferrer"
      className={styles.newsLink}
      title="Abrir noticia"
      onClick={e => e.stopPropagation()}
    >
      <ExternalLink size={15} />
    </a>
  </div>
);

// ─── Estado vacío ─────────────────────────────────────────────────────────────
const EmptyState = ({ onRefresh }) => (
  <div className={styles.emptyState}>
    <MailOpen size={52} strokeWidth={1.2} className={styles.emptyIcon} />
    <p>No hay notificaciones disponibles.</p>
    <button className={styles.actionButton} onClick={onRefresh}>
      <RefreshCw size={14} style={{ marginRight: 6 }} />
      Actualizar
    </button>
  </div>
);

// ─── Componente principal ─────────────────────────────────────────────────────
const Notifications = () => {
  const { user } = useContext(AuthContext);

  const [notifications, setNotifications]   = useState([]);
  const [loading, setLoading]               = useState(true);
  const [error, setError]                   = useState(false);
  const [activeId, setActiveId]             = useState(null);
  const [showClearModal, setShowClearModal] = useState(false);
  const [deleteTargetId, setDeleteTargetId] = useState(null);

  // ── Carga de datos desde el backend ────────────────────────────────────────
  const fetchNotifications = useCallback(async () => {
    if (!user?.id) return;
    setLoading(true);
    setError(false);
    try {
      const token      = authService.getToken();
      const readMap    = loadReadMap(user.id);
      const deletedSet = loadDeletedSet(user.id);

      const raw = await getAllNotificationsForUser(user.id, token);

      const mapped = raw
        .map(n => mapNotification(n, readMap, deletedSet))
        .filter(Boolean);

      setNotifications(mapped);
    } catch {
      setError(true);
    } finally {
      setLoading(false);
    }
  }, [user?.id]);

  useEffect(() => { fetchNotifications(); }, [fetchNotifications]);

  // ── Persistir cambios de lectura en localStorage ────────────────────────────
  const persistReadMap = useCallback((updatedNotifications) => {
    if (!user?.id) return;
    const map = {};
    updatedNotifications.forEach(n => { map[n.id] = n.isRead; });
    saveReadMap(user.id, map);
  }, [user?.id]);

  // ── Handlers ────────────────────────────────────────────────────────────────
  const handlePageClick = () => {
    if (activeId !== null) {
      setNotifications(prev => prev.map(n =>
        n.id === activeId ? { ...n, isExpanded: false } : n
      ));
    }
    setActiveId(null);
  };

  const handleCardClick = (id, hasNews) => {
    setActiveId(id);
    setNotifications(prev => {
      const next = prev.map(n => {
        if (n.id !== id) return n;
        return {
          ...n,
          isRead:     true,
          isExpanded: hasNews && !n.isExpanded ? true : n.isExpanded,
        };
      });
      persistReadMap(next);
      return next;
    });
  };

  const handleToggleExpand = (e, id) => {
    e.stopPropagation();
    setNotifications(prev => {
      const next = prev.map(n => {
        if (n.id === activeId && n.id !== id) return { ...n, isExpanded: false };
        if (n.id === id) return { ...n, isExpanded: !n.isExpanded, isRead: true };
        return n;
      });
      persistReadMap(next);
      return next;
    });
    setActiveId(id);
  };

  const handleToggleRead = (e, id) => {
    e.stopPropagation();
    setNotifications(prev => {
      const next = prev.map(n => n.id === id ? { ...n, isRead: !n.isRead } : n);
      persistReadMap(next);
      return next;
    });
  };

  const handleOpenDeleteModal = (e, id) => {
    e.stopPropagation();
    setDeleteTargetId(id);
  };

  const handleConfirmDelete = () => {
    if (!user?.id) return;
    const deletedSet = loadDeletedSet(user.id);
    deletedSet.add(deleteTargetId);
    saveDeletedSet(user.id, deletedSet);

    setNotifications(prev => prev.filter(n => n.id !== deleteTargetId));
    if (activeId === deleteTargetId) setActiveId(null);
    setDeleteTargetId(null);
  };

  const markAllAsRead = () => {
    setNotifications(prev => {
      const next = prev.map(n => ({ ...n, isRead: true }));
      persistReadMap(next);
      return next;
    });
  };

  const handleClearAll = () => {
    if (!user?.id) return;
    const deletedSet = loadDeletedSet(user.id);
    notifications.forEach(n => deletedSet.add(n.id));
    saveDeletedSet(user.id, deletedSet);

    setNotifications([]);
    setActiveId(null);
    setShowClearModal(false);
  };

  // ── Helpers ─────────────────────────────────────────────────────────────────
  const userName = user?.first_name ?? 'Usuario';

  const getAlertMessage = (count) => {
    if (count === 0) return `¡Hola ${userName}! Tu alerta no tiene noticias desde la última revisión.`;
    if (count === 1) return `¡Hola ${userName}! Tu alerta tiene 1 noticia nueva desde la última revisión.`;
    return `¡Hola ${userName}! Tu alerta tiene ${count} noticias nuevas desde la última revisión.`;
  };

  const unreadCount = notifications.filter(n => !n.isRead).length;

  // ── Loading ─────────────────────────────────────────────────────────────────
  if (loading) {
    return (
      <div className={styles.pageWrapper}>
        <div className={styles.loadingOverlay}>
          <Loader2 className={styles.spinner} size={48} />
          <p>Cargando notificaciones…</p>
        </div>
      </div>
    );
  }

  // ── Error ───────────────────────────────────────────────────────────────────
  if (error) {
    return (
      <div className={styles.pageWrapper}>
        <div className={styles.errorContainer}>
          <h2>Error al cargar notificaciones</h2>
          <button className={styles.actionButton} onClick={fetchNotifications}>
            Reintentar
          </button>
        </div>
      </div>
    );
  }

  // ── Render ──────────────────────────────────────────────────────────────────
  return (
    <div className={styles.pageWrapper} onClick={handlePageClick}>

      {showClearModal && (
        <ConfirmModal
          title="Limpiar buzón"
          text="¿Estás seguro de que quieres eliminar todas las notificaciones? Esta acción no se puede deshacer."
          confirmLabel="Eliminar todo"
          onConfirm={handleClearAll}
          onCancel={() => setShowClearModal(false)}
        />
      )}

      {deleteTargetId !== null && (
        <ConfirmModal
          title="Eliminar notificación"
          text="¿Estás seguro de que quieres eliminar esta notificación? No podrás recuperarla después."
          confirmLabel="Eliminar"
          onConfirm={handleConfirmDelete}
          onCancel={() => setDeleteTargetId(null)}
        />
      )}

      <div className={styles.centerContainer}>

        {/* ── CABECERA ── */}
        <div className={styles.header}>
          <h1 className={styles.title}>NOTIFICACIONES</h1>
          <div className={styles.headerActions}>
            {unreadCount > 0 && (
              <button
                className={styles.textButton}
                onClick={e => { e.stopPropagation(); markAllAsRead(); }}
              >
                Marcar todas como leídas
              </button>
            )}
            {notifications.length > 0 && (
              <button
                className={styles.clearButton}
                onClick={e => { e.stopPropagation(); setShowClearModal(true); }}
              >
                Limpiar buzón
              </button>
            )}
          </div>
        </div>

        {/* ── LISTA ── */}
        <div className={styles.listContainer}>
          {notifications.length === 0 ? (
            <EmptyState onRefresh={fetchNotifications} />
          ) : (
            notifications.map(notif => {
              const hasNews  = notif.news.length > 0;
              const isActive = activeId === notif.id;
              const isDimmed = notif.isRead && !isActive;

              return (
                <div
                  key={notif.id}
                  className={[
                    styles.alertCard,
                    notif.isRead ? styles.alertRead : styles.alertUnread,
                    isDimmed  ? styles.alertDimmed : '',
                    isActive  ? styles.alertActive : '',
                  ].join(' ')}
                  onClick={e => { e.stopPropagation(); handleCardClick(notif.id, hasNews); }}
                >
                  <div className={styles.alertHeader}>
                    <div className={styles.alertTitleGroup}>
                      <h2 className={styles.alertTitle}>
                        <BellRing size={13} className={styles.alertTitleIcon} />
                        ACTUALIZACIÓN DE ALERTA:&nbsp;
                        <span className={styles.alertTitleQuoted}>"{notif.alertName}"</span>
                      </h2>
                      <span className={styles.alertDate}>{notif.date}</span>
                    </div>

                    <div className={styles.alertActions} onClick={e => e.stopPropagation()}>
                      <button
                        className={styles.iconBtn}
                        onClick={e => handleToggleRead(e, notif.id)}
                        title={notif.isRead ? 'Marcar como no leída' : 'Marcar como leída'}
                      >
                        {notif.isRead ? <Mail size={16} /> : <MailCheck size={16} />}
                      </button>

                      <button
                        className={`${styles.iconBtn} ${styles.iconBtnDelete}`}
                        onClick={e => handleOpenDeleteModal(e, notif.id)}
                        title="Eliminar notificación"
                      >
                        <Trash2 size={16} />
                      </button>

                      {hasNews ? (
                        <button
                          className={styles.iconBtn}
                          onClick={e => handleToggleExpand(e, notif.id)}
                          title={notif.isExpanded ? 'Contraer' : 'Expandir'}
                        >
                          {notif.isExpanded ? <ChevronUp size={16} /> : <ChevronDown size={16} />}
                        </button>
                      ) : (
                        <span className={styles.iconBtnDisabled} title="Sin noticias nuevas">
                          <Minus size={16} />
                        </span>
                      )}
                    </div>
                  </div>

                  <p className={styles.alertMessage}>
                    {getAlertMessage(notif.news.length)}
                  </p>

                  {hasNews && (
                    <div className={[
                      styles.newsList,
                      notif.isExpanded ? styles.newsListExpanded : '',
                    ].join(' ')}>
                      {notif.news.map(item => (
                        <NewsCard key={item.id} item={item} />
                      ))}
                    </div>
                  )}
                </div>
              );
            })
          )}
        </div>
      </div>
    </div>
  );
};

export default Notifications;