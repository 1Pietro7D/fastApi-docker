// =============================================================================
// FILE: stores/uiStore.js
// DESCRIZIONE: Questo store Pinia gestisce lo stato generale dell'interfaccia
// utente (UI) che non è legato a dati specifici di business (come i trade).
// Esempi includono lo stato di apertura/chiusura di modali, sidebar, etc.
// =============================================================================

import { defineStore } from 'pinia';
import { ref, watch } from 'vue';
import { useMediaQuery } from '@vueuse/core';
import breakpointTokens from '../../tokens/base/layout/breakpoint.json';

// Definiamo lo store usando la sintassi "Setup Store"
export const useUiStore = defineStore('ui', () => {

  // --- STATO (State) ---
  const isSidebarCollapsed = ref(false);
  const isMobileMenuOpen = ref(false);
  const visibleStatKeys = ref(['netPnl', 'winRate', 'profitFactor', 'trades', 'avgWin']);
  const isWeeklySummaryVisible = ref(true);
  const isCalendarTradeCountVisible = ref(true);
  const isCalendarWinRateVisible = ref(true);

  // --- LOGICA RESPONSIVE ---
  /*
    BEST PRACTICE: Sincronizzazione JS e CSS tramite Token
    Per la logica responsiva in JavaScript (es. per sapere se siamo su mobile),
    è fondamentale usare la stessa identica soglia (breakpoint) del nostro CSS.
    Invece di scrivere un valore fisso (es. 768px), importiamo direttamente il
    file JSON dei token e usiamo il valore del breakpoint `md`.
    Questo garantisce che se un giorno modificheremo il token, la logica JS
    si aggiornerà automaticamente insieme al CSS.
  */
  const isMobile = useMediaQuery(`(max-width: ${breakpointTokens.base.layout.breakpoint.md.$value})`);

  // Chiudiamo automaticamente il menu mobile se l'utente allarga la finestra
  // passando dalla visuale mobile a quella desktop.
  watch(isMobile, (isNowMobile) => {
    if (!isNowMobile && isMobileMenuOpen.value) {
      closeMobileMenu();
    }
  });


  // --- AZIONI (Actions) ---

  function toggleWeeklySummary() {
    isWeeklySummaryVisible.value = !isWeeklySummaryVisible.value;
  }

  function toggleCalendarTradeCount() {
    isCalendarTradeCountVisible.value = !isCalendarTradeCountVisible.value;
  }

  function toggleCalendarWinRate() {
    isCalendarWinRateVisible.value = !isCalendarWinRateVisible.value;
  }

  function toggleSidebar() {
    // La sidebar collassabile funziona solo su schermi grandi.
    if (!isMobile.value) {
      isSidebarCollapsed.value = !isSidebarCollapsed.value;
    }
  }

  function toggleMobileMenu() {
    isMobileMenuOpen.value = !isMobileMenuOpen.value;
  }

  function closeMobileMenu() {
    isMobileMenuOpen.value = false;
  }

  function toggleStatVisibility(key) {
    const index = visibleStatKeys.value.indexOf(key);
    if (index === -1) {
      visibleStatKeys.value.push(key);
    } else {
      visibleStatKeys.value.splice(index, 1);
    }
  }

  // --- STATO E AZIONI PER I MODALI ---
  const isDailySummaryModalOpen = ref(false);
  const selectedDate = ref(null);
  const isWeeklySummaryModalOpen = ref(false);
  const selectedWeekIndex = ref(null);
  // Salviamo lo stato della sidebar prima di aprire un modale
  let sidebarStateBeforeModal = false;

  function openDailySummaryModal(date) {
    selectedDate.value = date;
    isDailySummaryModalOpen.value = true;
    // Quando apriamo un modale, collassiamo la sidebar se siamo su desktop.
    if (!isMobile.value) {
      sidebarStateBeforeModal = isSidebarCollapsed.value;
      isSidebarCollapsed.value = true;
    }
  }

  function closeDailySummaryModal() {
    isDailySummaryModalOpen.value = false;
    selectedDate.value = null;
    // Ripristiniamo lo stato della sidebar
    if (!isMobile.value) {
      isSidebarCollapsed.value = sidebarStateBeforeModal;
    }
  }

  function openWeeklySummaryModal(weekIndex) {
    selectedWeekIndex.value = weekIndex;
    isWeeklySummaryModalOpen.value = true;
    // Quando apriamo un modale, collassiamo la sidebar se siamo su desktop.
    if (!isMobile.value) {
      sidebarStateBeforeModal = isSidebarCollapsed.value;
      isSidebarCollapsed.value = true;
    }
  }

  function closeWeeklySummaryModal() {
    isWeeklySummaryModalOpen.value = false;
    selectedWeekIndex.value = null;
    // Ripristiniamo lo stato della sidebar
    if (!isMobile.value) {
      isSidebarCollapsed.value = sidebarStateBeforeModal;
    }
  }


  // --- ESPORTAZIONE ---
  return {
    isSidebarCollapsed,
    isMobileMenuOpen,
    isMobile, // Esportiamo lo stato reattivo
    visibleStatKeys,
    isWeeklySummaryVisible,
    isCalendarTradeCountVisible,
    isCalendarWinRateVisible,
    isDailySummaryModalOpen,
    selectedDate,
    isWeeklySummaryModalOpen,
    selectedWeekIndex,

    toggleSidebar,
    toggleMobileMenu,
    closeMobileMenu,
    toggleStatVisibility,
    toggleWeeklySummary,
    toggleCalendarTradeCount,
    toggleCalendarWinRate,
    openDailySummaryModal,
    closeDailySummaryModal,
    openWeeklySummaryModal,
    closeWeeklySummaryModal,
  };
});
