<script setup>
import { computed } from 'vue';
import { Doughnut } from 'vue-chartjs';
import { Chart as ChartJS, ArcElement, Tooltip, Legend } from 'chart.js';
import { useChartColors } from '../../composables/useChartColors';

ChartJS.register(ArcElement, Tooltip, Legend);

const props = defineProps({
  value: {
    type: Number,
    required: true,
  },
});

const { colors, isReady } = useChartColors();

// Helper function to get color based on Profit Factor using Design System colors
const getPnlColor = (value) => {
  if (value < 1.5) return colors.value.negative;
  if (value < 2.5) return colors.value.textTertiary;
  return colors.value.positive;
};

const chartData = computed(() => {
  const maxVal = 4; // Set a reasonable max for the gauge scale
  const clampedValue = Math.max(0, Math.min(props.value, maxVal));

  return {
    datasets: [
      {
        data: [clampedValue, maxVal - clampedValue],
        backgroundColor: [
          getPnlColor(props.value),
          colors.value.surfaceSecondary, // Correct neutral background
        ],
        borderWidth: 0,
        circumference: 180,
        rotation: -90,
      },
    ],
  };
});

const chartOptions = computed(() => ({
  responsive: true,
  maintainAspectRatio: true,
  aspectRatio: 2, // Make it twice as wide as it is tall
  cutout: '80%', // Controls the thickness of the doughnut
  plugins: {
    legend: {
      display: false,
    },
    tooltip: {
      enabled: false,
    },
  },
}));

</script>

<template>
  <div class="gauge-chart-container">
    <Doughnut v-if="isReady" :data="chartData" :options="chartOptions" />
  </div>
</template>

<style scoped>
.gauge-chart-container {
  position: relative;
  width: 100%;
  height: 100%;
}
</style>
