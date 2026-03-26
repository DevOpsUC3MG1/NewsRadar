import {
  LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer
} from 'recharts';

// Datos de prueba para NewsRadar
const data = [
  { dia: 'Lun', lecturas: 4000, compartidos: 2400 },
  { dia: 'Mar', lecturas: 3000, compartidos: 1398 },
  { dia: 'Mié', lecturas: 2000, compartidos: 9800 },
  { dia: 'Jue', lecturas: 2780, compartidos: 3908 },
  { dia: 'Vie', lecturas: 1890, compartidos: 4800 },
  { dia: 'Sáb', lecturas: 2390, compartidos: 3800 },
  { dia: 'Dom', lecturas: 3490, compartidos: 4300 },
];

export default function NewsStatsChart() {
  return (
    // El ResponsiveContainer hace que el gráfico se adapte al tamaño de la pantalla
    <div style={{ width: '100%', height: 350, marginTop: '20px' }}>
      <ResponsiveContainer>
        <LineChart
          data={data}
          margin={{ top: 5, right: 30, left: 20, bottom: 5 }}
        >
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="dia" />
          <YAxis />
          <Tooltip />
          <Legend />
          <Line type="monotone" dataKey="lecturas" stroke="#8884d8" activeDot={{ r: 8 }} />
          <Line type="monotone" dataKey="compartidos" stroke="#82ca9d" />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}