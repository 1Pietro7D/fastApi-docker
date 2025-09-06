// =============================================================================
// FILE: stores/trades.js
// DESCRIZIONE: Store dei trade, refattorizzato per massima efficienza.
// =============================================================================

import { defineStore } from 'pinia';
import { useFilterStore } from './filterStore';

export const useTradesStore = defineStore('trades', {
  state: () => ({
    trades: [
      // Dati di esempio con i nuovi campi
      { id: 1, ticker: 'AAPL', type: 'Long', pnl: 150.75, date: '2025-08-28', strategy: 'Breakout', risk: 50, openTime: '09:30:15', instrument: 'Stocks', commission: 4.50, netROI: 1.5, rMultiple: 3.01, ticks: 60, bestExit: 151.00, volume: 100 },
      { id: 2, ticker: 'TSLA', type: 'Short', pnl: -75.20, date: '2025-08-28', strategy: 'Reversal', risk: 50, openTime: '10:05:40', instrument: 'Stocks', commission: 4.50, netROI: -0.75, rMultiple: -1.50, ticks: -30, bestExit: 249.50, volume: 50 },
      { id: 3, ticker: 'NVDA', type: 'Long', pnl: 278.40, date: '2025-08-27', strategy: 'Breakout', risk: 100, openTime: '11:15:00', instrument: 'Stocks', commission: 6.20, netROI: 1.39, rMultiple: 2.78, ticks: 110, bestExit: 450.00, volume: 200 },
      { id: 4, ticker: 'GOOG', type: 'Long', pnl: 121.00, date: '2025-08-20', strategy: 'Momentum', risk: 60, openTime: '14:00:05', instrument: 'Stocks', commission: 3.80, netROI: 1.0, rMultiple: 2.01, ticks: 48, bestExit: 135.00, volume: 75 },
      { id: 5, ticker: 'MSFT', type: 'Long', pnl: 88.50, date: '2025-08-28', strategy: 'Reversal', risk: 40, openTime: '14:30:00', instrument: 'Stocks', commission: 4.50, netROI: 1.1, rMultiple: 2.21, ticks: 35, bestExit: 330.00, volume: 150 },
      { id: 6, ticker: 'AMD', type: 'Short', pnl: -42.10, date: '2025-08-10', strategy: 'Breakout', risk: 40, openTime: '09:45:10', instrument: 'Stocks', commission: 2.10, netROI: -0.52, rMultiple: -1.05, ticks: -21, bestExit: 109.00, volume: 100 },
      { id: 7, ticker: 'META', type: 'Long', pnl: 210.00, date: '2025-07-30', strategy: 'Momentum', risk: 70, openTime: '10:10:10', instrument: 'Stocks', commission: 5.00, netROI: 1.5, rMultiple: 3.00, ticks: 84, bestExit: 315.00, volume: 50 },
    ],
  }),

  getters: {
    allStrategies(state) {
      const strategies = new Set(state.trades.map(trade => trade.strategy).filter(Boolean));
      return ['All', ...Array.from(strategies)];
    },

    filteredTrades: (state) => {
      const filterStore = useFilterStore();
      let trades = state.trades;
      if (filterStore.startDate && filterStore.endDate) {
        const start = new Date(filterStore.startDate).setHours(0, 0, 0, 0);
        const end = new Date(filterStore.endDate).setHours(23, 59, 59, 999);
        trades = trades.filter(trade => {
          const tradeDate = new Date(trade.date);
          return tradeDate >= start && tradeDate <= end;
        });
      }
      if (filterStore.selectedStrategy && filterStore.selectedStrategy !== 'all') {
        trades = trades.filter(trade => trade.strategy === filterStore.selectedStrategy);
      }
      return trades;
    },

    processedData(state) {
      const trades = this.filteredTrades;
      const filterStore = useFilterStore();
      const viewDateForCalendar = new Date(filterStore.endDate);

      const stats = { totalPnl: 0, tradeCount: 0, winningTrades: 0, losingTrades: 0, breakEvenTrades: 0, grossProfit: 0, grossLoss: 0, totalRisk: 0 };
      const dailyDataForCalendar = {};
      const performanceByStrategy = {};
      const performanceByDayOfWeek = {};
      const pnlByDay = {};
      const daysOfWeek = ['Domenica', 'Lunedì', 'Martedì', 'Mercoledì', 'Giovedì', 'Venerdì', 'Sabato'];
      daysOfWeek.forEach(day => {
        performanceByDayOfWeek[day] = { totalPnl: 0, tradeCount: 0, winningTrades: 0 };
      });

      for (const trade of trades) {
        stats.totalPnl += trade.pnl;
        stats.tradeCount++;
        stats.totalRisk += trade.risk;
        if (trade.pnl > 0) {
          stats.winningTrades++;
          stats.grossProfit += trade.pnl;
        } else if (trade.pnl < 0) {
          stats.losingTrades++;
          stats.grossLoss += Math.abs(trade.pnl);
        } else {
          stats.breakEvenTrades++;
        }

        const tradeDate = new Date(trade.date);
        const dayKey = tradeDate.toISOString().split('T')[0];

        if (!pnlByDay[dayKey]) pnlByDay[dayKey] = 0;
        pnlByDay[dayKey] += trade.pnl;

        if (tradeDate.getFullYear() === viewDateForCalendar.getFullYear() && tradeDate.getMonth() === viewDateForCalendar.getMonth()) {
          if (!dailyDataForCalendar[dayKey]) {
            dailyDataForCalendar[dayKey] = { totalPnl: 0, tradeCount: 0, winningTrades: 0 };
          }
          dailyDataForCalendar[dayKey].totalPnl += trade.pnl;
          dailyDataForCalendar[dayKey].tradeCount++;
          if (trade.pnl > 0) dailyDataForCalendar[dayKey].winningTrades++;
        }

        if (trade.strategy) {
          if (!performanceByStrategy[trade.strategy]) {
            performanceByStrategy[trade.strategy] = { totalPnl: 0, tradeCount: 0, winningTrades: 0 };
          }
          performanceByStrategy[trade.strategy].totalPnl += trade.pnl;
          performanceByStrategy[trade.strategy].tradeCount++;
          if (trade.pnl > 0) performanceByStrategy[trade.strategy].winningTrades++;
        }

        const dayName = daysOfWeek[tradeDate.getDay()];
        performanceByDayOfWeek[dayName].totalPnl += trade.pnl;
        performanceByDayOfWeek[dayName].tradeCount++;
        if (trade.pnl > 0) performanceByDayOfWeek[dayName].winningTrades++;
      }

      const winLossDaysStats = { winningDays: 0, losingDays: 0, breakEvenDays: 0 };
      for (const dayPnl of Object.values(pnlByDay)) {
        if (dayPnl > 0) winLossDaysStats.winningDays++;
        else if (dayPnl < 0) winLossDaysStats.losingDays++;
        else winLossDaysStats.breakEvenDays++;
      }

      return { stats, dailyDataForCalendar, performanceByStrategy, performanceByDayOfWeek, winLossDaysStats, recentTrades: trades.slice(0, 4) };
    },

    recentTrades() {
      return this.processedData.recentTrades;
    },

    allDashboardStats() {
      const { stats } = this.processedData;
      const { totalPnl, tradeCount, winningTrades, losingTrades, breakEvenTrades, grossProfit, grossLoss } = stats;

      if (tradeCount === 0) {
        return {
          netPnl: { key: 'netPnl', label: 'Net P&L', value: '$0.00', changeType: 'neutral' },
          winRate: { key: 'winRate', label: 'Win Rate', value: 'N/A', wins: 0, losses: 0, breakevens: 0, changeType: 'neutral' },
          trades: { key: 'trades', label: 'Trades', value: '0', changeType: 'neutral' },
          profitFactor: { key: 'profitFactor', label: 'Profit Factor', value: 'N/A', changeType: 'neutral' },
          avgWin: { key: 'avgWin', label: 'Avg. Win', value: '$0.00', changeType: 'neutral' },
          avgLoss: { key: 'avgLoss', label: 'Avg. Loss', value: '$0.00', changeType: 'neutral' },
          expectancy: { key: 'expectancy', label: 'Expectancy', value: '$0.00', changeType: 'neutral' },
        };
      }

      const winRate = (winningTrades / tradeCount) * 100;
      const lossRate = 1 - (winRate / 100);
      const profitFactor = grossLoss > 0 ? grossProfit / grossLoss : Infinity;
      const avgWin = winningTrades > 0 ? grossProfit / winningTrades : 0;
      const avgLoss = (tradeCount - winningTrades) > 0 ? grossLoss / (tradeCount - winningTrades) : 0;
      const expectancy = (winRate / 100 * avgWin) - (lossRate * avgLoss);

      return {
        netPnl: { key: 'netPnl', label: 'Net P&L', value: `${totalPnl >= 0 ? '+' : ''}$${totalPnl.toFixed(2)}`, changeType: totalPnl >= 0 ? 'positive' : 'negative' },
        winRate: { key: 'winRate', label: 'Win Rate', value: `${winRate.toFixed(1)}%`, wins: winningTrades, losses: losingTrades, breakevens: breakEvenTrades, changeType: 'positive' },
        trades: { key: 'trades', label: 'Trades', value: String(tradeCount), changeType: 'neutral' },
        profitFactor: { key: 'profitFactor', label: 'Profit Factor', value: profitFactor === Infinity ? '∞' : profitFactor.toFixed(2), changeType: profitFactor > 1 ? 'positive' : 'negative' },
        avgWin: { key: 'avgWin', label: 'Avg. Win', value: `$${avgWin.toFixed(2)}`, changeType: 'positive' },
        avgLoss: { key: 'avgLoss', label: 'Avg. Loss', value: `$${avgLoss.toFixed(2)}`, changeType: 'negative' },
        expectancy: { key: 'expectancy', label: 'Expectancy', value: `$${expectancy.toFixed(2)}`, changeType: expectancy > 0 ? 'positive' : 'negative' },
      };
    },

    getDailySummary(state) {
      return (date) => {
        if (!date) return null;

        const dailyTrades = state.trades.filter(t => t.date === date);
        const sortedDailyTrades = [...dailyTrades].sort((a, b) => a.id - b.id);

        const summary = {
          date,
          trades: sortedDailyTrades,
          stats: { netPnl: 0, tradeCount: 0, winningTrades: 0, losingTrades: 0, totalCommission: 0, profitFactor: 0, grossProfit: 0, totalVolume: 0 },
          cumulativePnlForChart: { labels: ['Start'], data: [0] }
        };

        if (dailyTrades.length === 0) return summary;

        let grossLoss = 0;
        let cumulativePnl = 0;

        for (const trade of sortedDailyTrades) {
          summary.stats.netPnl += trade.pnl;
          summary.stats.tradeCount++;
          summary.stats.totalCommission += trade.commission;
          summary.stats.totalVolume += trade.volume;

          if (trade.pnl > 0) {
            summary.stats.winningTrades++;
            summary.stats.grossProfit += trade.pnl;
          } else if (trade.pnl < 0) {
            summary.stats.losingTrades++;
            grossLoss += Math.abs(trade.pnl);
          }

          cumulativePnl += trade.pnl;
          summary.cumulativePnlForChart.data.push(cumulativePnl);
          summary.cumulativePnlForChart.labels.push(trade.ticker);
        }

        summary.stats.profitFactor = grossLoss > 0 ? summary.stats.grossProfit / grossLoss : (summary.stats.grossProfit > 0 ? Infinity : 0);
        summary.stats.pnlAfterCommission = summary.stats.netPnl - summary.stats.totalCommission;

        return summary;
      };
    },

    getWeeklySummaryDetails(state) {
      return (weekIndex) => {
        if (weekIndex === null || weekIndex === undefined) return null;

        const weekData = this.calendarDataByMonth.weeksOfDays[weekIndex];
        if (!weekData) return null;

        const weekDates = weekData.filter(day => !day.isPlaceholder).map(day => day.fullDate);
        const weeklyTrades = state.trades.filter(t => weekDates.includes(t.date));
        const sortedWeeklyTrades = [...weeklyTrades].sort((a, b) => new Date(a.date) - new Date(b.date) || a.id - b.id);

        const startDate = weekDates[0];
        const endDate = weekDates[weekDates.length - 1];

        const summary = {
          startDate,
          endDate,
          trades: sortedWeeklyTrades,
          stats: { netPnl: 0, tradeCount: 0, winningTrades: 0, losingTrades: 0, totalCommission: 0, profitFactor: 0, grossProfit: 0, totalVolume: 0 },
          cumulativePnlForChart: { labels: ['Start'], data: [0] }
        };

        if (weeklyTrades.length === 0) return summary;

        let grossLoss = 0;
        let cumulativePnl = 0;

        for (const trade of sortedWeeklyTrades) {
          summary.stats.netPnl += trade.pnl;
          summary.stats.tradeCount++;
          summary.stats.totalCommission += trade.commission;
          summary.stats.totalVolume += trade.volume;

          if (trade.pnl > 0) {
            summary.stats.winningTrades++;
            summary.stats.grossProfit += trade.pnl;
          } else if (trade.pnl < 0) {
            summary.stats.losingTrades++;
            grossLoss += Math.abs(trade.pnl);
          }

          cumulativePnl += trade.pnl;
          summary.cumulativePnlForChart.data.push(cumulativePnl);
          summary.cumulativePnlForChart.labels.push(`${trade.date.split('-')[2]} - ${trade.ticker}`);
        }

        summary.stats.profitFactor = grossLoss > 0 ? summary.stats.grossProfit / grossLoss : (summary.stats.grossProfit > 0 ? Infinity : 0);
        summary.stats.pnlAfterCommission = summary.stats.netPnl - summary.stats.totalCommission;

        return summary;
      };
    },

    calendarDataByMonth() {
      const { dailyDataForCalendar } = this.processedData;
      const filterStore = useFilterStore();
      const viewDate = new Date(filterStore.endDate);
      const year = viewDate.getFullYear();
      const month = viewDate.getMonth();

      const daysInMonth = new Date(year, month + 1, 0).getDate();
      const firstDayOfWeek = new Date(year, month, 1).getDay();
      const calendarDays = [];
      const offset = (firstDayOfWeek === 0) ? 6 : firstDayOfWeek - 1;
      for (let i = 0; i < offset; i++) {
        calendarDays.push({ isPlaceholder: true, key: `ph-start-${i}` });
      }

      for (let i = 1; i <= daysInMonth; i++) {
        const dateStr = `${year}-${String(month + 1).padStart(2, '0')}-${String(i).padStart(2, '0')}`;
        calendarDays.push({
          date: i,
          fullDate: dateStr,
          dailyData: dailyDataForCalendar[dateStr] || { totalPnl: 0, tradeCount: 0, winningTrades: 0 },
          isPlaceholder: false,
          key: dateStr,
        });
      }

      while (calendarDays.length % 7 !== 0) {
        calendarDays.push({ isPlaceholder: true, key: `ph-end-${calendarDays.length}` });
      }

      const weeksOfDays = [];
      const weeklySummaries = [];
      for (let i = 0; i < calendarDays.length; i += 7) {
        const weekChunk = calendarDays.slice(i, i + 7);
        weeksOfDays.push(weekChunk);

        const weeklyPnl = weekChunk.reduce((sum, day) => sum + (day.dailyData?.totalPnl || 0), 0);
        const tradingDaysCount = weekChunk.filter(day => !day.isPlaceholder && day.dailyData.tradeCount > 0).length;

        weeklySummaries.push({
          weekNumber: (i / 7) + 1,
          totalPnl: weeklyPnl,
          tradingDaysCount: tradingDaysCount,
        });
      }

      return { weeksOfDays, weeklySummaries };
    },

    strategyPerformanceData() {
      const rawData = this.processedData.performanceByStrategy;
      if (Object.keys(rawData).length === 0) return [];
      const maxPnl = Math.max(...Object.values(rawData).map(stat => Math.abs(stat.totalPnl)));
      return Object.entries(rawData).map(([strategy, stats]) => {
        const winRate = stats.tradeCount > 0 ? (stats.winningTrades / stats.tradeCount) * 100 : 0;
        return {
          label: strategy,
          value: `${stats.tradeCount} trades | ${winRate.toFixed(0)}% WR | $${stats.totalPnl.toFixed(2)}`,
          barWidth: maxPnl > 0 ? `${(Math.abs(stats.totalPnl) / maxPnl) * 100}%` : '0%',
          isPositive: stats.totalPnl >= 0,
        };
      });
    },

    performanceByDayOfWeek() {
        return this.processedData.performanceByDayOfWeek;
    },

    winLossDays(state) {
      if (!this.processedData.winLossDaysStats) {
        return { winningDays: 0, losingDays: 0, breakEvenDays: 0 };
      }
      return this.processedData.winLossDaysStats;
    },

    equityCurveData(state) {
      if (this.filteredTrades.length === 0) return { labels: [], data: [] };
      const sortedTrades = [...this.filteredTrades].sort((a, b) => new Date(a.date) - new Date(b.date));
      let cumulativePnl = 0;
      const dataPoints = sortedTrades.map(trade => {
        cumulativePnl += trade.pnl;
        return { date: trade.date, pnl: cumulativePnl };
      });
      return { labels: dataPoints.map(p => p.date), data: dataPoints.map(p => p.pnl) };
    },

    tradeHeaders: () => [
      { key: 'ticker', text: 'Ticker' },
      { key: 'type', text: 'Type' },
      { key: 'pnl', text: 'Net P&L' },
      { key: 'date', text: 'Date' },
    ],

    calendarControlsData() {
      const filterStore = useFilterStore();
      const viewDate = new Date(filterStore.endDate);

      if (isNaN(viewDate.getTime())) return { monthLabel: 'Invalid Date', monthlyPnl: 0 };

      const monthLabel = viewDate.toLocaleString('en-US', { month: 'long', year: 'numeric' });
      let monthlyPnl = 0;
      for (const trade of this.filteredTrades) {
        const tradeDate = new Date(trade.date);
        if (tradeDate.getFullYear() === viewDate.getFullYear() && tradeDate.getMonth() === viewDate.getMonth()) {
          monthlyPnl += trade.pnl;
        }
      }
      return { monthLabel, monthlyPnl };
    }
  },

  actions: {
    addTrade(newTrade) {
      const fullTrade = {
        ...newTrade,
        id: Date.now(),
        date: new Date().toISOString().split('T')[0],
        openTime: new Date().toLocaleTimeString(),
        instrument: 'Stocks',
        commission: 5.00,
        netROI: Math.random() * 2,
        rMultiple: Math.random() * 3,
        ticks: Math.floor(Math.random() * 100),
        bestExit: newTrade.pnl * 1.1,
        volume: Math.floor(Math.random() * 1000) + 100,
      };
      this.trades.unshift(fullTrade);
    },
  },
});
