<!--
// =============================================================================
// FILE: components/layout/DashboardHeader.vue
// DESCRIZIONE: Header finale con logica responsive migliorata per i filtri.
// Le azioni sono state spostate in DashboardView.
// =============================================================================
-->
<script setup>
import { useMediaQuery } from '@vueuse/core';
import HamburgerButton from '../ui/HamburgerButton.vue';
import DropdownButton from '../ui/DropdownButton.vue';
import StrategyFilter from '../dashboard/StrategyFilter.vue';
import DateRangeFilter from '../dashboard/DateRangeFilter.vue';
import { useUiStore } from '../../stores/uiStore';

// Import the icon components
import FilterIcon from '../icons/FilterIcon.vue';
import CalendarIcon from '../icons/CalendarIcon.vue';

const uiStore = useUiStore();

defineProps({
  title: {
    type: String,
    required: true,
  },
});

// Logica responsive con VueUse
const isDesktop = useMediaQuery('(min-width: 769px)');
</script>

<template>
  <header class="header">
    <div class="header-left">
      <HamburgerButton class="hamburger-menu" :is-open="uiStore.isMobileMenuOpen" @toggle="uiStore.toggleMobileMenu" />
      <h1 class="title">{{ title }}</h1>
    </div>

    <div class="header-right">
      <!-- Filtri per Desktop (v-if) -->
      <div v-if="isDesktop" class="header-controls">
        <DropdownButton>
          <template #icon><FilterIcon /></template>
          <template #text>Strategy</template>
          <template #content><StrategyFilter /></template>
        </DropdownButton>
        <DropdownButton>
          <template #icon><CalendarIcon /></template>
          <template #text>Date Range</template>
          <template #content><DateRangeFilter /></template>
        </DropdownButton>
      </div>

      <!-- Filtro unificato per Mobile (v-else) -->
      <div v-else class="header-controls">
        <DropdownButton>
          <template #icon><FilterIcon /></template>
          <template #text>Filters</template>
          <template #content>
            <div class="mobile-filters">
              <StrategyFilter />
              <DateRangeFilter />
            </div>
          </template>
        </DropdownButton>
      </div>
    </div>
  </header>
</template>

<style scoped>
.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: var(--semantic-size-stack-md);
  /* Il padding è ora gestito completamente dal contenitore MainLayout */
}
.header-left, .header-right, .header-controls {
  display: flex;
  align-items: center;
  gap: var(--semantic-size-stack-sm);
}

.title {
  font: var(--semantic-font-style-heading-2xl);
  color: var(--semantic-color-text-primary);
}

.mobile-filters {
  display: flex;
  flex-direction: column;
  gap: var(--semantic-size-stack-md);
}

/* --- RESPONSIVE VISIBILITY --- */
.hamburger-menu {
  display: none;
}

/* Tablet and below */
@media (max-width: 768px) {
  .hamburger-menu {
    display: flex;
  }
  .title {
    font: var(--semantic-font-style-heading-xl);
  }
}
</style>
