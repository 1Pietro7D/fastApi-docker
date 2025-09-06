<!--
// =============================================================================
// FILE: components/dashboard/EquityCurveChart.vue
// DESCRIZIONE: Implementazione del grafico della curva di equity.
// Utilizza Chart.js e vue-chartjs per renderizzare i dati calcolati
// dallo store `trades.js`.
// =============================================================================
-->

<script setup>
import { computed } from 'vue';
import { Line } from 'vue-chartjs';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  Filler, // Importato per poter colorare l'area sotto la linea
} from 'chart.js';
import { useTradesStore } from '../../stores/trades';

// Registriamo i componenti di Chart.js che useremo.
ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  Filler
);

const tradesStore = useTradesStore();

// Usiamo una computed property per reagire ai cambiamenti nei dati dello store (es. filtri).
const chartData = computed(() => {
  const equityData = tradesStore.equityCurveData;
  return {
    labels: equityData.labels,
    datasets: [
      {
        label: 'Cumulative P&L',
        backgroundColor: 'rgba(75, 192, 192, 0.2)', // Colore dell'area sotto la linea, useremo token
        borderColor: 'rgb(75, 192, 192)', // Colore della linea, useremo token
        data: equityData.data,
        tension: 0.1, // Rende la linea leggermente curva
        fill: true, // Abilita il riempimento dell'area
      },
    ],
  };
});

// Opzioni di configurazione per il grafico.
const chartOptions = computed(() => ({
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: {
      display: false, // Nascondiamo la legenda di default, il titolo è sufficiente
    },
    tooltip: {
      mode: 'index',
      intersect: false,
    },
  },
  scales: {
    x: {
      grid: {
        // Usiamo le variabili CSS dei token per i colori
        color: 'var(--semantic-color-border-muted)',
      },
      ticks: {
        color: 'var(--semantic-color-text-secondary)',
      },
    },
    y: {
      grid: {
        color: 'var(--semantic-color-border-muted)',
      },
      ticks: {
        color: 'var(--semantic-color-text-secondary)',
        // Formattiamo i tick dell'asse Y per mostrare il simbolo del dollaro
        callback: function(value) {
          return '$' + value;
        }
      },
    },
  },
}));

// Aggiungiamo una computed property per verificare se ci sono dati da mostrare.
const hasData = computed(() => {
  return tradesStore.equityCurveData && tradesStore.equityCurveData.data.length > 0;
});
</script>

<template>
  <div class="chart-card">
    <div class="chart-header">
      <h2 class="chart-title">Equity Curve</h2>
    </div>
    <div class="chart-container">
      <Line v-if="hasData" :data="chartData" :options="chartOptions" />
      <div v-else class="chart-placeholder">
        <p class="placeholder-text">No trading data available for the selected period.</p>
      </div>
    </div>
  </div>
</template>

<style scoped>
.chart-card {
  background-color: var(--semantic-color-surface-primary);
  border: var(--base-border-width-1) solid var(--semantic-color-border-default);
  border-radius: var(--semantic-border-radius-surface);
  box-shadow: var(--semantic-effect-shadow-elevation-low);
  padding: var(--semantic-size-inset-lg);
  display: flex;
  flex-direction: column;
  gap: var(--semantic-size-stack-md);
}

.chart-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.chart-title {
  font: var(--semantic-font-style-heading-xl); /* Usiamo la shorthand per i font */
  color: var(--semantic-color-text-primary);
}

/*
  Diamo un'altezza fissa al contenitore del grafico per evitare che
  il layout cambi durante il caricamento dei dati.
*/
.chart-container {
  position: relative;
  height: 320px;
}

.chart-placeholder {
  width: 100%;
  height: 100%;
  display: grid;
  place-items: center;
  border-radius: var(--semantic-border-radius-interactive);
  background-color: var(--semantic-color-surface-page);
}
.placeholder-text {
    color: var(--semantic-color-text-tertiary);
    font: var(--semantic-font-style-body-md);
}
</style>
