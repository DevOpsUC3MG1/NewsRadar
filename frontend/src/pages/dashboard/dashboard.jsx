import React, { useState, useEffect } from 'react';
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
  Cell, PieChart, Pie, Legend
} from 'recharts';
import styles from './dashboard.module.css';

const Dashboard = () => {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(false);

  // Ejemplo práctico: Simulación de llamada a la API
  const fetchDashboardData = async () => {
    setLoading(true);
    setError(false);
    try {
      // Simulamos un retraso de red de 2 segundos
      await new Promise(resolve => setTimeout(resolve, 2000));

      // Simulación de respuesta exitosa del backend
      const response = {
        metrics: [
          { title: "FUENTES ACTIVAS", value: 12, change: "+12% esta semana", type: "pos" },
          { title: "NOTICIAS CAPTURADAS", value: "1,420", change: "-1% esta semana", type: "neg" },
          { title: "ALERTAS CONFIGURADAS", value: 8, change: "Sin cambios", type: "neutral" },
          { title: "CANALES RSS", value: 104, change: "+8% esta semana", type: "pos" }
        ],
        evolucion: [
          { name: 'Lun', noticias: 45 }, { name: 'Mar', noticias: 52 },
          { name: 'Mie', noticias: 38 }, { name: 'Jue', noticias: 65 },
          { name: 'Vie', noticias: 48 }, { name: 'Sab', noticias: 20 },
          { name: 'Dom', noticias: 15 }
        ],
        categorias: [
          { name: 'Política', value: 400 }, { name: 'Economía', value: 300 },
          { name: 'Salud', value: 200 }, { name: 'Tecno', value: 100 }
        ]
      };

      setData(response);
    } catch (err) {
      setError(true);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchDashboardData();
  }, []);

  // Componente interno para mostrar la carga en las tarjetas pequeñas
  const SkeletonCard = () => (
    <div className={styles.card}>
      <div className={`${styles.skeleton} ${styles.skeletonText}`}></div>
      <div className={`${styles.skeleton} ${styles.skeletonValue}`}></div>
    </div>
  );

  // 1. Caso de Error
  if (error) {
    return (
      <div className={styles.dashboardWrapper}>
        <div className={styles.errorContainer}>
          <h2>¡Ups! Algo salió mal al cargar el dashboard</h2>
          <p>No pudimos conectar con el servidor de NewsRadar.</p>
          <button className={styles.retryButton} onClick={fetchDashboardData}>
            Reintentar conexión
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className={styles.dashboardWrapper}>

      {/* FILA 1: KPIs */}
      <div className={styles.topRow}>
        {loading ? (
          // 2. Caso de Carga: Mostramos 4 esqueletos
          [1, 2, 3, 4].map(i => <SkeletonCard key={i} />)
        ) : (
          // 3. Caso de Éxito: Datos reales
          data.metrics.map((item, idx) => (
            <div className={styles.card} key={idx}>
              <span className={styles.cardTitle}>{item.title}</span>
              <span className={styles.metricValue}>{item.value}</span>
              <span className={`${styles.percentage} ${styles[item.type]}`}>
                {item.change}
              </span>
            </div>
          ))
        )}
      </div>

      {/* FILA 2: Gráficas */}
      <div className={styles.bottomRow}>

        {/* Gráfica de Evolución */}
        <div className={`${styles.card} ${styles.largeCard}`}>
          <span className={styles.cardTitle}>EVOLUCIÓN DE CAPTURA</span>
          <div className={styles.chartContainer}>
            {loading ? (
              <div className={`${styles.skeleton}`} style={{height: '100%'}}></div>
            ) : (
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={data.evolucion}>
                  <CartesianGrid strokeDasharray="3 3" vertical={false} />
                  <XAxis dataKey="name" axisLine={false} tickLine={false} />
                  <YAxis axisLine={false} tickLine={false} />
                  <Tooltip />
                  <Bar dataKey="noticias" fill="#0088FE" radius={[4, 4, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            )}
          </div>
        </div>

        {/* Gráfica de Categorías */}
        <div className={`${styles.card} ${styles.largeCard}`}>
          <span className={styles.cardTitle}>NOTICIAS POR CATEGORÍA</span>
          <div className={styles.chartContainer}>
            {loading ? (
              <div className={`${styles.skeleton}`} style={{height: '100%'}}></div>
            ) : (
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie
                    data={data.categorias}
                    innerRadius={50}
                    outerRadius={70}
                    paddingAngle={5}
                    dataKey="value"
                    label={({ name }) => name}
                  >
                    {data.categorias.map((entry, index) => (
                      <Cell key={index} fill={['#0088FE', '#00C49F', '#FFBB28', '#FF8042'][index % 4]} />
                    ))}
                  </Pie>
                  <Legend verticalAlign="bottom" height={36}/>
                </PieChart>
              </ResponsiveContainer>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;