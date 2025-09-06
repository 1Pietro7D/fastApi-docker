<script setup>
import { useUiStore } from '../../stores/uiStore';
import BaseCheckbox from '../ui/BaseCheckbox.vue';
import { useMediaQuery } from '@vueuse/core';
import { watch } from 'vue';

const uiStore = useUiStore();
const isDesktop = useMediaQuery('(min-width: 769px)');

// Quando si passa alla visuale mobile, disattiviamo le opzioni non disponibili
watch(isDesktop, (isNowDesktop) => {
  if (!isNowDesktop) {
    if (uiStore.isWeeklySummaryVisible) {
      uiStore.toggleWeeklySummary();
    }
    if (uiStore.isCalendarWinRateVisible) {
      uiStore.toggleCalendarWinRate();
    }
  }
});

// Non c'è bisogno di una funzione handler separata,
// possiamo chiamare l'azione dello store direttamente dal template.
</script>

<template>
  <div class="settings-menu">
    <h4 class="settings-title">Calendar Settings</h4>
    <div class="settings-list">
      <template v-if="isDesktop">
        <div class="settings-item">
          <BaseCheckbox
            label="Show Weekly Summary"
            :model-value="uiStore.isWeeklySummaryVisible"
            @update:modelValue="uiStore.toggleWeeklySummary()"
          />
        </div>
      </template>
      <div class="settings-item">
        <BaseCheckbox
          label="Show Trade Count"
          :model-value="uiStore.isCalendarTradeCountVisible"
          @update:modelValue="uiStore.toggleCalendarTradeCount()"
        />
      </div>
      <template v-if="isDesktop">
        <div class="settings-item">
          <BaseCheckbox
            label="Show Win Rate %"
            :model-value="uiStore.isCalendarWinRateVisible"
            @update:modelValue="uiStore.toggleCalendarWinRate()"
          />
        </div>
      </template>
    </div>
  </div>
</template>

<style scoped>
.settings-menu {
  display: flex;
  flex-direction: column;
  gap: var(--semantic-size-stack-sm);
  padding: var(--base-size-spacing-2);
}
.settings-title {
  font: var(--semantic-font-style-label-md);
  color: var(--semantic-color-text-tertiary);
  margin-bottom: var(--base-size-spacing-1);
}
.settings-list {
  display: flex;
  flex-direction: column;
  gap: var(--semantic-size-stack-sm);
}
</style>
