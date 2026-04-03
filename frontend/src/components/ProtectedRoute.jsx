import { useContext } from 'react';
import { Navigate } from 'react-router-dom';
import { AuthContext } from '../context/AuthContext';

export default function ProtectedRoute({ children }) {
  // Consumimos nuestro contexto para saber el estado del usuario
  const { user, loading } = useContext(AuthContext);

  // Mientras leemos el token del disco duro, mostramos una pantalla de carga
  if (loading) {
    return (
      <div style={{ display: 'flex', justifyContent: 'center', marginTop: '50px' }}>
        <h2>Cargando aplicación...</h2>
      </div>
    );
  }

  // Si no hay usuario logueado, lo expulsamos a la pantalla de entrada
  if (!user) {
    return <Navigate to="/" replace />;
  }

  // Si todo está bien, renderizamos el componente que intentaba ver (ej. Home)
  return children;
}