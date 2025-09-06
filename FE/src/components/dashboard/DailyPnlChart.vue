<script setup>
import { computed } from 'vue';
import { Line } from 'vue-chartjs';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Tooltip,
  Filler,
  Legend,
} from 'chart.js';

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Tooltip,
  Filler,
  Legend
);

const props = defineProps({
  chartData: {
    type: Object,
    required: true,
    default: () => ({ labels: [], data: [] })
  }
});

const data = computed(() => {
  const isPositive = props.chartData.data.length > 0 ? props.chartData.data[props.chartData.data.length - 1] >= 0 : true;

  const positiveBorder = 'rgb(16, 185, 129)';
  const negativeBorder = 'rgb(239, 68, 68)';

  // This function will be executed by Chart.js, which provides the chart context.
  const getGradient = (context) => {
    const chart = context.chart;
    const { ctx, chartArea } = chart;

    if (!chartArea) {
      // This happens on the initial render before the chart area is defined.
      // A gradient will be applied on the next update.
      return null;
    }

    const gradient = ctx.createLinearGradient(0, chartArea.bottom, 0, chartArea.top);

    if (isPositive) {
      gradient.addColorStop(0, 'rgba(16, 185, 129, 0)');
      gradient.addColorStop(1, 'rgba(16, 185, 129, 0.4)');
    } else {
      gradient.addColorStop(0, 'rgba(239, 68, 68, 0)');
      gradient.addColorStop(1, 'rgba(239, 68, 68, 0.4)');
    }

    return gradient;
  };

  return {
    labels: props.chartData.labels,
    datasets: [
      {
        label: 'Cumulative P&L',
        backgroundColor: getGradient, // Pass the function to create the gradient
        borderColor: isPositive ? positiveBorder : negativeBorder,
        data: props.chartData.data,
        tension: 0.3,
        fill: true,
        pointRadius: 0,
        pointHoverRadius: 5,
        borderWidth: 2,
      },
    ],
  };
});

const chartOptions = computed(() => ({
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: {
      display: false,
    },
    tooltip: {
      mode: 'index',
      intersect: false,
    },
  },
  scales: {
    x: {
      display: false,
    },
    y: {
      display: true,
      grid: {
        color: 'rgba(229, 231, 235, 0.2)', // Use a hardcoded light gray color
        borderDash: [3, 3], // Dotted line effect
        drawBorder: false, // Do not draw the solid axis line
      },
      ticks: {
        color: 'var(--semantic-color-text-secondary)',
        callback: function(value) {
          return '$' + value;
        }
      },
    },
  },
}));

const hasData = computed(() => {
  return props.chartData && props.chartData.data.length > 1;
});
</script>

<template>
  <div class="chart-container">
    <Line v-if="hasData" :data="data" :options="chartOptions" />
    <div v-else class="chart-placeholder">
      <p>No trades to display.</p>
    </div>
  </div>
</template>

<style scoped>
.chart-container {
  position: relative;
  height: 100%;
  min-height: 150px;
}
.chart-placeholder {
  width: 100%;
  height: 100%;
  display: grid;
  place-items: center;
  border-radius: var(--semantic-border-radius-interactive);
  background-color: var(--semantic-color-surface-page);
  color: var(--semantic-color-text-tertiary);
  font: var(--semantic-font-style-body-sm);
}
</style>
