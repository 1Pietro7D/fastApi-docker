# app/Controllers/trades_controller.py
# Controller FastAPI per i Trade: lista/lettura/creazione/aggiornamento + dati calendario + Vantage Score (pubblici, con user_id come query)

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
    """
    CRUD/Query dei trades resi PUBBLICI.
    Richiedono sempre un 'user_id' (UUID) come query param per sapere di chi leggere/scrivere.
    """

    def __init__(self) -> None:
        ...

    async def list_trades(
        self,
        user_id: UUID = Query(..., description="UUID dell'utente proprietario dei trades"),
        symbol: Optional[str] = Query(None),
        direction: Optional[str] = Query(None),
        setups: Optional[List[str]] = Query(None),
        mistakes: Optional[List[str]] = Query(None),
        days_of_week: Optional[List[int]] = Query(None, description="ISO day of week 1..7"),
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
        for tr, tag_names in rows:
            dto = TradeRead.model_validate(tr)
            dto.tags = tag_names
            out.append(dto)
        return out

    async def get_trade(
        self,
        trade_id: UUID,
        user_id: UUID = Query(..., description="UUID dell'utente proprietario del trade"),
        db: AsyncSession = Depends(get_db),
    ) -> TradeRead:
        repo = TradeRepository(db)
        row = await repo.get_by_id_with_tags(user_id, trade_id)
        if not row:
            raise HTTPException(status_code=404, detail="Trade non trovato")
        trade, tag_names = row
        dto = TradeRead.model_validate(trade)
        dto.tags = tag_names
        return dto

    async def create_trade(
        self,
        payload: TradeCreate,
        user_id: UUID = Query(..., description="UUID dell'utente proprietario (FK su auth.users.id)"),
        db: AsyncSession = Depends(get_db),
    ) -> TradeRead:
        repo = TradeRepository(db)
        data = payload.model_dump()
        tag_names = data.pop("tags", None) or []
        trade = await repo.create_with_tags(user_id, data, tag_names)
        dto = TradeRead.model_validate(trade)
        _, tags_now = await repo.get_by_id_with_tags(user_id, trade.id)  # type: ignore[arg-type]
        dto.tags = tags_now
        return dto

    async def update_trade(
        self,
        trade_id: UUID,
        payload: TradeUpdate,
        user_id: UUID = Query(..., description="UUID dell'utente proprietario del trade"),
        db: AsyncSession = Depends(get_db),
    ) -> TradeRead:
        repo = TradeRepository(db)
        patch = payload.model_dump(exclude_none=True)
        tag_names = patch.pop("tags", None)
        trade = await repo.update_with_tags(user_id, trade_id, patch, tag_names)
        if not trade:
            raise HTTPException(status_code=404, detail="Trade non trovato")
        dto = TradeRead.model_validate(trade)
        _, tags_now = await repo.get_by_id_with_tags(user_id, trade_id)
        dto.tags = tags_now
        return dto

    async def calendar_data(
        self,
        user_id: UUID = Query(..., description="UUID dell'utente proprietario"),
        db: AsyncSession = Depends(get_db),
    ) -> list[dict]:
        repo = TradeRepository(db)
        return await repo.get_calendar_data(user_id)

    async def vantage_score(
        self,
        user_id: UUID = Query(..., description="UUID dell'utente proprietario"),
        db: AsyncSession = Depends(get_db),
    ) -> dict:
        repo = TradeRepository(db)
        rows = await repo.list_with_filters(user_id)
        trades_as_dicts: list[dict] = []
        for tr, tag_names in rows:
            dto = Trade
