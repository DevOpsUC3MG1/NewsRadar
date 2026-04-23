# Arquitectura Frontend - NewsRadar

## Stack Tecnológico

| Tecnología | Versión | Propósito |
|-----------|---------|----------|
| **React.js** | 18+ | Framework de UI |
| **Vite** | - | Bundler y dev server |
| **react-i18next** | - | Internacionalización (ES/EN) |
| **Recharts** | - | Gráficas y estadísticas |
| **react-wordcloud** | - | Nubes de palabras |
| **Axios** | - | Cliente HTTP |

---

## Estructura de Directorios

```
frontend/
├── public/
│   └── locales/
│       ├── en/
│       │   └── translation.json    # Textos en inglés
│       └── es/
│           └── translation.json    # Textos en español
├── src/
│   ├── App.jsx                     # Componente raíz
│   ├── main.jsx                    # Entry point
│   ├── i18n.js                     # Configuración i18n
│   ├── assets/
│   │   ├── App.css                 # Estilos globales
│   │   └── index.css               # Reset CSS
│   ├── components/
│   │   ├── badge.jsx               # Componente Badge
│   │   ├── button.jsx              # Componente Button
│   │   ├── card.jsx                # Componente Card
│   │   ├── ExampleNewCharts.jsx    # Ejemplo de gráficas
│   │   ├── input.jsx               # Componente Input
│   │   ├── MainLayout.jsx          # Layout principal
│   │   ├── modal.jsx               # Componente Modal
│   │   ├── ProtectedRoute.jsx      # Guard de rutas autenticadas
│   │   ├── table.jsx               # Componente Table
│   │   ├── Header/
│   │   │   ├── Header.jsx          # Header para usuarios autenticados
│   │   │   └── Header.module.css
│   │   ├── HeaderNoUser/
│   │   │   ├── HeaderNoUser.jsx    # Header para login/registro
│   │   │   └── HeaderNoUser.module.css
│   │   └── Sidebar/
│   │       ├── Sidebar.jsx         # Navegación lateral
│   │       └── Sidebar.module.css
│   ├── context/
│   │   └── AuthContext.jsx         # Context de autenticación
│   ├── i18n/
│   │   └── (configuración i18n)
│   ├── pages/
│   │   ├── Home.jsx                # Página inicio
│   │   ├── About.jsx               # Página about
│   │   ├── UITesting.jsx           # Testing de componentes
│   │   ├── prueba.jsx              # Página de prueba
│   │   ├── login/
│   │   │   └── login.jsx           # Página de login
│   │   ├── change_pwd/
│   │   │   └── change_pwd.jsx      # Cambio de contraseña
│   │   ├── registro/               # Registro de usuario
│   │   └── verify_acc/             # Verificación de cuenta
│   └── services/
│       └── authService.js          # Servicios de autenticación
├── Dockerfile                      # Imagen Docker
├── package.json                    # Dependencias
├── vite.config.js                  # Configuración Vite
└── index.html                      # HTML principal
```

---

## Componentes Reutilizables

### Badge (badge.jsx)
**Propósito:** Mostrar etiquetas con estilos predefinidos

**Props:**
- `text`: Texto a mostrar
- `variant`: 'success' | 'warning' | 'error' | 'info'
- `size`: 'small' | 'medium' | 'large'

**Ejemplo:**
```jsx
<Badge text="Activa" variant="success" />
```

### Button (button.jsx)
**Propósito:** Botones reutilizables con estilos consistentes

**Props:**
- `onClick`: Manejador de click
- `variant`: 'primary' | 'secondary' | 'danger'
- `disabled`: Boolean
- `loading`: Boolean (muestra spinner)

**Ejemplo:**
```jsx
<Button onClick={handleSubmit} variant="primary">
  Enviar
</Button>
```

### Card (card.jsx)
**Propósito:** Contenedores con estilo card

**Props:**
- `title`: Título de la tarjeta
- `children`: Contenido
- `icon`: Icono opcional

**Ejemplo:**
```jsx
<Card title="Alertas Activas">
  <p>Contenido de la alerta</p>
</Card>
```

### Input (input.jsx)
**Propósito:** Campos de entrada unificados

