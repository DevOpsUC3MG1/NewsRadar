// frontend/src/i18n.js
import i18n from 'i18next';
import { initReactI18next } from 'react-i18next';
import HttpApi from 'i18next-http-backend';
import LanguageDetector from 'i18next-browser-languagedetector';

// Inicializar i18next
i18n
  .use(HttpApi) // Permite cargar archivos JSON de traducción
  .use(LanguageDetector) // Detecta automáticamente el idioma del navegador
  .use(initReactI18next) // Conecta i18next con React
  .init({
    supportedLngs: ['en', 'es'], // Idiomas disponibles
    fallbackLng: 'en', // Idioma por defecto si no encuentra traducción
    debug: true, // Opcional: muestra logs en consola
    interpolation: {
      escapeValue: false, // React ya escapa por seguridad
    },
    backend: {
      loadPath: '/locales/{{lng}}/translation.json', // Ruta a archivos de traducción
    },
    react: {
      useSuspense: true, // Para cargar traducciones de manera asíncrona
    },
  });

export default i18n;