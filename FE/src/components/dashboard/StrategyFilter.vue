<!--
// =============================================================================
// FILE: components/dashboard/StrategyFilter.vue
// DESCRIZIONE: Componente refattorizzato per usare bottoni invece di un select,
// per coerenza stilistica con DateRangeFilter.
// =============================================================================
-->
<script setup>
import { computed } from 'vue';
import { useTradesStore } from '../../stores/trades';
import { useFilterStore } from '../../stores/filterStore';

const tradesStore = useTradesStore();
const filterStore = useFilterStore();

const strategyOptions = computed(() => tradesStore.allStrategies);

const selectStrategy = (strategy) => {
  const strategyToSet = strategy === 'All' ? 'all' : strategy;
  filterStore.setStrategyFilter(strategyToSet);
};
</script>

<template>
  <div class="filter-group">
    <button
      v-for="strategy in strategyOptions"
      :key="strategy"
      @click="selectStrategy(strategy)"
      class="filter-button"
      :class="{ 'filter-button--active': (filterStore.selectedStrategy === strategy) || (filterStore.selectedStrategy === 'all' && strategy === 'All') }"
    >
      {{ strategy }}
    </button>
  </div>
</template>

<style scoped>
/* Stili presi da DateRangeFilter per coerenza visiva */
.filter-group {
  display: flex;
  flex-direction: column; /* Impilare i bottoni verticalmente */
  gap: var(--base-size-spacing-1);
  align-items: stretch; /* Allunga i bottoni per riempire lo spazio */
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
  text-align: left; /* Allinea il testo a sinistra */
  width: 100%;
}

.filter-button:hover {
  color: var(--semantic-color-text-primary);
  background-color: var(--semantic-color-surface-secondary);
}

/* Stile per il bottone attualmente attivo. */
.filter-button--active {
  background-color: var(--semantic-color-interactive-primary-default);
  color: var(--semantic-color-text-on-brand);
  font-weight: var(--base-font-weight-semibold);
}

.filter-button--active:hover {
  background-color: var(--semantic-color-interactive-primary-hover);
  color: var(--semantic-color-text-on-brand);
}
</style>
