<script setup>
import { computed } from 'vue';
import { useUiStore } from '@/stores/uiStore';
import { useTradesStore } from '@/stores/trades';
import BaseModal from '@/components/ui/BaseModal.vue';
import BaseButton from '@/components/ui/BaseButton.vue';
import IconButton from '@/components/ui/IconButton.vue';
import SparkleIcon from '@/components/icons/SparkleIcon.vue';
import DailyPnlChart from './DailyPnlChart.vue';
import BasePill from '@/components/ui/BasePill.vue';
import BaseTable from '@/components/ui/BaseTable.vue'; // Import BaseTable

const uiStore = useUiStore();
const tradesStore = useTradesStore();

const dailyData = computed(() => {
  if (!uiStore.selectedDate) return null;
  return tradesStore.getDailySummary(uiStore.selectedDate);
});

const handleClose = () => {
  uiStore.closeDailySummaryModal();
};

const pnlStyle = (pnl) => {
  if (pnl > 0) return { color: 'var(--semantic-color-feedback-positive-text)' };
  if (pnl < 0) return { color: 'var(--semantic-color-feedback-negative-text)' };
  return {};
};

const formattedDate = computed(() => {
  if (!dailyData.value) return '';
  const date = new Date(dailyData.value.date + 'T00:00:00');
  return date.toLocaleDateString('en-US', { weekday: 'short', month: 'short', day: 'numeric', year: 'numeric' });
});

const formattedPnl = (pnl) => {
    if (pnl === null || pnl === undefined) return '$0.00';
    const sign = pnl >= 0 ? '+' : '-';
    return `${sign}$${Math.abs(pnl).toFixed(2)}`;
};

const statsGrid = computed(() => {
    if (!dailyData.value) return null;
    const stats = dailyData.value.stats;
    return {
        col1: [ { label: 'Total Trades', value: stats.tradeCount }, { label: 'Winrate', value: `${(stats.winningTrades / (stats.tradeCount || 1) * 100).toFixed(1)}%` }, ],
        col2: [ { label: 'Winners', value: stats.winningTrades }, { label: 'Losers', value: stats.losingTrades }, ],
        col3: [
          { label: 'Gross P&L', value: formattedPnl(stats.pnlAfterCommission), rawValue: stats.pnlAfterCommission, isPnl: true },
          { label: 'Volume', value: stats.totalVolume },
        ],
        col4: [ { label: 'Commissions', value: `$${stats.totalCommission.toFixed(2)}` }, { label: 'Profit Factor', value: stats.profitFactor.toFixed(2) }, ]
    };
});

const tradeTableHeaders = computed(() => [
    { key: 'openTime', text: 'Open Time' }, { key: 'ticker', text: 'Ticker' }, { key: 'type', text: 'Side' }, { key: 'instrument', text: 'Instrument' },
    { key: 'pnl', text: 'Net P&L' }, { key: 'netROI', text: 'Net ROI' }, { key: 'rMultiple', text: 'Realized R' }, { key: 'playbook', text: 'Playbook' },
    { key: 'ticks', text: 'Ticks' }, { key: 'bestExit', text: 'Best Exit' }, { key: 'commission', text: 'Commission' },
]);
</script>

<template>
  <BaseModal
    :show="uiStore.isDailySummaryModalOpen"
    @close="handleClose"
    :show-close-button="false"
    class="daily-summary-modal"
  >
    <template #header>
      <div class="header-content">
        <div class="header-left">
          <div class="header-info">
            <span class="date">{{ formattedDate }}</span>
            <span :style="pnlStyle(dailyData?.stats.netPnl)">Net P&L {{ formattedPnl(dailyData?.stats.netPnl) }}</span>
          </div>
          <BaseButton variant="secondary" size="small">Add Note</BaseButton>
        </div>
        <div class="header-right">
          <IconButton aria-label="AI Assistant" size="small"><SparkleIcon /></IconButton>
        </div>
      </div>
    </template>

    <template #default>
      <div v-if="dailyData" class="modal-body-content">
        <div class="top-section">
          <div class="chart-section"><DailyPnlChart :chart-data="dailyData.cumulativePnlForChart" /></div>
          <div class="stats-section">
            <div class="stat-col" v-for="col in statsGrid" :key="col[0].label">
                <div v-for="stat in col" :key="stat.label" class="stat-cell">
                    <span class="stat-label">{{ stat.label }}</span>
                    <span v-if="stat.isPnl" class="stat-value" :style="pnlStyle(stat.rawValue)">{{ stat.value }}</span>
                    <span v-else class="stat-value">{{ stat.value }}</span>
                </div>
            </div>
          </div>
        </div>

        <div class="table-wrapper">
          <BaseTable :headers="tradeTableHeaders" :items="dailyData.trades" size="x-small">
            <template #pnl="{ item }">
              <span :style="pnlStyle(item.pnl)">{{ formattedPnl(item.pnl) }}</span>
            </template>
            <template #playbook="{ item }">
              <BasePill>{{ item.strategy }}</BasePill>
            </template>
             <template #netROI="{ item }">
              {{ item.netROI.toFixed(2) }}%
            </template>
             <template #rMultiple="{ item }">
              {{ item.rMultiple.toFixed(2) }}
            </template>
             <template #bestExit="{ item }">
              {{ item.bestExit.toFixed(2) }}
            </template>
             <template #commission="{ item }">
              ${{ item.commission.toFixed(2) }}
            </template>
          </BaseTable>
        </div>
      </div>
       <div v-else class="loading-state">Loading data...</div>
    </template>

    <template #footer>
      <div class="footer-content">
        <BaseButton variant="secondary" size="small" @click="handleClose">Cancel</BaseButton>
        <BaseButton variant="primary" size="small">View Details</BaseButton>
      </div>
    </template>
  </BaseModal>
