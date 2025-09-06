<!--
// =============================================================================
// FILE: components/dashboard/DateRangeFilter.vue
// DESCRIZIONE: Questo componente gestisce l'interfaccia per la selezione
// dell'intervallo di date. Mostra una serie di bottoni per i preset
// comuni e si interfaccia con il `filterStore` per aggiornare lo stato globale.
// =============================================================================
-->

<script setup>
// --- IMPORTAZIONI ---
import { useFilterStore } from '../../stores/filterStore';

// --- LOGICA DEL COMPONENTE ---
// Creiamo un'istanza dello store dei filtri.
const filterStore = useFilterStore();

// Definiamo i preset che vogliamo mostrare come bottoni.
const presets = [
  { key: '7d', label: '7D' },
  { key: '30d', label: '30D' },
  { key: '90d', label: '90D' },
  { key: 'ytd', label: 'YTD' },
];

// Funzione chiamata al click di un bottone.
const selectPreset = (presetKey) => {
  // Chiama l'azione dello store per aggiornare l'intervallo di date.
  filterStore.setDateRangeFromPreset(presetKey);
};
</script>

<template>
  <div class="filter-group">
    <!-- Creiamo un bottone per ogni preset definito nell'array. -->
    <button
      v-for="preset in presets"
      :key="preset.key"
      @click="selectPreset(preset.key)"
      class="filter-button"
      :class="{ 'filter-button--active': filterStore.selectedPreset === preset.key }"
    >
      {{ preset.label }}
    </button>
  </div>
</template>

<style scoped>
/* Stili specifici per questo componente. */
.filter-group {
  display: flex;
  gap: var(--base-size-spacing-2);
  /* The background and padding are now handled by the Dropdown container */
}

.filter-button {
  /* Stili di base del bottone */
  font: var(--semantic-font-style-label-md);
  color: var(--semantic-color-text-secondary);
  background-color: transparent;
  border: none;
  padding: var(--base-size-spacing-1-5) var(--base-size-spacing-3);
  border-radius: var(--base-border-radius-sm);
  cursor: pointer;
  transition: all var(--base-animation-duration-fast);
}

.filter-button:hover {
  color: var(--semantic-color-text-primary);
  background-color: var(--semantic-color-surface-primary);
}

/* Stile per il bottone attualmente attivo. */
.filter-button--active {
  background-color: var(--semantic-color-surface-primary);
  color: var(--semantic-color-text-primary);
  font-weight: var(--base-font-weight-semibold);
  box-shadow: var(--base-effect-shadow-sm);
}
</style>
