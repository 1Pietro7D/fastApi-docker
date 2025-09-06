# app/Repositories/trade_repository.py

from __future__ import annotations

from typing import Optional, List
from uuid import UUID

from sqlalchemy import select, insert, update, delete, and_, func, Date, cast
from sqlalchemy.ext.asyncio import AsyncSession

from app.Models.trade import Trade
from app.Models.tag import Tag
from app.Models.trades_tags import TradesTags


class TradeRepository:
    """Query e mutazioni per trades + gestione associazioni tag."""

    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    # ---------- Letture ----------

    async def get_by_id_with_tags(self, user_id: UUID, trade_id: UUID) -> Optional[tuple[Trade, List[str]]]:
        stmt = select(Trade).where(and_(Trade.id == trade_id, Trade.user_id == user_id)).limit(1)
        res = await self.db.execute(stmt)
        trade = res.scalars().first()
        if not trade:
            return None

        tag_stmt = (
            select(Tag.name)
            .join(TradesTags, and_(TradesTags.tag_id == Tag.id, TradesTags.user_id == Tag.user_id))
            .where(and_(TradesTags.trade_id == trade.id, TradesTags.user_id == user_id))
            .order_by(Tag.name.asc())
        )
        tag_names = (await self.db.execute(tag_stmt)).scalars().all()
        return trade, list(tag_names)

    async def list_with_filters(
        self,
        user_id: UUID,
        symbol: Optional[str] = None,
        direction: Optional[str] = None,
        setups: Optional[List[str]] = None,
        mistakes: Optional[List[str]] = None,
        days_of_week: Optional[List[int]] = None,  # ISO DOW 1..7
        min_size: Optional[float] = None,
        max_size: Optional[float] = None,
        tags: Optional[List[str]] = None,
    ) -> list[tuple[Trade, list[str]]]:
        t = Trade
        base = select(t).where(t.user_id == user_id)

        if symbol:
            base = base.where(t.symbol.ilike(f"%{symbol}%"))
        if direction:
            base = base.where(t.direction == direction)
        if setups:
            base = base.where(t.setup.in_(setups))
        if mistakes:
            base = base.where(t.mistakes.op("@>")(mistakes))
        if days_of_week:
            base = base.where(and_(t.entry_timestamp.is_not(None), func.extract("isodow", t.entry_timestamp).in_(days_of_week)))
        if min_size is not None:
            base = base.where(t.position_size >= min_size)
        if max_size is not None:
            base = base.where(t.position_size <= max_size)

        base = base.order_by(t.entry_timestamp.desc().nullslast(), t.created_at.desc())
        trades = (await self.db.execute(base)).scalars().all()

        if tags:
            tag_ids = (await self.db.execute(
                select(Tag.id).where(and_(Tag.user_id == user_id, Tag.name.in_(tags)))
            )).scalars().all()
            if not tag_ids:
                return []

            sub = (
                select(TradesTags.trade_id)
                .where(and_(TradesTags.user_id == user_id, TradesTags.tag_id.in_(tag_ids)))
                .group_by(TradesTags.trade_id)
                .having(func.count(func.distinct(TradesTags.tag_id)) == len(tag_ids))
            )
            ok_ids = set((await self.db.execute(sub)).scalars().all())
            trades = [tr for tr in trades if tr.id in ok_ids]

        if not trades:
            return []

        trade_ids = [tr.id for tr in trades]
        tags_rows = await self.db.execute(
            select(TradesTags.trade_id, Tag.name)
            .join(Tag, and_(Tag.id == TradesTags.tag_id, Tag.user_id == TradesTags.user_id))
            .where(and_(TradesTags.user_id == user_id, TradesTags.trade_id.in_(trade_ids)))
            .order_by(Tag.name.asc())
        )
        tags_map: dict[UUID, list[str]] = {}
        for tid, tname in tags_rows.all():
            tags_map.setdefault(tid, []).append(tname)

        return [(tr, tags_map.get(tr.id, [])) for tr in trades]

    async def get_calendar_data(self, user_id: UUID) -> list[dict]:
        stmt = (
            select(
                cast(Trade.entry_timestamp, Date).label("trade_date"),
                func.coalesce(func.sum(Trade.p_l), 0.0).label("daily_pnl"),
            )
            .where(and_(Trade.user_id == user_id, Trade.entry_timestamp.is_not(None)))
            .group_by(cast(Trade.entry_timestamp, Date))
            .order_by(cast(Trade.entry_timestamp, Date).asc())
        )
        rows = (await self.db.execute(stmt)).all()
        return [{"date": r.trade_date.isoformat(), "pnl": float(r.daily_pnl or 0.0)} for r in rows]

    # ---------- Scritture ----------

    async def create_with_tags(self, user_id: UUID, data: dict, tag_names: list[str]) -> Trade:
        payload = {**data, "user_id": user_id}
        res = await self.db.execute(insert(Trade).values(**payload).returning(Trade))
        trade = res.scalar_one()

        if tag_names:
            tag_ids = await self._ensure_tags(user_id, tag_names)
            await self._attach_tags(trade.id, user_id, tag_ids)

        await self.db.commit()
        return trade

    async def update_with_tags(
        self,
        user_id: UUID,
        trade_id: UUID,
        patch: dict,
        tag_names: Optional[list[str]],
    ) -> Optional[Trade]:
        res = await self.db.execute(
            update(Trade)
            .where(and_(Trade.id == trade_id, Trade.user_id == user_id))
            .values(**patch)
            .returning(Trade)
        )
        trade = res.scalar_one_or_none()
        if not trade:
            await self.db.rollback()
            return None

        if tag_names is not None:
            await self.db.execute(delete(TradesTags).where(and_(TradesTags.trade_id == trade_id, TradesTags.user_id == user_id)))
            if tag_names:
                tag_ids = await self._ensure_tags(user_id, tag_names)
                await self._attach_tags(trade_id, user_id, tag_ids)

        await self.db.commit()
        return trade

    # ---------- Helpers tag ----------

    async def _ensure_tags(self, user_id: UUID, tag_names: list[str]) -> list[UUID]:
        ids: list[UUID] = []
        # de-duplica e normalizza
        for name in {n.strip() for n in tag_names if n and n.strip()}:
            row = (await self.db.execute(
                select(Tag).where(and_(Tag.user_id == user_id, Tag.name == name)).limit(1)
            )).scalars().first()
            if row:
                ids.append(row.id)
                continue
            ids.append((await self.db.execute(insert(Tag).values(user_id=user_id, name=name).returning(Tag.id))).scalar_one())
        return ids

    async def _attach_tags(self, trade_id: UUID, user_id: UUID, tag_ids: list[UUID]) -> None:
        if not tag_ids:
            return
        values = [{"trade_id": trade_id, "tag_id": tid, "user_id": user_id} for tid in set(tag_ids)]
        await self.db.execute(insert(TradesTags), values)
