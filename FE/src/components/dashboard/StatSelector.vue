<!--
// =============================================================================
// FILE: components/dashboard/StatSelector.vue
// DESCRIZIONE: Questo componente fornisce l'interfaccia (una lista di checkbox)
// per permettere all'utente di scegliere quali statistiche visualizzare
// sulla dashboard.
// =============================================================================
-->

<script setup>
// --- IMPORTAZIONI ---
import { useTradesStore } from '../../stores/trades';
import { useUiStore } from '../../stores/uiStore';
import BaseCheckbox from '../ui/BaseCheckbox.vue';

// --- STORE ---
const tradesStore = useTradesStore();
const uiStore = useUiStore();

// --- LOGICA DEL COMPONENTE ---
// Prendiamo l'oggetto di tutte le statistiche disponibili dallo store dei trade.
const allStats = tradesStore.allDashboardStats;

// Funzione che viene chiamata quando un utente clicca su una checkbox.
const handleCheckboxChange = (statKey) => {
  // Chiama l'azione nello store della UI per aggiungere/rimuovere la chiave.
  uiStore.toggleStatVisibility(statKey);
};
</script>

<template>
  <div class="stat-selector">
    <h4 class="selector-title">Customize Stats</h4>
    <div class="selector-list">
      <!--
      Cicliamo su ogni statistica disponibile in `allStats`.
      `stat` sarà l'oggetto (es. { key: 'netPnl', label: 'Net P&L', ... })
      e `key` sarà la sua chiave (es. 'netPnl').
      -->
      <div v-for="(stat, key) in allStats" :key="key" class="selector-item">
        <!--
        Usiamo il nostro componente BaseCheckbox.
        - `:model-value`: Determina se la checkbox è spuntata o meno. È spuntata se
          la sua `key` è presente nell'array `visibleStatKeys` dello uiStore.
        - `@update:modelValue`: Quando la checkbox viene cliccata, questo evento scatta
          e noi chiamiamo la nostra funzione `handleCheckboxChange` per aggiornare lo store.
          Questo è l'equivalente manuale di `v-model`.
        -->
        <BaseCheckbox
          :label="stat.label"
          :model-value="uiStore.visibleStatKeys.includes(key)"
          @update:modelValue="handleCheckboxChange(key)"
        />
      </div>
    </div>
  </div>
</template>

<style scoped>
.stat-selector {
  display: flex;
  flex-direction: column;
  gap: var(--semantic-size-stack-md);
}
.selector-title {
  font: var(--semantic-font-style-heading-lg);
  color: var(--semantic-color-text-primary);
}
.selector-list {
  display: grid;
  /* Creiamo una griglia a due colonne per la lista. */
  grid-template-columns: repeat(2, 1fr);
  gap: var(--semantic-size-stack-sm);
}
.selector-item {
  /* Stile per ogni riga della lista. */
}
</style>
