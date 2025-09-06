# app/Services/metrics/trade_enricher.py

from decimal import Decimal

def enrich_trade_with_advanced_metrics(trade):
    """
    Calcola metriche avanzate per un singolo trade e le aggiunge al dizionario del trade.
    Modifica il dizionario 'trade' in-place e lo restituisce.
    """
    if not trade:
        return None

    entry = Decimal(trade.get('entry_price') or 0)
    exit_price = Decimal(trade.get('exit_price') or 0)
    lowest = Decimal(trade.get('lowest_price_during_trade') or 0)
    highest = Decimal(trade.get('highest_price_during_trade') or 0)
    sl = Decimal(trade.get('stop_loss_price') or 0)
    tp = Decimal(trade.get('take_profit_price') or 0)
    pnl = Decimal(trade.get('p_l') or 0)
    position_size = Decimal(trade.get('position_size') or 1)
    direction = trade.get('direction')

    # 1) Infer value-per-point (es. futures)
    value_per_point = Decimal(0)
    if direction and entry and exit_price and pnl != 0:
        pnl_in_points = (exit_price - entry) if direction == 'Long' else (entry - exit_price)
        if pnl_in_points != 0:
            value_per_point = abs(pnl / pnl_in_points)

    # fallback: usa la size come moltiplicatore (azioni, ecc.)
    if value_per_point == 0:
        value_per_point = position_size

    # 2) MAE/MFE (punti e USD)
    if entry > 0 and lowest > 0 and highest > 0 and direction:
        if direction == 'Long':
            mae_points = entry - lowest
            mfe_points = highest - entry
        else:  # Short
            mae_points = highest - entry
            mfe_points = entry - lowest
        trade['mae_usd'] = -abs(mae_points * value_per_point)  # MAE sempre perdita potenziale
        trade['mfe_usd'] = mfe_points * value_per_point
    else:
        trade['mae_usd'], trade['mfe_usd'] = Decimal(0), Decimal(0)

    # 3) R-Multiples e valori USD
    potential_risk_points = abs(entry - sl) if entry and sl else Decimal(0)
    if potential_risk_points > 0:
        initial_dollar_risk = potential_risk_points * value_per_point
        potential_reward_points = abs(tp - entry) if tp and entry else Decimal(0)

        trade['planned_rr'] = (potential_reward_points / potential_risk_points) if potential_risk_points else Decimal(0)
        trade['stop_loss_usd'] = -abs(initial_dollar_risk)
        trade['profit_target_usd'] = potential_reward_points * value_per_point
        trade['realized_rr'] = (pnl / initial_dollar_risk) if initial_dollar_risk > 0 else Decimal(0)
    else:
        trade['planned_rr'], trade['realized_rr'] = Decimal(0), Decimal(0)
        trade['stop_loss_usd'], trade['profit_target_usd'] = Decimal(0), Decimal(0)

    return trade
