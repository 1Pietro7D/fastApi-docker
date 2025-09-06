# app/Controllers/trades_controller.py
# Controller per i TRADES:
# - lista filtrata (richiede user_id in query)
# - get singolo trade per id (pubblico, senza user_id in query)
# - create/update/delete (richiedono user_id in query per scoping)
# - calendar data (per user_id)
# - vantage score (per user_id)
#
# NOTA IMPORTANTE:
# Per evitare MissingGreenlet quando Pydantic legge campi lazy del modello ORM,
# convertiamo l'oggetto Trade in un dict “piatto” ed aggiungiamo i tag già
# caricati dal repository. Poi validiamo il dict con TradeRead.

from __future__ import annotations

from typing import List, Optional
from uuid import UUID

from fastapi import Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.Infrastructure.db import get_db
from app.Repositories.trade_repository import TradeRepository
from app.Schemas.trade import TradeCreate, TradeUpdate, TradeRead
from app.Services.metrics.metrics_calculator import MetricsCalculator


class TradesController:
    """CRUD/Query trades + calendario e Vantage Score."""

    def __init__(self) -> None:
        ...

    # --------------------------
    # helper DTO builder
    # --------------------------
    @staticmethod
    def _to_trade_read_dict(trade, tag_names: List[str]) -> dict:
        """
        Estrae solo i campi “piatti” dal modello ORM Trade e aggiunge `tags`.
        NON passa l'oggetto ORM a Pydantic per evitare accessi lazy.
        """
        return {
            "id": trade.id,
            "created_at": trade.created_at,
            "user_id": trade.user_id,
            "p_l": trade.p_l,
            "setup": trade.setup,
            "stop_loss_price": trade.stop_loss_price,
            "take_profit_price": trade.take_profit_price,
            "notes": trade.notes,
            "entry_price": trade.entry_price,
            "exit_price": trade.exit_price,
            "position_size": trade.position_size,
            "lowest_price_during_trade": trade.lowest_price_during_trade,
            "highest_price_during_trade": trade.highest_price_during_trade,
            "symbol": trade.symbol,
            "direction": trade.direction,
            "emotional_state": trade.emotional_state,
            "mistakes": trade.mistakes,
            "notes_pre_trade": trade.notes_pre_trade,
            "notes_post_trade": trade.notes_post_trade,
            "entry_timestamp": trade.entry_timestamp,
            "exit_timestamp": trade.exit_timestamp,
            "tags": tag_names or [],
        }

    # --------------------------
    # LIST
    # --------------------------
    async def list_trades(
        self,
        user_id: UUID = Query(..., description="ID utente proprietario dei trade"),
        symbol: Optional[str] = Query(None),
        direction: Optional[str] = Query(None),
        setups: Optional[List[str]] = Query(None),
        mistakes: Optional[List[str]] = Query(None),
        days_of_week: Optional[List[int]] = Query(
            None, description="ISO day of week 1..7"
        ),
        min_size: Optional[float] = Query(None),
        max_size: Optional[float] = Query(None),
        tags: Optional[List[str]] = Query(None),
        db: AsyncSession = Depends(get_db),
    ) -> List[TradeRead]:
        repo = TradeRepository(db)
        rows = await repo.list_with_filters(
            user_id=user_id,
            symbol=symbol,
            direction=direction,
            setups=setups,
            mistakes=mistakes,
            days_of_week=days_of_week,
            min_size=min_size,
            max_size=max_size,
            tags=tags,
        )
        out: List[TradeRead] = []
        for trade, tag_names in rows:
            payload = self._to_trade_read_dict(trade, tag_names)
            out.append(TradeRead.model_validate(payload))
        return out

    # --------------------------
    # GET by ID (senza user_id)
    # --------------------------
    async def get_trade(
        self,
        trade_id: UUID,
        db: AsyncSession = Depends(get_db),
    ) -> TradeRead:
        repo = TradeRepository(db)
        row = await repo.get_by_trade_id_with_tags(trade_id)
        if not row:
            raise HTTPException(status_code=404, detail="Trade non trovato")
        trade, tag_names = row
        payload = self._to_trade_read_dict(trade, tag_names)
        return TradeRead.model_validate(payload)

    # --------------------------
    # CREATE
    # --------------------------
    async def create_trade(
        self,
        payload: TradeCreate,
        user_id: UUID = Query(..., description="ID utente proprietario del nuovo trade"),
        db: AsyncSession = Depends(get_db),
    ) -> TradeRead:
        repo = TradeRepository(db)
        data = payload.model_dump()
        tag_names = data.pop("tags", None) or []
        trade = await repo.create_with_tags(user_id, data, tag_names)
        # ricarica i tag (in forma di nomi) per il DTO
        _, tags_now = await repo.get_by_id_with_tags(user_id, trade.id)  # type: ignore[arg-type]
        payload_dict = self._to_trade_read_dict(trade, tags_now)
        return TradeRead.model_validate(payload_dict)

    # --------------------------
    # UPDATE
    # --------------------------
    async def update_trade(
        self,
        trade_id: UUID,
        payload: TradeUpdate,
        user_id: UUID = Query(..., description="ID utente proprietario del trade"),
        db: AsyncSession = Depends(get_db),
    ) -> TradeRead:
        repo = TradeRepository(db)
        patch = payload.model_dump(exclude_none=True)
        tag_names = patch.pop("tags", None)
        trade = await repo.update_with_tags(user_id, trade_id, patch, tag_names)
        if not trade:
            raise HTTPException(status_code=404, detail="Trade non trovato")

        _, tags_now = await repo.get_by_id_with_tags(user_id, trade_id)  # type: ignore[arg-type]
        payload_dict = self._to_trade_read_dict(trade, tags_now)
        return TradeRead.model_validate(payload_dict)

    # --------------------------
    # DELETE
    # --------------------------
    async def delete_trade(
        self,
        trade_id: UUID,
        user_id: UUID = Query(..., description="ID utente proprietario del trade"),
        db: AsyncSession = Depends(get_db),
    ) -> dict:
        repo = TradeRepository(db)
        ok = await repo.delete(user_id, trade_id)
        if not ok:
            raise HTTPException(status_code=404, detail="Trade non trovato")
        return {"deleted": True}

    # --------------------------
    # CALENDAR DATA
    # --------------------------
    async def calendar_data(
        self,
        user_id: UUID = Query(..., description="ID utente"),
        db: AsyncSession = Depends(get_db),
    ) -> list[dict]:
        repo = TradeRepository(db)
        return await repo.get_calendar_data(user_id)

    # --------------------------
    # VANTAGE SCORE
    # --------------------------
    async def vantage_score(
        self,
        user_id: UUID = Query(..., description="ID utente"),
        db: AsyncSession = Depends(get_db),
    ) -> dict:
        repo = TradeRepository(db)
        rows = await repo.list_with_filters(user_id)

        # trasformiamo le tuple (Trade, tag_names) in dizionari flat per il calcolatore
        trades_as_dicts = []
        for trade, tag_names in rows:
            trades_as_dicts.append(self._to_trade_read_dict(trade, tag_names))

        calc = MetricsCalculator(trades_as_dicts)
        return calc.calculate_vantage_score()
