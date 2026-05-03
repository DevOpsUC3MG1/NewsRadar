import React, { useState, useEffect } from 'react';
import { Settings, Search, Newspaper, Bell, MailOpen } from 'lucide-react';
import styles from './notificaciones.module.css';

// ─── Modal de confirmación ────────────────────────────────────────────────────
const ConfirmModal = ({ onConfirm, onCancel }) => (
  <div className={styles.modalOverlay} onClick={onCancel}>
    <div className={styles.modalBox} onClick={(e) => e.stopPropagation()}>
      <h3 className={styles.modalTitle}>Limpiar buzón</h3>
      <p className={styles.modalText}>
        ¿Estás seguro de que quieres eliminar todas las notificaciones? Esta acción no se puede deshacer.
      </p>
      <div className={styles.modalActions}>
        <button className={styles.modalCancel} onClick={onCancel}>Cancelar</button>
        <button className={styles.modalConfirm} onClick={onConfirm}>Eliminar todo</button>
      </div>
    </div>
  </div>
);

const Notifications = () => {
  const [notifications, setNotifications] = useState([]);
  const [loading, setLoading]             = useState(true);
  const [error, setError]                 = useState(false);
  const [visibleCount, setVisibleCount]   = useState(4);
  const [showModal, setShowModal]         = useState(false);

  const fetchNotifications = async () => {
    setLoading(true);
    setError(false);
    try {
      await new Promise(resolve => setTimeout(resolve, 1500));
      const mockData = [
        { id: 1, type: 'maintenance', title: 'Mantenimiento del Servidor',    message: 'Habrá un corte de servicio programado esta noche de 02:00 a 04:00 AM para mejoras en la base de datos.', date: 'Hace 2 horas', isRead: false },
        { id: 2, type: 'new_source',  title: 'Nueva fuente disponible',       message: 'Se ha añadido "El Periódico" a la lista de fuentes disponibles.',                                          date: 'Hace 5 horas', isRead: false },
        { id: 3, type: 'new_rss',     title: 'Nuevas publicaciones RSS',      message: 'Tu alerta "Tecnología e IA" ha encontrado 14 nuevos artículos.',                                           date: 'Hace 8 horas', isRead: false },
        { id: 4, type: 'new_rss',     title: 'Nuevas publicaciones RSS',      message: 'Tu alerta "Economía Europea" ha encontrado 3 nuevos artículos.',                                           date: 'Ayer',         isRead: true  },
        { id: 5, type: 'new_source',  title: 'Nueva fuente disponible',       message: 'Se ha añadido "Revista Científica" a la lista de fuentes.',                                               date: 'Hace 2 días',  isRead: true  },
        { id: 6, type: 'maintenance', title: 'Actualización completada',      message: 'El sistema ha sido actualizado a la versión 2.1 con éxito.',                                              date: 'Hace 3 días',  isRead: true  },
      ];
      setNotifications(mockData);
    } catch (err) {
      setError(true);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { fetchNotifications(); }, []);

  const markAsRead = (id) =>
    setNotifications(prev => prev.map(n => n.id === id ? { ...n, isRead: true } : n));

  const markAllAsRead = () =>
    setNotifications(prev => prev.map(n => ({ ...n, isRead: true })));

  const handleClearConfirmed = () => {
    setNotifications([]);
    setShowModal(false);
  };

  const visibleNotifications = notifications.slice(0, visibleCount);
  const unreadCount = notifications.filter(n => !n.isRead).length;

  const getIconData = (type, isRead) => {
    const opacity = isRead ? 0.45 : 1;
    switch (type) {
      case 'maintenance':
        return { Icon: Settings,  color: `rgba(255,184,0,${opacity})`,   bg: isRead ? 'rgba(255,184,0,0.06)' : 'rgba(255,184,0,0.12)' };
      case 'new_source':
        return { Icon: Search,    color: `rgba(78,141,245,${opacity})`,  bg: isRead ? 'rgba(78,141,245,0.06)' : 'rgba(78,141,245,0.12)' };
      case 'new_rss':
        return { Icon: Newspaper, color: `rgba(46,204,113,${opacity})`,  bg: isRead ? 'rgba(46,204,113,0.06)' : 'rgba(46,204,113,0.12)' };
      default:
        return { Icon: Bell,      color: `rgba(150,150,150,${opacity})`, bg: 'rgba(150,150,150,0.1)' };
    }
  };

  const SkeletonNotification = () => (
    <div className={styles.notificationCard}>
      <div className={`${styles.skeleton} ${styles.skeletonIcon}`} />
      <div className={styles.notificationContent}>
        <div className={`${styles.skeleton} ${styles.skeletonTitle}`} />
        <div className={`${styles.skeleton} ${styles.skeletonText}`} />
      </div>
    </div>
  );

  if (error) {
    return (
      <div className={styles.pageWrapper}>
        <div className={styles.errorContainer}>
          <h2>Error al cargar notificaciones</h2>
          <button className={styles.actionButton} onClick={fetchNotifications}>Reintentar</button>
        </div>
      </div>
    );
  }

  return (
    <div className={styles.pageWrapper}>
      {/* Modal de confirmación */}
      {showModal && (
        <ConfirmModal
          onConfirm={handleClearConfirmed}
          onCancel={() => setShowModal(false)}
        />
      )}

      <div className={styles.centerContainer}>

        {/* CABECERA */}
        <div className={styles.header}>
          <h1 className={styles.title}>NOTIFICACIONES</h1>
          <div className={styles.headerActions}>
            {unreadCount > 0 && (
              <button className={styles.textButton} onClick={markAllAsRead}>
                Marcar todas como leídas
              </button>
            )}
            {notifications.length > 0 && (
              <button className={styles.clearButton} onClick={() => setShowModal(true)}>
                Limpiar buzón
              </button>
            )}
          </div>
        </div>

        {/* LISTA */}
        <div className={styles.listContainer}>
          {loading ? (
            [1, 2, 3, 4].map(i => <SkeletonNotification key={i} />)
          ) : notifications.length === 0 ? (
            <div className={styles.emptyState}>
              <MailOpen size={52} strokeWidth={1.2} className={styles.emptyIcon} />
              <p>No hay notificaciones disponibles.</p>
              <button className={styles.actionButton} onClick={fetchNotifications}>Actualizar</button>
            </div>
          ) : (
            <>
              {visibleNotifications.map(notif => {
                const { Icon, color, bg } = getIconData(notif.type, notif.isRead);
                return (
                  <div
                    key={notif.id}
                    className={`${styles.notificationCard} ${notif.isRead ? styles.read : styles.unread}`}
                    onClick={() => !notif.isRead && markAsRead(notif.id)}
                  >
                    {!notif.isRead && <div className={styles.unreadDot} />}

                    <div className={styles.iconContainer} style={{ backgroundColor: bg }}>
                      <Icon size={22} color={color} strokeWidth={1.8} />
                    </div>

                    <div className={styles.notificationContent}>
                      <div className={styles.contentHeader}>
                        <h3 className={`${styles.notifTitle} ${notif.isRead ? styles.readText : ''}`}>
                          {notif.title}
                        </h3>
                        <span className={styles.notifDate}>{notif.date}</span>
                      </div>
                      <p className={`${styles.notifMessage} ${notif.isRead ? styles.readText : ''}`}>
                        {notif.message}
                      </p>
                    </div>
                  </div>
                );
              })}

              {visibleCount < notifications.length && (
                <div className={styles.loadMoreContainer}>
                  <button
                    className={styles.loadMoreButton}
                    onClick={() => setVisibleCount(notifications.length)}
                  >
                    Mostrar más
                  </button>
                </div>
              )}
            </>
          )}
        </div>
      </div>
    </div>
  );
};

export default Notifications;