**Props:**
- `type`: 'text' | 'email' | 'password' | 'number'
- `placeholder`: Texto de placeholder
- `value`: Valor actual
- `onChange`: Manejador de cambio
- `error`: String de error
- `label`: Label del input

**Ejemplo:**
```jsx
<Input
  type="email"
  label="Email"
  placeholder="usuario@ejemplo.com"
  value={email}
  onChange={(e) => setEmail(e.target.value)}
/>
```

### Modal (modal.jsx)
**Propósito:** Diálogos modales reutilizables

**Props:**
- `isOpen`: Boolean
- `onClose`: Manejador de cierre
- `title`: Título del modal
- `children`: Contenido
- `actions`: Array de botones de acción

**Ejemplo:**
```jsx
<Modal
  isOpen={showModal}
  onClose={() => setShowModal(false)}
  title="Confirmar acción"
  actions={[
    { label: "Cancelar", onClick: () => setShowModal(false) },
    { label: "Confirmar", onClick: handleConfirm }
  ]}
>
  ¿Estás seguro?
</Modal>
```

### Table (table.jsx)
**Propósito:** Tablas de datos con paginación

**Props:**
- `columns`: Array de columnas { header, key }
- `data`: Array de filas
- `onRowClick`: Manejador de click en fila
- `selectable`: Boolean (checkboxes)

**Ejemplo:**
```jsx
<Table
  columns={[
    { header: "Email", key: "email" },
    { header: "Rol", key: "role" }
  ]}
  data={usuarios}
/>
```

---

## Layouts

### MainLayout (MainLayout.jsx)
**Propósito:** Layout principal para la aplicación

**Estructura:**
```
┌─────────────────────────────────┐
│        Header                   │
├──────────┬──────────────────────┤
│ Sidebar  │ Contenido Principal  │
│          │                      │
│          │                      │
└──────────┴──────────────────────┘
```

**Componentes incluidos:**
- Header: Navegación superior
- Sidebar: Menú lateral
- Outlet para rutas

---

## Headers

### Header (Header/Header.jsx)
**Para usuarios autenticados**

**Elementos:**
- Logo/Título
- Menú de navegación
- Selector de idioma (i18n)
- Menú de usuario (perfil, logout)

### HeaderNoUser (HeaderNoUser/HeaderNoUser.jsx)
**Para usuarios no autenticados**

**Elementos:**
- Logo/Título
- Links: Inicio, Acerca de
- Botones: Login, Registro

---

## Sidebar (Sidebar/Sidebar.jsx)

**Propósito:** Navegación lateral persistente

**Items de menú:**
- Dashboard
- Alertas
- Notificaciones
- Fuentes RSS
- Categorías
- Configuración
- Logout

**Características:**
- Collapse/expand
- Items activos resaltados
- Responsive (colapsable en mobile)

---

## Autenticación

### AuthContext (context/AuthContext.jsx)

**Estado global:**
```jsx
{
  user: {
    id: 1,
    email: "usuario@ejemplo.com",
    first_name: "Juan",
    organization: "Empresa"
  },
  token: "uuid-token",
  isAuthenticated: true,
  isLoading: false
}
```

**Funciones:**
- `login(email, password)`: Autentica usuario
- `register(data)`: Registra nuevo usuario
- `logout()`: Cierra sesión
- `verify(token)`: Verifica email
- `resetPassword(token, newPassword)`: Restablece contraseña

**Uso:**
```jsx
import { useAuth } from './context/AuthContext';

function MyComponent() {
  const { user, logout } = useAuth();
  return <button onClick={logout}>Logout</button>;
}
```

---

## Protección de Rutas

### ProtectedRoute (ProtectedRoute.jsx)

**Propósito:** Guard para rutas que requieren autenticación

**Comportamiento:**
- Si usuario NO autenticado → Redirige a login
- Si usuario autenticado → Renderiza componente
- Si verificación pendiente → Muestra página de verificación

**Uso:**
```jsx
<Route
  path="/dashboard"
  element={<ProtectedRoute><Dashboard /></ProtectedRoute>}
/>
```

---

## Páginas

### Login (pages/login/login.jsx)
- Formulario de autenticación
- Validación de campos
- Rememberme (opcional)
- Link de "Olvidé contraseña"
- Link a registro

