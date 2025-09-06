// =============================================================================
// FILE: main.js
// DESCRIZIONE: Questo è il punto di ingresso principale dell'intera applicazione.
// È il primo file che viene eseguito e ha il compito di "assemblare"
// le parti fondamentali di Vue e dei suoi plugin.
// =============================================================================

import { createApp } from 'vue';
import { createPinia } from 'pinia';
import App from './App.vue';
import router from './router';

// --- IMPORTAZIONI DEGLI STILI GLOBALI ---
/*
  BEST PRACTICE: Importazione Centralizzata degli Stili
  Importiamo prima `index.css`, che è il nostro punto di ingresso per tutti i
  design token. A sua volta, `index.css` importa i file dei token nell'ordine
  corretto (`_base.css` e poi `tokens.css`).
  Successivamente importiamo `main.css`, che contiene gli stili globali e i reset,
  e che può quindi utilizzare i token definiti in precedenza.
*/
import '@/styles/index.css';
import '@/assets/main.css';


// --- CREAZIONE E CONFIGURAZIONE DELL'APP ---

// 1. Creiamo l'istanza principale dell'applicazione Vue.
const app = createApp(App);

// 2. Diciamo a Vue di usare Pinia per la gestione dello stato.
app.use(createPinia());

// 3. Diciamo a Vue di usare il nostro router per la navigazione.
app.use(router);


// --- MONTAGGIO DELL'APP ---

// 4. Infine, "montiamo" l'applicazione nell'elemento `#app` del DOM.
app.mount('#app');
