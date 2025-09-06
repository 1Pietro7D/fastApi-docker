// src/composables/useChartColors.js
import { onMounted, ref } from 'vue';

/**
 * Un composable riutilizzabile per recuperare i colori semantici dal foglio di stile principale.
 * Include colori di fallback e una flag `isReady` per garantire un rendering robusto.
 */
export function useChartColors() {
  const isReady = ref(false);
  const colors = ref({
    // Fallback colors to prevent errors before mount
    positive: '#16a34a',
    negative: '#dc2626',
    neutral: '#3b82f6',
    surfaceSecondary: '#E5E7EB',
    textTertiary: '#9CA3AF'
  });

  onMounted(() => {
    try {
      const style = getComputedStyle(document.documentElement);
      const fetchedColors = {
        positive: style.getPropertyValue('--semantic-color-feedback-positive-text').trim(),
        negative: style.getPropertyValue('--semantic-color-feedback-negative-text').trim(),
        neutral: style.getPropertyValue('--semantic-color-text-interactive').trim(),
        surfaceSecondary: style.getPropertyValue('--semantic-color-surface-secondary').trim(),
        textTertiary: style.getPropertyValue('--semantic-color-text-tertiary').trim()
      };

      // Assicuriamoci che i colori siano stati effettivamente caricati prima di aggiornare
      if (fetchedColors.positive) {
        colors.value = fetchedColors;
      }
    } catch (error) {
      console.error('Failed to fetch chart colors from CSS variables:', error);
      // In caso di errore, i colori di fallback verranno utilizzati.
    } finally {
      isReady.value = true;
    }
  });

  return {
    colors,
    isReady,
  };
}
