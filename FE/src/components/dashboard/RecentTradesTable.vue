<!--
// =============================================================================
// FILE: components/dashboard/RecentTradesTable.vue
// DESCRIZIONE: Questo componente visualizza una tabella di trade recenti.
// È stato rifattorizzato per leggere i dati direttamente dallo store Pinia,
// rendendolo reattivo ai cambiamenti dello stato centrale.
// =============================================================================
-->

<script setup>
// --- IMPORTAZIONI ---
import BaseTable from '../ui/BaseTable.vue';
// 1. Importiamo lo store dei trade.
import { useTradesStore } from '../../stores/trades';

// --- LOGICA DEL COMPONENTE ---
// 2. Creiamo un'istanza dello store.
const tradesStore = useTradesStore();

// 3. I dati finti locali (`recentTrades`) sono stati rimossi.
//    Useremo direttamente i getters dello store nel template.
//    Anche le intestazioni le prendiamo dallo store per coerenza.
const headers = tradesStore.tradeHeaders;
</script>

<template>
  <div class="recent-trades-card">
    <h2 class="card-title">Recent Trades</h2>
    <!--
    Ora `:items` è collegato al getter `recentTrades` dello store.
    Qualsiasi modifica alla lista dei trade nello store (es. un nuovo trade aggiunto)
    verrà automaticamente riflessa qui.
    -->
    <BaseTable :headers="headers" :items="tradesStore.recentTrades">
      <!-- La personalizzazione dello slot per il P&L rimane invariata. -->
      <template #pnl="{ item }">
        <span :class="item.pnl >= 0 ? 'pnl-positive' : 'pnl-negative'">
          {{ item.pnl >= 0 ? '+' : '' }}${{ Math.abs(item.pnl).toFixed(2) }}
        </span>
      </template>
    </BaseTable>
  </div>
</template>

<style scoped>
/* Stili specifici per questo componente. */
.recent-trades-card {
  display: flex;
  flex-direction: column;
  gap: var(--semantic-size-stack-md);
  background-color: var(--semantic-color-surface-primary);
  border: var(--base-border-width-1) solid var(--semantic-color-border-default);
  border-radius: var(--semantic-border-radius-surface);
  box-shadow: var(--semantic-effect-shadow-elevation-low);
  padding: var(--semantic-size-inset-lg);
}
.card-title {
  font-family: var(--semantic-font-style-heading-xl-font-family);
  font-size: var(--semantic-font-style-heading-xl-font-size);
  font-weight: var(--semantic-font-style-heading-xl-font-weight);
  color: var(--semantic-color-text-primary);
}

.pnl-positive {
  color: var(--semantic-color-feedback-positive-text);
  font-family: var(--semantic-font-style-data-numeric-font-family);
}
.pnl-negative {
  color: var(--semantic-color-feedback-negative-text);
  font-family: var(--semantic-font-style-data-numeric-font-family);
}
</style>
