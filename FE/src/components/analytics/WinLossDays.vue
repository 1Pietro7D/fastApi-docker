<!--
// =============================================================================
// FILE: components/analytics/WinLossDays.vue
// DESCRIZIONE: Un componente-widget che visualizza il conteggio dei giorni
// di trading positivi, negativi e in pareggio.
// =============================================================================
-->

<script setup>
import { computed } from 'vue';
import { useTradesStore } from '../../stores/trades';

const tradesStore = useTradesStore();

// Usiamo una computed property per accedere ai dati in modo reattivo.
const stats = computed(() => tradesStore.winLossDays);

const totalDays = computed(() => {
  return stats.value.winningDays + stats.value.losingDays + stats.value.breakEvenDays;
});
</script>

<template>
  <div class="breakdown-card">
    <h3 class="card-title">Win / Loss Days</h3>
    <div v-if="totalDays > 0" class="stats-container">
      <div class="stat-item">
        <span class="stat-value positive">{{ stats.winningDays }}</span>
        <span class="stat-label">Winning Days</span>
      </div>
      <div class="stat-item">
        <span class="stat-value negative">{{ stats.losingDays }}</span>
        <span class="stat-label">Losing Days</span>
      </div>
      <div class="stat-item">
        <span class="stat-value neutral">{{ stats.breakEvenDays }}</span>
        <span class="stat-label">Break-Even Days</span>
      </div>
    </div>
    <div v-else class="no-data-placeholder">
      <p>No trading days in the selected period.</p>
    </div>
  </div>
</template>

<style scoped>
/* Riusiamo lo stile di BreakdownCard per coerenza */
.breakdown-card {
  background-color: var(--semantic-color-surface-primary);
  border: 1px solid var(--semantic-color-border-default);
  border-radius: var(--semantic-border-radius-surface);
  padding: var(--semantic-size-inset-lg);
  display: flex;
  flex-direction: column;
  gap: var(--semantic-size-stack-md);
}

.card-title {
  font: var(--semantic-font-style-heading-md);
  color: var(--semantic-color-text-primary);
}

.stats-container {
  display: flex;
  justify-content: space-around;
  text-align: center;
}

.stat-item {
  display: flex;
  flex-direction: column;
  gap: var(--semantic-size-stack-xs);
}

.stat-value {
  font: var(--semantic-font-style-heading-xl);
  font-weight: var(--base-font-weight-bold);
}

.stat-label {
  font: var(--semantic-font-style-body-sm);
  color: var(--semantic-color-text-secondary);
}

.positive {
  color: var(--semantic-color-text-positive);
}

.negative {
  color: var(--semantic-color-text-negative);
}

.neutral {
  color: var(--semantic-color-text-secondary);
}

.no-data-placeholder {
  text-align: center;
  color: var(--semantic-color-text-tertiary);
  padding: var(--semantic-size-inset-xl);
  font: var(--semantic-font-style-body-md);
}
</style>
