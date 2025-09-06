// =============================================================================
// FILE: src/services/api.js
// DESCRIPTION: This file centralizes all API communication. It creates a
// pre-configured instance of axios. Using this centralized file makes it
// easy to manage things like authentication headers or base URLs in one place.
//
// DESCRIZIONE: Questo file centralizza tutta la comunicazione con le API.
// Crea un'istanza pre-configurata di axios. Usare questo file centralizzato
// rende facile gestire in un unico posto cose come gli header di
// autenticazione o gli URL di base.
// =============================================================================

import axios from 'axios';

// --- AXIOS INSTANCE CREATION ---
// We create a new axios instance. This allows us to have a configuration
// specific to our backend API.
//
// CREAZIONE DELL'ISTANZA DI AXIOS
// Creiamo una nuova istanza di axios. Questo ci permette di avere una
// configurazione specifica per la nostra API backend.

const apiClient = axios.create({
  // The base URL for all API requests. Vite exposes environment variables
  // on the `import.meta.env` object. We'll create a .env file to define
  // VITE_API_URL.
  //
  // L'URL di base per tutte le richieste API. Vite espone le variabili
  // d'ambiente sull'oggetto `import.meta.env`. Creeremo un file .env
  // per definire VITE_API_URL.
  baseURL: import.meta.env.VITE_API_URL,

  // We can set default headers here, for example, for authentication.
  // Qui possiamo impostare degli header di default, ad esempio per l'autenticazione.
  headers: {
    'Content-Type': 'application/json',
  },
});

// --- EXPORT ---
// We export the configured instance to be used throughout the application.
//
// ESPORTAZIONE
// Esportiamo l'istanza configurata per essere usata in tutta l'applicazione.
export default apiClient;
