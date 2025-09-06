<!--
// =============================================================================
// FILE: views/TradesView.vue
// DESCRIZIONE: Questo componente rappresenta la "vista" della pagina "My Trades".
// Il suo unico scopo è mostrare una tabella con la lista completa di tutti
// i trade registrati dall'utente.
// =============================================================================
-->

<script setup>
// --- IMPORTAZIONI ---

// Importiamo lo store Pinia dei trade per accedere alla lista dei dati.
import { useTradesStore } from '@/stores/trades';
// Importiamo il nostro componente riutilizzabile `BaseTable` per visualizzare i dati.
import BaseTable from '@/components/ui/BaseTable.vue';


// --- LOGICA DEL COMPONENTE ---

// Creiamo un'istanza dello store per poterlo usare nel template.
const tradesStore = useTradesStore();
</script>

<template>
  <!-- Il template definisce la struttura HTML della pagina. -->
  <div class="trades-view">
    <!-- Un semplice titolo per la pagina. -->
    <h1 class="view-title">My Trades</h1>

    <!--
    Qui usiamo il nostro componente `BaseTable`.
    - `:headers` riceve la lista delle intestazioni dal getter dello store.
    - `:items` riceve la lista dei trade direttamente dallo stato dello store.
    Questo mostra la potenza di avere uno store centralizzato e componenti riutilizzabili:
    la vista diventa molto semplice e si occupa solo di "assemblare" i pezzi.
    -->
    <BaseTable
      :headers="tradesStore.tradeHeaders"
      :items="tradesStore.trades"
    />
  </div>
</template>

<style scoped>
/*
Gli stili "scoped" si applicano solo a questo componente.
In questo caso, sono stati rimossi perché la dashboard-view non esiste in questo file.
Se fossero necessari stili specifici, andrebbero qui. Esempio:
.trades-view {
  padding: var(--semantic-size-inset-xl);
}
*/
.trades-view {
  display: flex;
  flex-direction: column;
  gap: var(--semantic-size-stack-lg);
  padding: var(--semantic-size-inset-xl); /* Aggiunto padding per coerenza */
  flex-grow: 1; /* Aggiunto per occupare lo spazio disponibile */
}
.view-title {
  font: var(--semantic-font-style-heading-h3);
  color: var(--semantic-color-text-primary);
}
</style>
