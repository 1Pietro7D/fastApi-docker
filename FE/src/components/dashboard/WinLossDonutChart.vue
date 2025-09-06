<script setup>
import { computed } from 'vue';
import { Doughnut } from 'vue-chartjs';
import { Chart as ChartJS, ArcElement, Tooltip, Legend } from 'chart.js';
import { useChartColors } from '../../composables/useChartColors';

ChartJS.register(ArcElement, Tooltip, Legend);

const props = defineProps({
  wins: { type: Number, required: true },
  losses: { type: Number, required: true },
  breakevens: { type: Number, required: true },
});

const { colors, isReady } = useChartColors();

const chartData = computed(() => ({
  datasets: [
    {
      data: [props.wins, props.losses, props.breakevens],
      backgroundColor: [
        colors.value.positive,
        colors.value.negative,
        colors.value.neutral,
      ],
      borderWidth: 0,
    },
  ],
}));

const chartOptions = computed(() => ({
  responsive: true,
  maintainAspectRatio: true,
  aspectRatio: 1,
  cutout: '75%',
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
  <div class="donut-chart-container">
    <Doughnut v-if="isReady && (wins + losses + breakevens > 0)" :data="chartData" :options="chartOptions" />
  </div>
</template>

<style scoped>
.donut-chart-container {
  width: 80%;
  height: 80%;
}
</style>
