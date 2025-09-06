<!--
// =============================================================================
// FILE: components/analytics/BreakdownCard.vue
// DESCRIZIONE: Questo è un componente UI generico e riutilizzabile, progettato
// per visualizzare un "breakdown" di dati, cioè una scomposizione di una
// metrica in varie categorie (es. performance per strategia, per giorno, etc.).
// =============================================================================
-->

<script setup>
// --- PROPS ---
defineProps({
  // Il titolo della card (es. "Performance by Strategy").
  title: {
    type: String,
    required: true,
  },
  // Un array di oggetti che rappresentano le righe da visualizzare.
  // Ogni oggetto deve avere una `label` e un `value`. Può avere dati extra.
  items: {
    type: Array,
    required: true,
  },
  // La chiave dell'oggetto item che verrà usata per calcolare la larghezza della barra.
  barValueKey: {
    type: String,
    default: 'value',
  }
});
</script>

<template>
  <div class="breakdown-card">
    <h3 class="card-title">{{ title }}</h3>
    <ul class="item-list">
      <!-- Cicliamo su ogni item per creare una riga della lista. -->
      <li v-for="item in items" :key="item.label" class="item-row">
        <div class="item-info">
          <span class="item-label">{{ item.label }}</span>
          <span class="item-value">{{ item.value }}</span>
        </div>
        <!--
        Una semplice barra di progresso per un feedback visivo.
        La sua larghezza è calcolata in base al valore.
        NOTA: Questa è una visualizzazione di base, potrebbe essere migliorata.
        -->
        <div class="progress-bar-bg">
          <div
            class="progress-bar-fg"
            :style="{ width: item.barWidth || '0%' }"
            :class="item.isPositive ? 'positive' : 'negative'"
          ></div>
        </div>
      </li>
    </ul>
  </div>
</template>

<style scoped>
.breakdown-card {
  background-color: var(--semantic-color-surface-primary);
  border: var(--base-border-width-1) solid var(--semantic-color-border-default);
  border-radius: var(--semantic-border-radius-surface);
  padding: var(--semantic-size-inset-lg);
  display: flex;
  flex-direction: column;
  gap: var(--semantic-size-stack-md);
}

.card-title {
  font: var(--semantic-font-style-heading-lg);
  color: var(--semantic-color-text-primary);
}

.item-list {
  list-style-type: none;
  padding: 0;
  margin: 0;
  display: flex;
  flex-direction: column;
  gap: var(--semantic-size-stack-md);
}

.item-row {
  display: flex;
  flex-direction: column;
  gap: var(--semantic-size-stack-xs);
}

.item-info {
  display: flex;
  justify-content: space-between;
  align-items: baseline;
  font-size: var(--semantic-font-style-body-sm-font-size);
}

.item-label {
  color: var(--semantic-color-text-secondary);
}

.item-value {
  color: var(--semantic-color-text-primary);
  font-weight: var(--base-font-weight-medium);
}

.progress-bar-bg {
  width: 100%;
  height: 8px;
  background-color: var(--semantic-color-surface-secondary);
  border-radius: var(--base-border-radius-full);
  overflow: hidden;
}

.progress-bar-fg {
  height: 100%;
  border-radius: var(--base-border-radius-full);
  transition: width 0.5s var(--base-animation-easing-out);
}

.progress-bar-fg.positive {
  background-color: var(--semantic-color-feedback-positive-text);
}

.progress-bar-fg.negative {
  background-color: var(--semantic-color-feedback-negative-text);
}
</style>
