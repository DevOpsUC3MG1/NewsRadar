import React, { useState, useEffect } from 'react';
import styles from './notificaciones.module.css';

const Notifications = () => {
  const [notifications, setNotifications] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(false);
  const [visibleCount, setVisibleCount] = useState(4);

  const fetchNotifications = async () => {
    setLoading(true);
    setError(false);
    try {
      await new Promise(resolve => setTimeout(resolve, 1500));

      const mockData = [
        { id: 1, type: 'maintenance', title: 'Mantenimiento del Servidor', message: 'Habrá un corte de servicio programado esta noche de 02:00 a 04:00 AM para mejoras en la base de datos.', date: 'Hace 2 horas', isRead: false },
        { id: 2, type: 'new_source', title: 'Nueva fuente disponible', message: 'Se ha añadido "El Periódico" a la lista de fuentes disponibles.', date: 'Hace 5 horas', isRead: false },
        { id: 3, type: 'new_rss', title: 'Nuevas publicaciones RSS', message: 'Tu alerta "Tecnología e IA" ha encontrado 14 nuevos artículos.', date: 'Hace 8 horas', isRead: false },
        { id: 4, type: 'new_rss', title: 'Nuevas publicaciones RSS', message: 'Tu alerta "Economía Europea" ha encontrado 3 nuevos artículos.', date: 'Ayer', isRead: true },
        { id: 5, type: 'new_source', title: 'Nueva fuente disponible', message: 'Se ha añadido "Revista Científica" a la lista de fuentes.', date: 'Hace 2 días', isRead: true },
        { id: 6, type: 'maintenance', title: 'Actualización completada', message: 'El sistema ha sido actualizado a la versión 2.1 con éxito.', date: 'Hace 3 días', isRead: true },
      ];

      setNotifications(mockData);
    } catch (err) {
      setError(true);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchNotifications();
  }, []);

  const markAsRead = (id) => {
    setNotifications(prev => 
      prev.map(notif => notif.id === id ? { ...notif, isRead: true } : notif)
    );
  };

  const markAllAsRead = () => {
    setNotifications(prev => prev.map(notif => ({ ...notif, isRead: true })));
  };

  // NUEVA FUNCIÓN: Limpiar todas las notificaciones
  const clearAllNotifications = () => {
    if (window.confirm('¿Estás seguro de que quieres vaciar el buzón?')) {
      setNotifications([]);
    }
  };

  const visibleNotifications = notifications.slice(0, visibleCount);
  const unreadCount = notifications.filter(n => !n.isRead).length;

  const SkeletonNotification = () => (
    <div className={styles.notificationCard}>
      <div className={`${styles.skeleton} ${styles.skeletonIcon}`}></div>
      <div className={styles.notificationContent}>
        <div className={`${styles.skeleton} ${styles.skeletonTitle}`}></div>
        <div className={`${styles.skeleton} ${styles.skeletonText}`}></div>
      </div>
    </div>
  );

  const getIconData = (type) => {
    switch(type) {
      case 'maintenance': return { icon: '⚙️', color: '#FFB800' }; 
      case 'new_source': return { icon: '🔍', color: '#4e8df5' }; 
      case 'new_rss': return { icon: '📰', color: '#2ecc71' }; 
      default: return { icon: '🔔', color: '#666666' };
    }
  };

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
      <div className={styles.centerContainer}>
        
        <div className={styles.header}>
          <h1 className={styles.title}>NOTIFICACIONES</h1>
          
          {/* GRUPO DE BOTONES DE ACCIÓN */}
          <div className={styles.headerActions}>
            {unreadCount > 0 && (
              <button className={styles.textButton} onClick={markAllAsRead}>
                Marcar todas como leídas
              </button>
            )}
            {notifications.length > 0 && (
              <button className={styles.clearButton} onClick={clearAllNotifications}>
                Limpiar buzón
              </button>
            )}
          </div>
        </div>

        <div className={styles.listContainer}>
          {loading ? (
            [1, 2, 3, 4].map(i => <SkeletonNotification key={i} />)
          ) : notifications.length === 0 ? (
            /* ESTADO VACÍO */
            <div className={styles.emptyState}>
              <span className={styles.emptyIcon}>📭</span>
              <p>No hay notificaciones disponibles.</p>
              <button className={styles.actionButton} onClick={fetchNotifications}>Actualizar</button>
            </div>
          ) : (
            <>
              {visibleNotifications.map(notif => {
                const { icon, color } = getIconData(notif.type);
                return (
                  <div 
                    key={notif.id} 
                    className={`${styles.notificationCard} ${!notif.isRead ? styles.unread : ''}`}
                    onClick={() => !notif.isRead && markAsRead(notif.id)}
                  >
                    {!notif.isRead && <div className={styles.unreadDot}></div>}
                    <div className={styles.iconContainer} style={{ backgroundColor: `${color}20`, color: color }}>
                      {icon}
                    </div>
                    <div className={styles.notificationContent}>
                      <div className={styles.contentHeader}>
                        <h3 className={styles.notifTitle}>{notif.title}</h3>
                        <span className={styles.notifDate}>{notif.date}</span>
                      </div>
                      <p className={styles.notifMessage}>{notif.message}</p>
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