</template>

<style scoped>
/* --- Mobile First Styles --- */

/* Header Styles */
.header-content {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  width: 100%;
  flex-wrap: wrap;
  gap: var(--semantic-size-stack-sm);
}
.header-left { display: flex; align-items: center; gap: var(--semantic-size-stack-sm); }
.header-info { display: flex; flex-direction: column; }
.date { font: var(--semantic-font-style-body-sm); color: var(--semantic-color-text-secondary); }
.header-info > span:last-child { font: var(--semantic-font-style-heading-sm); font-weight: 600; }
.header-right { display: flex; align-items: center; gap: var(--base-size-spacing-2); flex-shrink: 0; }

/* Body Styles */
.modal-body-content { display: flex; flex-direction: column; gap: var(--semantic-size-stack-md); flex-grow: 1; min-height: 0; }
.top-section { display: flex; flex-direction: column; gap: var(--semantic-size-stack-md); }
.chart-section { min-height: 150px; }

/* Stats Section Styles */
.stats-section {
  display: grid;
  grid-template-columns: 1fr 1fr; /* 2 columns for mobile */
  border: var(--base-border-width-1) solid var(--semantic-color-border-default);
  border-radius: var(--semantic-border-radius-surface);
  overflow: hidden;
}
.stat-col {
  display: flex;
  flex-direction: column;
  gap: var(--semantic-size-stack-sm);
  padding: var(--semantic-size-inset-sm);
}
/* Add borders to create a grid visually */
.stat-col:nth-child(odd) {
  border-right: var(--base-border-width-1) solid var(--semantic-color-border-default);
}
.stat-col:nth-child(1), .stat-col:nth-child(2) {
  border-bottom: var(--base-border-width-1) solid var(--semantic-color-border-default);
}

.stat-cell { display: flex; flex-direction: column; gap: var(--base-size-spacing-0-5); }
.stat-label { font: var(--semantic-font-style-label-sm); color: var(--semantic-color-text-secondary); }
.stat-value { font: var(--semantic-font-style-body-sm); color: var(--semantic-color-text-primary); font-weight: 600; }
.loading-state { text-align: center; padding: var(--semantic-size-inset-xl); color: var(--semantic-color-text-secondary); }

/* Table Styles */
.table-wrapper {
  flex-grow: 1;
  min-height: 0; /* Important for vertical scrolling in flex */
}

/* Footer Styles */
.footer-content {
  width: 100%;
  display: flex;
  justify-content: flex-end;
  gap: var(--semantic-size-gap-sm);
  padding-top: var(--semantic-size-inset-md);
  border-top: var(--base-border-width-1) solid var(--semantic-color-border-default);
}


/* --- Tablet & Desktop Overrides --- */
@media (min-width: 768px) {
  .modal-body-content {
    gap: var(--semantic-size-stack-lg);
  }
  .top-section {
    display: grid;
    grid-template-columns: 1fr 1.5fr;
    gap: var(--semantic-size-stack-xl);
    flex-direction: row; /* Revert to row for grid */
  }
  .stats-section {
    grid-template-columns: repeat(4, 1fr);
    border-left: var(--base-border-width-1) solid var(--semantic-color-border-default);
    border-top: none;
    border-right: none;
    border-bottom: none;
    border-radius: 0;
  }
  .stat-col {
    gap: var(--semantic-size-stack-lg);
    padding: 0 var(--semantic-size-inset-lg);
    border-right: var(--base-border-width-1) solid var(--semantic-color-border-default);
    border-bottom: none;
  }
  .stat-col:nth-child(odd) {
    border-right: var(--base-border-width-1) solid var(--semantic-color-border-default);
  }
  .stat-col:last-child {
    border-right: none;
  }
  .stat-col:nth-child(1), .stat-col:nth-child(2) {
    border-bottom: none;
  }
  .table-wrapper {
    min-width: 0; /* Fix for horizontal scrolling in flex */
    overflow-x: auto;
  }
}
</style>
