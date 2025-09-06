// =============================================================================
// FILE: stores/counter.js
// DESCRIZIONE: Questo è un altro store Pinia, probabilmente creato come esempio
// iniziale. Utilizza una sintassi diversa e più moderna rispetto a `trades.js`,
// chiamata "Setup Store", che assomiglia molto alla sezione `<script setup>`
// dei componenti Vue 3.
// =============================================================================

// --- IMPORTAZIONI ---
// `ref` e `computed` sono funzioni della "Composition API" di Vue.
// `ref` crea una variabile reattiva (il suo valore può cambiare e l'interfaccia si aggiornerà).
// `computed` crea un valore calcolato che dipende da altre variabili reattive.
import { ref, computed } from 'vue';
import { defineStore } from 'pinia';

// --- DEFINIZIONE DELLO STORE ---
// Quando passiamo una funzione a `defineStore`, stiamo usando la sintassi "Setup Store".
export const useCounterStore = defineStore('counter', () => {
  // --- STATO (State) ---
  // `count` è la nostra variabile di stato. È come una proprietà dentro `state: () => ({...})`.
  const count = ref(0);

  // --- GETTERS ---
  // `doubleCount` è un getter. È una proprietà calcolata che si aggiorna automaticamente
  // quando `count` cambia. È come un getter nell'oggetto `getters: {}`.
  const doubleCount = computed(() => count.value * 2);

  // --- AZIONI (Actions) ---
  // `increment` è un'azione. È una funzione che modifica lo stato.
  // È come un metodo nell'oggetto `actions: {}`.
  function increment() {
    count.value++; // Incrementiamo il valore di `count`.
  }

  // --- ESPORTAZIONE DELLO STORE ---
  // In un setup store, dobbiamo restituire esplicitamente tutte le variabili
  // e le funzioni che vogliamo rendere accessibili dall'esterno.
  return { count, doubleCount, increment };
});
