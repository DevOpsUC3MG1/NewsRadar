import { StrictMode, Suspense } from 'react'
import { createRoot } from 'react-dom/client'
import './assets/index.css'
import App from './App.jsx'
import { AuthProvider } from './context/AuthContext.jsx'
import './i18n'

// Componente de carga bonito y centrado
const LoadingScreen = () => (
  <div className="initial-loader-container">
    <div className="spinner"></div>
    <h2 className="loader-title">NEWSRADAR</h2>
  </div>
);

createRoot(document.getElementById('root')).render(
  <StrictMode>
    <Suspense fallback={<LoadingScreen />}>
      <AuthProvider>
        <App />
      </AuthProvider>
    </Suspense>
  </StrictMode>,
)