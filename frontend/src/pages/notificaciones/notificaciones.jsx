// frontend/src/pages/notificaciones/notificaciones.jsx
import React, { useState, useEffect } from 'react';
import {
  MailOpen, ChevronUp, ChevronDown, Minus,
  Trash2, MailCheck, Mail, ExternalLink, RefreshCw, BellRing, Loader2,
} from 'lucide-react';
import styles from './notificaciones.module.css';

// ─── Usuario mock (sustituir por contexto/auth real) ─────────────────────────
const USERNAME = 'Usuario';

// ─── Datos mock ───────────────────────────────────────────────────────────────
const MOCK_DATA = [
  {
    id: 1,
    alertName: 'Tecnología e IA',
    date: '15/05/2025 09:30',
    isRead: false,
    isExpanded: false,
    news: [
      {
        id: 'n1',
        rssChannel: 'TechCrunch',
        category: 'Inteligencia Artificial',
        title: 'GPT-5 revoluciona el sector de la IA generativa',
        subtitle: 'OpenAI lanza su nuevo modelo con capacidades multimodales avanzadas que prometen transformar la industria tecnológica por completo.',
        date: '15/05/2025 08:15',
        url: 'https://techcrunch.com',
      },
      {
        id: 'n2',
        rssChannel: 'The Verge',
        category: 'Tecnología',
        title: 'Apple presenta sus nuevas gafas de realidad mixta Vision Pro 2',
        subtitle: 'La segunda generación llega con mejoras significativas en autonomía, resolución y un nuevo procesador M3 Ultra.',
        date: '15/05/2025 07:42',
        url: 'https://theverge.com',
      },
    ],
  },
  {
    id: 2,
    alertName: 'Economía Europea',
    date: '14/05/2025 18:00',
    isRead: false,
    isExpanded: false,
    news: [],
  },
  {
    id: 3,
    alertName: 'Política Internacional',
    date: '13/05/2025 12:15',
    isRead: true,
    isExpanded: false,
    news: [
      {
        id: 'n3',
        rssChannel: 'El País',
        category: 'Internacional',
        title: 'Cumbre del G7 alcanza acuerdo histórico sobre política climática',
        subtitle: 'Los líderes de las siete economías más importantes acuerdan nuevos objetivos de reducción de emisiones para 2030.',
        date: '13/05/2025 11:00',
        url: 'https://elpais.com',
      },
    ],
  },
];

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
      <p className={styles.newsSubtitle}>{item.subtitle}</p>
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