### Registro (pages/registro/)
- Formulario de registro
- Validación de email único
- Validación de contraseña segura
- Aceptación de términos
- Link a login

### Verificación (pages/verify_acc/)
- Confirmación de token
- Envío de email de verificación
- Resend option

### Cambio de Contraseña (pages/change_pwd/change_pwd.jsx)
- Input contraseña actual
- Input nueva contraseña
- Confirmación contraseña
- Validación de seguridad

### Home (pages/Home.jsx)
- Página principal del dashboard
- Resumen de alertas
- Últimas notificaciones
- Estadísticas

### About (pages/About.jsx)
- Información del proyecto
- Créditos
- Versión

---

## Internacionalización (i18n)

### Configuración (i18n.js)

```javascript
import i18n from 'i18next';
import { initReactI18next } from 'react-i18next';

i18n.use(initReactI18next).init({
  lng: 'es',
  fallbackLng: 'en',
  resources: { ... }
});
```

### Archivos de Traducción

**public/locales/es/translation.json:**
```json
{
  "common": {
    "login": "Iniciar sesión",
    "logout": "Cerrar sesión",
    "register": "Registrarse"
  },
  "alerts": {
    "title": "Alertas",
    "create": "Crear alerta"
  }
}
```

**public/locales/en/translation.json:**
```json
{
  "common": {
    "login": "Sign In",
    "logout": "Sign Out",
    "register": "Sign Up"
  },
  "alerts": {
    "title": "Alerts",
    "create": "Create Alert"
  }
}
```

### Uso en Componentes

```jsx
import { useTranslation } from 'react-i18next';

function MyComponent() {
  const { t, i18n } = useTranslation();
  
  return (
    <>
      <h1>{t('alerts.title')}</h1>
      <button onClick={() => i18n.changeLanguage('en')}>
        English
      </button>
    </>
  );
}
```

---

## Servicios

### authService.js

**Funciones:**
```javascript
// Login
login(email, password) → Promise<{access_token, token_type}>

// Registro
register(userData) → Promise<{id, email, first_name, ...}>

// Verificar email
verifyEmail(token) → Promise<{success, message}>

// Recuperar contraseña
forgotPassword(email) → Promise<{success, message}>

// Restablecer contraseña
resetPassword(token, newPassword) → Promise<{success, message}>

// Obtener perfil
getProfile() → Promise<User>

// Actualizar perfil
updateProfile(userData) → Promise<User>
```

---

## Gráficas y Visualización

### Recharts
Biblioteca para gráficas (LineChart, BarChart, PieChart)

**Ejemplo:**
```jsx
import { BarChart, Bar, XAxis, YAxis, CartesianGrid } from 'recharts';

<BarChart data={data}>
  <CartesianGrid />
  <XAxis dataKey="name" />
  <YAxis />
  <Bar dataKey="alertas" fill="#8884d8" />
</BarChart>
```

### react-wordcloud
Nubes de palabras interactivas

---

## Estilos

### CSS Modules
Se utiliza CSS Modules para componentes

**Ejemplo:**
```jsx
// Header.jsx
import styles from './Header.module.css';

export default function Header() {
  return <header className={styles.header}>...</header>;
}
```

```css
/* Header.module.css */
.header {
  display: flex;
  justify-content: space-between;
  padding: 1rem;
  background-color: #f5f5f5;
}
```

---

## Configuración Vite

### vite.config.js
```javascript
import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true
      }
    }
  }
});
```

---

## Construcción y Despliegue

### Desarrollo
```bash
npm install
npm run dev  # Inicia servidor en localhost:5173
```

### Build
```bash
npm run build  # Genera dist/
npm run preview # Preview de build
```

### Docker
```bash
docker compose -f docker-compose.yml -f docker-compose.dev.yml up
# Frontend accesible en http://localhost:5173
```

---

## Mejores Prácticas

✅ **Componentes reutilizables:** Maximizar composición
✅ **Props validation:** Validar tipos con PropTypes o TypeScript
✅ **Context API:** Para estado global (auth, tema)
✅ **Error handling:** Try-catch en servicios
✅ **Loading states:** Spinner/skeleton durante async
✅ **Responsive design:** Mobile-first
✅ **Accessibility:** ARIA labels, semantic HTML
✅ **Performance:** Code splitting, lazy loading

