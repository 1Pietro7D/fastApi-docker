# app/Services/metrics/metrics_calculator.py

from decimal import Decimal
import numpy as np
from dateutil.parser import parse
from scipy.stats import skew, kurtosis

class MetricsCalculator:
    def __init__(self, trades):
        self.all_trades = trades
        if self.all_trades:
            self._prepare_trades()

    @staticmethod
    def filter_trades(trades, filters):
        """
        Filtra una lista di trade in base a criteri calcolati che non possono
        essere gestiti a livello di database.
        """
        if not filters:
            return trades

        filtered_trades = []
        for trade in trades:
            # Duration filter
            min_dur, max_dur = filters.get('min_duration'), filters.get('max_duration')
            if (min_dur is not None or max_dur is not None) and trade.get('entry_timestamp') and trade.get('exit_timestamp'):
                duration_minutes = (trade['exit_timestamp'] - trade['entry_timestamp']).total_seconds() / 60
                if (min_dur is not None and duration_minutes < min_dur) or \
                   (max_dur is not None and duration_minutes > max_dur):
                    continue  # Skip trade

            # R-Multiple filter
            min_rr, max_rr = filters.get('min_rr'), filters.get('max_rr')
            if min_rr is not None or max_rr is not None:
                pnl = Decimal(trade.get('p_l') or 0)
                entry = Decimal(trade.get('entry_price') or 0)
                sl = Decimal(trade.get('stop_loss_price') or 0)
                value_per_point = Decimal(trade.get('position_size') or 1)  # Simplified

                potential_risk_points = abs(entry - sl) if entry and sl else Decimal(0)
                if potential_risk_points > 0:
                    initial_dollar_risk = potential_risk_points * value_per_point
                    realized_rr = float(pnl / initial_dollar_risk) if initial_dollar_risk > 0 else 0.0
                    if (min_rr is not None and realized_rr < min_rr) or \
                       (max_rr is not None and realized_rr > max_rr):
                        continue  # Skip trade

            filtered_trades.append(trade)

        return filtered_trades

    def _prepare_trades(self):
        """Pre-calcola MAE/MFE e converte le date per ogni trade."""
        for trade in self.all_trades:
            # Calcolo MAE/MFE
            entry = Decimal(trade.get('entry_price', 0)) if trade.get('entry_price') is not None else Decimal(0)
            lowest = Decimal(trade.get('lowest_price_during_trade', 0)) if trade.get('lowest_price_during_trade') is not None else Decimal(0)
            highest = Decimal(trade.get('highest_price_during_trade', 0)) if trade.get('highest_price_during_trade') is not None else Decimal(0)
            direction = trade.get('direction')
            
            if entry > 0 and lowest > 0 and highest > 0 and direction:
                if direction == 'Long':
                    trade['mae_points'] = float(entry - lowest)
                    trade['mfe_points'] = float(highest - entry)
                elif direction == 'Short':
                    trade['mae_points'] = float(highest - entry)
                    trade['mfe_points'] = float(entry - lowest)
            else:
                trade['mae_points'], trade['mfe_points'] = 0, 0

            # Net ROI
            pnl = Decimal(trade.get('p_l')) if trade.get('p_l') is not None else Decimal('0')
            entry_price = Decimal(trade.get('entry_price')) if trade.get('entry_price') is not None else Decimal('0')
            position_size = Decimal(trade.get('position_size')) if trade.get('position_size') is not None else Decimal('0')
            cost = entry_price * position_size
            trade['net_roi'] = float((pnl / cost) * 100) if cost != 0 else 0.0

            # Conversione date
            if isinstance(trade.get('created_at'), str):
                trade['created_at'] = parse(trade['created_at'])
            if isinstance(trade.get('entry_timestamp'), str):
                 trade['entry_timestamp'] = parse(trade['entry_timestamp'])
            if isinstance(trade.get('exit_timestamp'), str):
                 trade['exit_timestamp'] = parse(trade['exit_timestamp'])

    def _get_empty_response(self):
        """Struttura di default quando non ci sono trade."""
        stats_keys = [
            'total_pl', 'trade_count', 'avg_win', 'avg_loss', 'profit_factor', 'expectancy',
            'avg_sell_efficiency', 'avg_total_efficiency', 'avg_planned_rr', 'avg_realized_rr',
            'max_drawdown_abs', 'max_drawdown_pct', 'sharpe_ratio', 'sortino_ratio',
            'calmar_ratio', 'skewness', 'kurtosis', 'var_95', 'cvar_95'
        ]
        return {
            'trades': [],
            'stats': {key: 0 for key in stats_keys},
            'equity_curve_data': [], 'setup_chart_data': [],
            'r_multiple_data': {'labels': [], 'data': []}
        }

    def _calculate_base_stats(self):
        """Statistiche di base (P&L, win/loss, etc.)."""
        pnl_data = [Decimal(t['p_l']) if t.get('p_l') is not None else Decimal('0') for t in self.all_trades]
        winning_trades_pnl = [pnl for pnl in pnl_data if pnl > 0]
        losing_trades_pnl = [pnl for pnl in pnl_data if pnl < 0]
        breakeven_trades_count = len([pnl for pnl in pnl_data if pnl == 0])
        winning_trades = [t for t in self.all_trades if t.get('p_l') is not None and Decimal(t['p_l']) > 0]

        # Long/Short
        long_wins = long_losses = long_be = 0
        short_wins = short_losses = short_be = 0
        for trade in self.all_trades:
            pnl = Decimal(trade.get('p_l', 0))
            if trade.get('direction') == 'Long':
                if pnl > 0: long_wins += 1
                elif pnl < 0: long_losses += 1
                else: long_be += 1
            elif trade.get('direction') == 'Short':
                if pnl > 0: short_wins += 1
                elif pnl < 0: short_losses += 1
                else: short_be += 1

        long_trades_count = long_wins + long_losses + long_be
        short_trades_count = short_wins + short_losses + short_be
        longs_win_percentage = (Decimal(long_wins) / long_trades_count * 100) if long_trades_count > 0 else Decimal(0)
        shorts_win_percentage = (Decimal(short_wins) / short_trades_count * 100) if short_trades_count > 0 else Decimal(0)

        trade_count = len(self.all_trades)
        win_count, loss_count = len(winning_trades_pnl), len(losing_trades_pnl)

        total_pl = sum(pnl_data)
        total_win = sum(winning_trades_pnl)
        total_loss = abs(sum(losing_trades_pnl))

        avg_win = total_win / win_count if win_count > 0 else Decimal(0)
        avg_loss = total_loss / loss_count if loss_count > 0 else Decimal(0)
        avg_trade_pnl = total_pl / trade_count if trade_count > 0 else Decimal(0)
        avg_win_loss_ratio = avg_win / avg_loss if avg_loss > 0 else Decimal('inf')
        profit_factor = total_win / total_loss if total_loss > 0 else Decimal('inf')

        win_rate = Decimal(win_count) / trade_count if trade_count > 0 else Decimal(0)
        expectancy = (win_rate * avg_win) - ((1-win_rate) * avg_loss)

        largest_profit = max(winning_trades_pnl) if winning_trades_pnl else Decimal(0)
        largest_loss = min(losing_trades_pnl) if losing_trades_pnl else Decimal(0)

        return {
            'total_pl': total_pl,
            'trade_count': trade_count,
            'winning_trades_count': win_count,
            'losing_trades_count': loss_count,
            'breakeven_trades_count': breakeven_trades_count,
            'winning_trades': winning_trades,
            'avg_win': avg_win, 'avg_loss': avg_loss,
            'profit_factor': profit_factor,
            'expectancy': expectancy,
            'win_rate': win_rate * 100,
            'average_trade_pnl': avg_trade_pnl,
            'average_win_loss_ratio': avg_win_loss_ratio,
            'largest_profit': largest_profit,
            'largest_loss': largest_loss,
            'longs_win_percentage': longs_win_percentage,
            'shorts_win_percentage': shorts_win_percentage,
            'long_trades_analysis': {'wins': long_wins, 'losses': long_losses, 'breakeven': long_be, 'total': long_trades_count},
            'short_trades_analysis': {'wins': short_wins, 'losses': short_losses, 'breakeven': short_be, 'total': short_trades_count},
            'losing_trades_pnl': losing_trades_pnl,
            'pnl_data': pnl_data
        }

    def _calculate_advanced_stats(self, base_stats):
        """Statistiche avanzate (efficienza, R:R, drawdown, ecc.)."""
        sell_efficiencies, total_efficiencies, planned_rrs, realized_rrs = [], [], [], []
        for t in base_stats['winning_trades']:
            entry_price = Decimal(t['entry_price']) if t.get('entry_price') is not None else None
            exit_price = Decimal(t['exit_price']) if t.get('exit_price') is not None else None
            mfe_points = Decimal(t['mfe_points']) if t.get('mfe_points') is not None else None

            if mfe_points and mfe_points > 0 and entry_price is not None and exit_price is not None:
                pnl_in_points = abs(exit_price - entry_price)
                if mfe_points > 0:
                    sell_efficiencies.append(pnl_in_points / mfe_points)

        for t in self.all_trades:
            if t.get('mfe_points') is not None and t.get('mae_points') is not None:
                mfe_points, mae_points = Decimal(t['mfe_points']), Decimal(t['mae_points'])
                if (mfe_points + mae_points) > 0:
                    total_efficiencies.append(mfe_points / (mfe_points + mae_points))

            entry = Decimal(t['entry_price']) if t.get('entry_price') is not None else Decimal('0')
            sl = Decimal(t['stop_loss_price']) if t.get('stop_loss_price') is not None else Decimal('0')
            tp = Decimal(t['take_profit_price']) if t.get('take_profit_price') is not None else Decimal('0')
            exit_price = Decimal(t['exit_price']) if t.get('exit_price') is not None else Decimal('0')
            direction = t.get('direction')
            potential_risk_points = abs(entry - sl) if entry and sl else Decimal(0)

            if potential_risk_points > 0:
                pnl = Decimal(t.get('p_l') or 0)
                position_size = Decimal(t.get('position_size') or 1)

                # Infer value per point
                value_per_point = Decimal(0)
                if direction and entry and exit_price:
                    pnl_in_points = (exit_price - entry) if direction == 'Long' else (entry - exit_price)
                    if pnl_in_points != 0:
                        value_per_point = abs(pnl / pnl_in_points)
                if value_per_point == 0:
                    value_per_point = position_size

                initial_dollar_risk = potential_risk_points * value_per_point
                potential_reward_points = abs(tp - entry) if tp and entry else Decimal(0)
                planned_rrs.append(potential_reward_points / potential_risk_points)

                if initial_dollar_risk > 0:
                    realized_rrs.append(pnl / initial_dollar_risk)

        self.all_trades.sort(key=lambda x: x['created_at'])
        safe_pnl_floats = [float(pnl) for pnl in base_stats['pnl_data']]
        equity_curve_data = [{'date': t['created_at'].strftime('%d/%m/%Y'), 'pl': pnl} for t, pnl in zip(self.all_trades, np.cumsum(safe_pnl_floats))]

        equity_points = [0] + [p['pl'] for p in equity_curve_data]
        peak_array = np.maximum.accumulate(equity_points)
        drawdown = peak_array - equity_points
        max_drawdown_abs = Decimal(np.max(drawdown))

        # Recovery Factor & Average Drawdown
        recovery_factor = base_stats['total_pl'] / max_drawdown_abs if max_drawdown_abs > 0 else Decimal('inf')
        all_drawdowns, in_drawdown = [], False
        current_dd_peak = equity_points[0]
        for point in equity_points[1:]:
            if point >= current_dd_peak:
                current_dd_peak = point
                in_drawdown = False
            else:
                if not in_drawdown:
                    in_drawdown = True
                    all_drawdowns.append([])
                all_drawdowns[-1].append(current_dd_peak - point)
        max_dd_values = [max(dd) for dd in all_drawdowns if dd]
        average_drawdown = np.mean(max_dd_values) if max_dd_values else Decimal(0)

        # Temporal metrics
        hold_times_minutes = []
        pnl_by_day_of_week = {i: Decimal(0) for i in range(7)}
        pnl_by_hour = {i: Decimal(0) for i in range(24)}
        for trade in self.all_trades:
            entry, exit_ts = trade.get('entry_timestamp'), trade.get('exit_timestamp')
            if entry and exit_ts:
                hold_times_minutes.append((exit_ts - entry).total_seconds() / 60)
            if entry:
                pnl_by_day_of_week[entry.weekday()] += Decimal(trade.get('p_l', 0))
                pnl_by_hour[entry.hour] += Decimal(trade.get('p_l', 0))

        average_hold_time = np.mean(hold_times_minutes) if hold_times_minutes else 0
        longest_trade_duration = max(hold_times_minutes) if hold_times_minutes else 0
        day_names = ["Lunedì", "Martedì", "Mercoledì", "Giovedì", "Venerdì", "Sabato", "Domenica"]
        performance_by_day_of_week = {day_names[i]: pnl for i, pnl in pnl_by_day_of_week.items()}
        performance_by_hour = {f"{h:02d}:00": pnl for h, pnl in pnl_by_hour.items()}

        # Daily aggregates
        daily_pnl, daily_volume = {}, {}
        for trade in self.all_trades:
            trade_date = trade['created_at'].date()
            daily_pnl.setdefault(trade_date, Decimal(0))
            daily_volume.setdefault(trade_date, Decimal(0))
            pnl = Decimal(trade.get('p_l') or 0)
            volume = Decimal(trade.get('position_size') or 0)
            daily_pnl[trade_date] += pnl
            daily_volume[trade_date] += volume

        daily_pnl_values = list(daily_pnl.values())
        winning_days_pnl = [p for p in daily_pnl_values if p > 0]
        losing_days_pnl = [p for p in daily_pnl_values if p < 0]

        average_daily_pnl = np.mean(daily_pnl_values) if daily_pnl_values else Decimal(0)
        average_winning_day_pnl = np.mean(winning_days_pnl) if winning_days_pnl else Decimal(0)
        average_losing_day_pnl = np.mean(losing_days_pnl) if losing_days_pnl else Decimal(0)
        largest_profitable_day = max(winning_days_pnl) if winning_days_pnl else Decimal(0)
        largest_losing_day = min(losing_days_pnl) if losing_days_pnl else Decimal(0)
        net_daily_pnl_chart = [{'date': d.strftime('%Y-%m-%d'), 'pnl': float(p)} for d, p in daily_pnl.items()]

        total_trading_days = len(daily_pnl_values)
        winning_days = len(winning_days_pnl)
        losing_days = len(losing_days_pnl)
        breakeven_days = total_trading_days - winning_days - losing_days
        day_win_percentage = (Decimal(winning_days) / total_trading_days * 100) if total_trading_days > 0 else Decimal(0)
        average_daily_volume = np.mean(list(daily_volume.values())) if daily_volume else Decimal(0)

        sharpe = sortino = calmar = Decimal(0)
        skewness_val = kurtosis_val = Decimal(0)
        var_95 = cvar_95 = Decimal(0)
        if len(daily_pnl) > 2:
            daily_returns = np.array([float(p) for p in daily_pnl.values()])
            avg_return = np.mean(daily_returns)
            volatility = np.std(daily_returns)
            skewness_val = skew(daily_returns)
            kurtosis_val = kurtosis(daily_returns)
            sharpe = Decimal(avg_return / volatility * np.sqrt(252)) if volatility > 0 else Decimal(0)
            downside_std = np.std(daily_returns[daily_returns < 0]) or 0
            sortino = Decimal(avg_return / downside_std * np.sqrt(252)) if downside_std > 0 else Decimal(0)

            var_95 = Decimal(np.percentile(daily_returns, 5))
            cvar_95 = Decimal(np.mean(daily_returns[daily_returns <= float(var_95)]))

            trade_dates = sorted(daily_pnl.keys())
            trading_days = (trade_dates[-1] - trade_dates[0]).days
            if trading_days > 0 and max_drawdown_abs > 0:
                annualized_return = base_stats['total_pl'] * (Decimal('365') / Decimal(trading_days))
                calmar = annualized_return / max_drawdown_abs

        # Streaks & consistency
        streaks_stats = self._calculate_streaks_and_consistency(base_stats['pnl_data'], daily_pnl_values)

        results = {
            'avg_sell_efficiency': np.mean(sell_efficiencies) * 100 if sell_efficiencies else Decimal(0),
            'avg_total_efficiency': np.mean(total_efficiencies) * 100 if total_efficiencies else Decimal(0),
            'avg_planned_rr': np.mean(planned_rrs) if planned_rrs else Decimal(0),
            'avg_realized_rr': np.mean(realized_rrs) if realized_rrs else Decimal(0),
            'equity_curve_data': equity_curve_data,
            'max_drawdown_abs': max_drawdown_abs,
            'max_drawdown_pct': (max_drawdown_abs / Decimal(peak_array[-1])) * 100 if (peak_array := np.maximum.accumulate([0] + [p['pl'] for p in equity_curve_data]))[-1] > 0 else Decimal(0),
            'sharpe_ratio': sharpe, 'sortino_ratio': sortino, 'calmar_ratio': calmar,
            'skewness': Decimal(skewness_val), 'kurtosis': Decimal(kurtosis_val),
            'var_95': abs(var_95), 'cvar_95': abs(cvar_95),
            'realized_rrs_list': [float(r) for r in realized_rrs],
            'average_daily_pnl': Decimal(average_daily_pnl),
            'average_winning_day_pnl': Decimal(average_winning_day_pnl),
            'average_losing_day_pnl': Decimal(average_losing_day_pnl),
            'largest_profitable_day': largest_profitable_day,
            'largest_losing_day': largest_losing_day,
            'net_daily_pnl_chart': net_daily_pnl_chart,
            'winning_days': winning_days,
            'losing_days': losing_days,
            'breakeven_days': breakeven_days,
            'day_win_percentage': day_win_percentage,
            'average_daily_volume': Decimal(average_daily_volume),
            'recovery_factor': base_stats['total_pl'] / max_drawdown_abs if max_drawdown_abs > 0 else Decimal('inf'),
            'average_drawdown': Decimal(average_drawdown),
            'average_hold_time': average_hold_time,
            'longest_trade_duration': longest_trade_duration,
            'performance_by_day_of_week': performance_by_day_of_week,
            'performance_by_hour': performance_by_hour,
        }
        results.update(streaks_stats)
        return results

    def _calculate_streaks_and_consistency(self, pnl_data, daily_pnl_values):
        # Trade streaks
        max_consecutive_wins = max_consecutive_losses = 0
        current_wins = current_losses = 0
        for pnl in pnl_data:
            if pnl > 0:
                current_wins += 1
                current_losses = 0
            elif pnl < 0:
                current_losses += 1
                current_wins = 0
            else:
                current_wins = current_losses = 0
            max_consecutive_wins = max(max_consecutive_wins, current_wins)
            max_consecutive_losses = max(max_consecutive_losses, current_losses)

        current_trade_streak = 0
        if pnl_data:
            if pnl_data[-1] > 0: current_trade_streak = current_wins
            elif pnl_data[-1] < 0: current_trade_streak = -current_losses

        # Day streaks
        max_consecutive_winning_days = max_consecutive_losing_days = 0
        current_winning_days = current_losing_days = 0
        for pnl in daily_pnl_values:
            if pnl > 0:
                current_winning_days += 1
                current_losing_days = 0
            elif pnl < 0:
                current_losing_days += 1
                current_winning_days = 0
            else:
                current_winning_days = current_losing_days = 0
            max_consecutive_winning_days = max(max_consecutive_winning_days, current_winning_days)
            max_consecutive_losing_days = max(max_consecutive_losing_days, current_losing_days)

        current_day_streak = 0
        if daily_pnl_values:
            if daily_pnl_values[-1] > 0: current_day_streak = current_winning_days
            elif daily_pnl_values[-1] < 0: current_day_streak = -current_losing_days

        # Consistency score (std dev dei PnL giornalieri)
        consistency_score = np.std(daily_pnl_values) if daily_pnl_values else 0

        return {
            'max_consecutive_wins': max_consecutive_wins,
            'max_consecutive_losses': max_consecutive_losses,
            'current_trade_streak': current_trade_streak,
            'max_consecutive_winning_days': max_consecutive_winning_days,
            'max_consecutive_losing_days': max_consecutive_losing_days,
            'current_day_streak': current_day_streak,
            'consistency_score': Decimal(consistency_score)
        }

    def calculate_vantage_score(self):
        """
        Calcola il Vantage Score e i suoi componenti individuali.
        """
        if not self.all_trades:
            return {
                'vantage_score': 0,
                'profit_factor_score': 0,
                'avg_win_loss_score': 0,
                'max_drawdown_score': 0,
                'win_rate_score': 0,
                'consistency_score': 0,
                'recovery_factor_score': 0
            }

        base_stats = self._calculate_base_stats()
        advanced_stats = self._calculate_advanced_stats(base_stats)
        stats = {**base_stats, **advanced_stats}

        # Scoring
        pf = stats.get('profit_factor', 0)
        if pf == float('inf') or pf >= 2.6: pf_score = 100
        elif pf >= 2.2: pf_score = 80
        elif pf >= 1.8: pf_score = 60
        elif pf >= 1.5: pf_score = 40
        elif pf > 1.0: pf_score = 20
        else: pf_score = 0

        awl = stats.get('average_win_loss_ratio', 0)
        if awl == float('inf') or awl >= 2.6: awl_score = 100
        elif awl >= 2.2: awl_score = 80
        elif awl >= 1.8: awl_score = 60
        elif awl >= 1.5: awl_score = 40
        elif awl > 1.0: awl_score = 20
        else: awl_score = 0

        max_dd_pct = float(stats.get('max_drawdown_pct', 100))
        mdd_score = max(0, 100 - max_dd_pct)

        win_rate = float(stats.get('win_rate', 0))
        wr_score = min(100, (win_rate / 60.0) * 100) if 60.0 > 0 else 0

        total_profit = float(stats.get('total_pl', 0))
        daily_std = float(stats.get('consistency_score', 0))
        consistency_score = 0
        if total_profit > 0 and daily_std > 0:
            variation = (daily_std / total_profit) * 100
            consistency_score = max(0, 100 - variation)
        elif total_profit > 0:
            consistency_score = 100

        rf = float(stats.get('recovery_factor', 0))
        if rf == float('inf') or rf >= 3.5: rf_score = 100
        elif rf >= 2.5: rf_score = 80
        elif rf >= 1.8: rf_score = 60
        elif rf >= 1.0: rf_score = 40
        else: rf_score = 0

        vantage_score = (
            (pf_score * 0.25) +
            (awl_score * 0.20) +
            (mdd_score * 0.20) +
            (wr_score * 0.15) +
            (consistency_score * 0.10) +
            (rf_score * 0.10)
        )

        return {
            'vantage_score': round(vantage_score, 2),
            'profit_factor_score': round(pf_score, 2),
            'avg_win_loss_score': round(awl_score, 2),
            'max_drawdown_score': round(mdd_score, 2),
            'win_rate_score': round(wr_score, 2),
            'consistency_score': round(consistency_score, 2),
            'recovery_factor_score': round(rf_score, 2)
        }

    def _prepare_chart_data(self, advanced_stats):
        """Dati per grafici."""
        performance_by_setup = {}
        for t in self.all_trades:
            setup_name = t.get('setup', "Non specificato")
            performance_by_setup.setdefault(setup_name, Decimal(0))
            pnl = Decimal(t['p_l']) if t.get('p_l') is not None else Decimal('0')
            performance_by_setup[setup_name] += pnl
        setup_chart_data = [{'setup': k, 'total_pl': float(v)} for k, v in performance_by_setup.items()]

        r_multiple_bins = [-np.inf, -2, -1, 0, 1, 2, 3, np.inf]
        r_multiple_labels = ["< -2R", "-2R..-1R", "-1R..0R", "0R..1R", "1R..2R", "2R..3R", "> 3R"]
        counts, _ = np.histogram(advanced_stats.get('realized_rrs_list', []), bins=r_multiple_bins)

        pnl_by_day_data = advanced_stats.get('performance_by_day_of_week', {})
        pnl_by_hour_data = advanced_stats.get('performance_by_hour', {})

        return {
            'setup_chart_data': setup_chart_data,
            'r_multiple_data': {'labels': r_multiple_labels, 'data': counts.tolist()},
            'performance_by_day': {
                'labels': list(pnl_by_day_data.keys()),
                'data': [float(v) for v in pnl_by_day_data.values()]
            },
            'performance_by_hour': {
                'labels': list(pnl_by_hour_data.keys()),
                'data': [float(v) for v in pnl_by_hour_data.values()]
            }
        }

    def calculate_all_metrics(self):
        """Pacchetto completo di metriche + grafici."""
        if not self.all_trades:
            return self._get_empty_response()

        base_stats = self._calculate_base_stats()
        advanced_stats = self._calculate_advanced_stats(base_stats)
        chart_data = self._prepare_chart_data(advanced_stats)

        final_stats = {**base_stats, **advanced_stats}
        for k in ('winning_trades', 'realized_rrs_list', 'losing_trades_pnl', 'pnl_data'):
            final_stats.pop(k, None)

        final_payload = {
            'trades': sorted(self.all_trades, key=lambda x: x['created_at'], reverse=True),
            'stats': final_stats,
            'equity_curve_data': advanced_stats['equity_curve_data'],
            **chart_data
        }
        return final_payload