// ─── Skeleton ─────────────────────────────────────────────────────────────────
const SkeletonCard = () => (
  <div className={styles.skeletonCard}>
    <div className={styles.skeletonLine} style={{ width: '50%', height: 15, marginBottom: 12 }} />
    <div className={styles.skeletonLine} style={{ width: '78%', height: 12 }} />
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
  const [notifications, setNotifications]   = useState([]);
  const [loading, setLoading]               = useState(true);
  const [error, setError]                   = useState(false);
  const [activeId, setActiveId]             = useState(null);
  const [showClearModal, setShowClearModal] = useState(false);
  const [deleteTargetId, setDeleteTargetId] = useState(null);

  // ── Carga de datos ──────────────────────────────────────────────────────────
  const fetchNotifications = async () => {
    setLoading(true);
    setError(false);
    try {
      await new Promise(r => setTimeout(r, 1200));
      setNotifications(MOCK_DATA.map(n => ({ ...n, news: [...n.news] })));
    } catch {
      setError(true);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { fetchNotifications(); }, []);

  // ── Handlers ────────────────────────────────────────────────────────────────

  // Click en la página (fuera de cualquier tarjeta) → quita el foco activo
  // y repliega las noticias de la tarjeta que estaba abierta
  const handlePageClick = () => {
    if (activeId !== null) {
      setNotifications(prev => prev.map(n =>
        n.id === activeId ? { ...n, isExpanded: false } : n
      ));
    }
    setActiveId(null);
  };

  // Click en la tarjeta: marca como leída, activa el foco y togglea expand si tiene noticias
  const handleCardClick = (id, hasNews) => {
    setActiveId(id);
    setNotifications(prev => prev.map(n => {
      if (n.id !== id) return n;
      return {
        ...n,
        isRead: true,
        // El contenedor solo expande si estaba colapsado; nunca colapsa.
        // Así, hacer click dentro de las noticias solo reactiva el foco.
        isExpanded: hasNews && !n.isExpanded ? true : n.isExpanded,
      };
    }));
  };

  // Botón expandir/contraer
  const handleToggleExpand = (e, id) => {
    e.stopPropagation();
    setNotifications(prev => prev.map(n => {
      // Repliega la notificación que estaba activa (si es distinta a la que se pulsa)
      if (n.id === activeId && n.id !== id) return { ...n, isExpanded: false };
      // Togglea la que se pulsa
      if (n.id === id) return { ...n, isExpanded: !n.isExpanded, isRead: true };
      return n;
    }));
    setActiveId(id);
  };

  // Botón marcar leída / no leída
  const handleToggleRead = (e, id) => {
    e.stopPropagation();
    setNotifications(prev => prev.map(n =>
      n.id === id ? { ...n, isRead: !n.isRead } : n
    ));
  };

  // Botón eliminar
  const handleOpenDeleteModal = (e, id) => {
    e.stopPropagation();
    setDeleteTargetId(id);
  };

  const handleConfirmDelete = () => {
    setNotifications(prev => prev.filter(n => n.id !== deleteTargetId));
    if (activeId === deleteTargetId) setActiveId(null);
    setDeleteTargetId(null);
  };

  // Marcar todas como leídas
  const markAllAsRead = () =>
    setNotifications(prev => prev.map(n => ({ ...n, isRead: true })));

  // Limpiar buzón
  const handleClearAll = () => {
    setNotifications([]);
    setActiveId(null);
    setShowClearModal(false);
  };

  // ── Helpers ─────────────────────────────────────────────────────────────────
  const getAlertMessage = (count) => {
    if (count === 0) return `¡Hola ${USERNAME}! Tu alerta no tiene noticias desde la última revisión.`;
    if (count === 1) return `¡Hola ${USERNAME}! Tu alerta tiene 1 noticia nueva desde la última revisión.`;
    return `¡Hola ${USERNAME}! Tu alerta tiene ${count} noticias nuevas desde la última revisión.`;
  };

  const unreadCount = notifications.filter(n => !n.isRead).length;

  // ── Loading overlay (igual que dashboard) ──────────────────────────────────
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

      {/* Modal: limpiar buzón */}
      {showClearModal && (
        <ConfirmModal
          title="Limpiar buzón"
          text="¿Estás seguro de que quieres eliminar todas las notificaciones? Esta acción no se puede deshacer."
          confirmLabel="Eliminar todo"
          onConfirm={handleClearAll}
          onCancel={() => setShowClearModal(false)}
        />
      )}

      {/* Modal: eliminar notificación individual */}
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
          ) : (            notifications.map(notif => {
              const hasNews = notif.news.length > 0;
              const isActive = activeId === notif.id;
              // Una notificación leída que NO es la activa se muestra oscurecida
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
                  {/* ── Fila superior: título + fecha + botones ── */}
                  <div className={styles.alertHeader}>
                    <div className={styles.alertTitleGroup}>
                      <h2 className={styles.alertTitle}>
                        <BellRing size={13} className={styles.alertTitleIcon} />
                        ACTUALIZACIÓN DE ALERTA:&nbsp;
                        <span className={styles.alertTitleQuoted}>"{notif.alertName}"</span>
                      </h2>
                      <span className={styles.alertDate}>{notif.date}</span>
                    </div>

                    {/* Botones de acción — stopPropagation para no disparar el click de la tarjeta */}
                    <div className={styles.alertActions} onClick={e => e.stopPropagation()}>
                      {/* Marcar leída / no leída */}
                      <button
                        className={styles.iconBtn}
                        onClick={e => handleToggleRead(e, notif.id)}
                        title={notif.isRead ? 'Marcar como no leída' : 'Marcar como leída'}
                      >
                        {notif.isRead
                          ? <Mail size={16} />
                          : <MailCheck size={16} />
                        }
                      </button>

                      {/* Eliminar */}
                      <button
                        className={`${styles.iconBtn} ${styles.iconBtnDelete}`}
                        onClick={e => handleOpenDeleteModal(e, notif.id)}
                        title="Eliminar notificación"
                      >
                        <Trash2 size={16} />
                      </button>

                      {/* Expandir / contraer — o guión si no hay noticias */}
                      {hasNews ? (
                        <button
                          className={styles.iconBtn}
                          onClick={e => handleToggleExpand(e, notif.id)}
                          title={notif.isExpanded ? 'Contraer' : 'Expandir'}
                        >
                          {notif.isExpanded
                            ? <ChevronUp size={16} />
                            : <ChevronDown size={16} />
                          }
                        </button>
                      ) : (
                        <span className={styles.iconBtnDisabled} title="Sin noticias nuevas">
                          <Minus size={16} />
                        </span>
                      )}
                    </div>
                  </div>

                  {/* ── Mensaje ── */}
                  <p className={styles.alertMessage}>
                    {getAlertMessage(notif.news.length)}
                  </p>

                  {/* ── Lista de noticias — siempre montada para animar entrada y salida ── */}
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