// =============================================================================
// FILE: stores/filterStore.js
// DESCRIZIONE: Questo store Pinia gestisce lo stato dei filtri dell'interfaccia,
// in particolare l'intervallo di date per l'analisi dei dati.
// Avere uno store separato per i filtri mantiene il codice organizzato.
// =============================================================================

import { defineStore } from 'pinia';
import { ref, computed } from 'vue';

// Definiamo lo store usando la sintassi "Setup Store"
export const useFilterStore = defineStore('filters', () => {

  // --- STATO (State) ---
  // `selectedPreset` tiene traccia del preset di date attualmente attivo (es. '7d', '30d').
  const selectedPreset = ref('30d');

  // `startDate` e `endDate` memorizzano l'intervallo di date calcolato.
  // Vengono inizializzati chiamando subito l'azione per il preset di default.
  const startDate = ref(null);
  const endDate = ref(new Date());

  // Nuovo stato per il filtro per strategia
  const selectedStrategy = ref('all'); // 'all' indica nessun filtro

  // --- AZIONI (Actions) ---

  // `setStrategyFilter` aggiorna la strategia selezionata.
  function setStrategyFilter(strategy) {
    selectedStrategy.value = strategy;
  }

  // `setDateRangeFromPreset` aggiorna l'intervallo di date in base a un preset.
  function changeMonth(direction) {
    const currentDate = new Date(endDate.value);
    currentDate.setDate(1);
    currentDate.setMonth(currentDate.getMonth() + direction);

    startDate.value = new Date(currentDate.getFullYear(), currentDate.getMonth(), 1);
    endDate.value = new Date(currentDate.getFullYear(), currentDate.getMonth() + 1, 0);
    selectedPreset.value = null;
  }

  function setDateRangeFromPreset(preset) {
    const end = new Date();
    const start = new Date();

    switch (preset) {
      case '7d':
        start.setDate(end.getDate() - 7);
        break;
      case '30d':
        start.setDate(end.getDate() - 30);
        break;
      case '90d':
        start.setDate(end.getDate() - 90);
        break;
      case 'ytd': // Year-to-date
        start.setMonth(0, 1); // Primo giorno dell'anno corrente
        break;
      default:
        // Se il preset non è riconosciuto, non facciamo nulla o impostiamo un default.
        // In questo caso, reimpostiamo a 30 giorni.
        start.setDate(end.getDate() - 30);
        preset = '30d';
        break;
    }

    // Aggiorniamo lo stato dello store
    selectedPreset.value = preset;
    endDate.value = end;
    startDate.value = start;
  }

  // --- INIZIALIZZAZIONE ---
  // Chiamiamo l'azione una volta all'avvio per impostare le date iniziali
  // basate sul preset di default ('30d').
  setDateRangeFromPreset(selectedPreset.value);

  // --- ESPORTAZIONE ---
  // Restituiamo le variabili e le azioni che vogliamo rendere accessibili
  // ad altri componenti e store.
  return {
    selectedPreset,
    startDate,
    endDate,
    selectedStrategy,
    setDateRangeFromPreset,
    setStrategyFilter,
    changeMonth,
  };
});
