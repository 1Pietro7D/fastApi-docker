<!--
// =============================================================================
// FILE: components/analytics/StrategyPerformance.vue
// DESCRIZIONE: Versione refattorizzata. Questo componente è ora molto più
// semplice, perché il lavoro di formattazione dei dati viene fatto
// direttamente nel getter `strategyPerformanceData` dello store.
// =============================================================================
-->

<script setup>
// --- IMPORTAZIONI ---
import { useTradesStore } from '../../stores/trades';
import BreakdownCard from './BreakdownCard.vue';

// --- LOGICA DEL COMPONENTE ---
const tradesStore = useTradesStore();

// La complessa proprietà `computed` è stata rimossa.
// Ora il componente si limita a passare i dati già pronti dal getter
// al componente di visualizzazione.
</script>

<template>
  <!--
  Passiamo direttamente i dati dal getter `strategyPerformanceData`
  alla prop `items` del nostro componente riutilizzabile.
  -->
  <BreakdownCard
    title="Performance by Strategy"
    :items="tradesStore.strategyPerformanceData"
  />
</template>

<style scoped>
/* Questo componente non ha bisogno di stili propri. */
</style>
