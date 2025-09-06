# app/Repositories/trade_repository.py
# Repository asincrono per la gestione dei TRADES, TAGS e tabella ponte TRADES_TAGS.
# Espone query filtrabili, CRUD, letture con tag aggregati e funzioni di supporto.
# Tutte le query sono costruite con SQLAlchemy 2.x (async) e Postgres.

from __future__ import annotations

from typing import Iterable, List, Optional, Sequence, Tuple
from uuid import UUID

from sqlalchemy import delete, func, select, update
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession

from app.Models.trade import Trade
from app.Models.tag import Tag
from app.Models.trades_tags import TradesTags


class TradeRepository:
    """Incapsula l’accesso a Trade / Tag / TradesTags (async)."""

    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    # ──────────────────────────────────────────────────────────────────────
    # HELPERS
    # ──────────────────────────────────────────────────────────────────────
    async def _get_tag_ids_for_user(
        self, user_id: UUID, names: Iterable[str]
    ) -> dict[str, UUID]:
        """
        Ritorna una mappa {name -> tag_id} per i tag (dell'utente) già esistenti.
        """
        names = [n for n in (names or []) if n]
        if not names:
            return {}

        q = (
            select(Tag.name, Tag.id)
            .where(Tag.user_id == user_id)
            .where(Tag.name.in_(names))
        )
        res = await self.db.execute(q)
        return {row[0]: row[1] for row in res.all()}

    async def _ensure_tags_and_get_ids(
        self, user_id: UUID, names: Iterable[str]
    ) -> List[UUID]:
        """
        Garantisce che per ogni name esista un Tag(user_id, name), creando quelli mancanti.
        Ritorna la lista degli id in input-order (senza duplicati).
        """
        deduped = []
        seen = set()
        for n in names or []:
            if not n:
                continue
            k = n.strip()
            if k and k not in seen:
                deduped.append(k)
                seen.add(k)

        if not deduped:
            return []

        existing = await self._get_tag_ids_for_user(user_id, deduped)
        to_create = [n for n in deduped if n not in existing]

        # Inserimento bulk con ON CONFLICT (user_id, name) DO NOTHING
        if to_create:
            stmt = (
                insert(Tag)
                .values([{"user_id": user_id, "name": n} for n in to_create])
                .on_conflict_do_nothing(
                    index_elements=[Tag.user_id, Tag.name]  # unique (user_id, name)
                )
                .returning(Tag.id, Tag.name)
            )
            # Nota: returning in on_conflict_do_nothing può non restituire righe se c'è conflitto.
            # Per ottenere tutti gli id coerenti, dopo l'insert rileggiamo comunque.
            await self.db.execute(stmt)

        # Reload globale dei tag richiesti (esistenti + appena creati)
        q = (
            select(Tag.name, Tag.id)
            .where(Tag.user_id == user_id)
            .where(Tag.name.in_(deduped))
        )
        res = await self.db.execute(q)
        name_to_id = {row[0]: row[1] for row in res.all()}

        # Mantieni l'ordine richiesto in input
        return [name_to_id[n] for n in deduped if n in name_to_id]

    async def _replace_trade_tag_links(
        self, user_id: UUID, trade_id: UUID, tag_ids: Iterable[UUID]
    ) -> None:
        """
        Sostituisce integralmente i link tag ↔ trade per il trade indicato.
        Esegue:
          - DELETE su trades_tags per quel trade (scoped per user_id per coerenza)
          - INSERT dei nuovi link (ON CONFLICT DO NOTHING per idempotenza)
        """
        # 1) rimuovi link esistenti
        del_stmt = delete(TradesTags).where(
            TradesTags.trade_id == trade_id, TradesTags.user_id == user_id
        )
        await self.db.execute(del_stmt)

        # 2) inserisci nuovi link
        rows = [
            {"trade_id": trade_id, "tag_id": tag_id, "user_id": user_id}
            for tag_id in (tag_ids or [])
        ]
        if rows:
            ins = (
                insert(TradesTags)
                .values(rows)
                .on_conflict_do_nothing(
                    index_elements=[TradesTags.trade_id, TradesTags.tag_id]
                )
            )
            await self.db.execute(ins)

    async def _load_tags_for_trades(
        self, trade_ids: Sequence[UUID]
    ) -> dict[UUID, list[str]]:
        """
        Carica tutte le etichette (nomi) dei tag per un insieme di trade_ids.
        Ritorna {trade_id: [name, ...]}.
        """
        if not trade_ids:
            return {}

        q = (
            select(TradesTags.trade_id, Tag.name)
            .join(Tag, Tag.id == TradesTags.tag_id)
            .where(TradesTags.trade_id.in_(trade_ids))
        )
        res = await self.db.execute(q)
        out: dict[UUID, list[str]] = {}
        for trade_id, name in res.all():
            out.setdefault(trade_id, []).append(name)
        return out

    # ──────────────────────────────────────────────────────────────────────
    # LIST + FILTRI
    # ──────────────────────────────────────────────────────────────────────
    async def list_with_filters(
        self,
        user_id: UUID,
        *,
        symbol: Optional[str] = None,
        direction: Optional[str] = None,
        setups: Optional[List[str]] = None,
        mistakes: Optional[List[str]] = None,
        days_of_week: Optional[List[int]] = None,  # 1..7 (ISO)
        min_size: Optional[float] = None,
        max_size: Optional[float] = None,
        tags: Optional[List[str]] = None,
    ) -> List[Tuple[Trade, List[str]]]:
        """
        Ritorna una lista di tuple (Trade, [tag_names]) filtrate per user_id e criteri opzionali.

        NOTE filtri:
          - symbol: ILIKE "%symbol%"
          - direction: ==
          - setups: IN
          - mistakes: array contiene tutti? (qui usiamo "contains" Postgres -> @>, basta che contenga l'insieme passato)
          - days_of_week: func.extract('isodow', entry_timestamp).in_(days_of_week)
          - min/max_size: range su position_size
          - tags: deve contenere TUTTI i tag passati (subquery con count(distinct) == len(tags))
        """
        base = select(Trade).where(Trade.user_id == user_id)

        if symbol:
            base = base.where(Trade.symbol.ilike(f"%{symbol}%"))
        if direction:
            base = base.where(Trade.direction == direction)
        if setups:
            base = base.where(Trade.setup.in_(setups))
        if mistakes:
            # Postgres ARRAY contains
            base = base.where(Trade.mistakes.contains(mistakes))
        if days_of_week:
            base = base.where(
                func.extract("isodow", Trade.entry_timestamp).in_(days_of_week)
            )
        if min_size is not None:
            base = base.where(Trade.position_size >= min_size)
        if max_size is not None:
            base = base.where(Trade.position_size <= max_size)

        # Filtra per TAGS (tutti presenti) con subquery:
        if tags:
            tag_subq = (
                select(TradesTags.trade_id)
                .join(Tag, Tag.id == TradesTags.tag_id)
                .where(TradesTags.user_id == user_id)
                .where(Tag.name.in_(tags))
                .group_by(TradesTags.trade_id)
                .having(func.count(func.distinct(Tag.name)) == len(set(tags)))
            )
            base = base.where(Trade.id.in_(tag_subq))

        base = base.order_by(
            Trade.entry_timestamp.desc().nullslast(), Trade.created_at.desc()
        )

        trades: List[Trade] = (await self.db.execute(base)).scalars().all()
        ids = [t.id for t in trades]
        tag_map = await self._load_tags_for_trades(ids)

        return [(t, tag_map.get(t.id, [])) for t in trades]

    # ──────────────────────────────────────────────────────────────────────
    # GET (scoped per utente) + GET (solo per trade_id)
    # ──────────────────────────────────────────────────────────────────────
    async def get_by_id_with_tags(
        self, user_id: UUID, trade_id: UUID
    ) -> Optional[Tuple[Trade, List[str]]]:
        """
        Ritorna (Trade, [tag_names]) se il trade appartiene a user_id; altrimenti None.
        """
        q = select(Trade).where(Trade.id == trade_id, Trade.user_id == user_id).limit(1)
        res = await self.db.execute(q)
        trade = res.scalars().first()
        if not trade:
            return None

        tag_map = await self._load_tags_for_trades([trade_id])
        return trade, tag_map.get(trade_id, [])

    async def get_by_trade_id_with_tags(
        self, trade_id: UUID
    ) -> Optional[Tuple[Trade, List[str]]]:
        """
        Ritorna (Trade, [tag_names]) cercando SOLO per trade_id (senza filtro su user_id).
        """
        q = select(Trade).where(Trade.id == trade_id).limit(1)
        res = await self.db.execute(q)
        trade = res.scalars().first()
        if not trade:
            return None

        tag_map = await self._load_tags_for_trades([trade_id])
        return trade, tag_map.get(trade_id, [])

    # ──────────────────────────────────────────────────────────────────────
    # CREATE
    # ──────────────────────────────────────────────────────────────────────
    async def create_with_tags(
        self, user_id: UUID, data: dict, tag_names: Optional[List[str]] = None
    ) -> Trade:
        """
        Crea un Trade per user_id e collega eventuali tag (creandoli se mancanti).
        Ritorna l'oggetto Trade appena creato.
        """
        # 1) crea Trade
        trade = Trade(user_id=user_id, **data)
        self.db.add(trade)
        await self.db.flush()   # ottieni id immediatamente

        # 2) gestisci Tags (se forniti)
        if tag_names:
            tag_ids = await self._ensure_tags_and_get_ids(user_id, tag_names)
            await self._replace_trade_tag_links(user_id, trade.id, tag_ids)  # type: ignore[arg-type]

        await self.db.commit()
        # refresh opzionale
        await self.db.refresh(trade)
        return trade

    # ──────────────────────────────────────────────────────────────────────
    # UPDATE
    # ──────────────────────────────────────────────────────────────────────
    async def update_with_tags(
        self,
        user_id: UUID,
        trade_id: UUID,
        patch: dict,
        tag_names: Optional[List[str]] = None,
    ) -> Optional[Trade]:
        """
        Aggiorna i campi del Trade di user_id. Se `tag_names` è non-None,
        riallinea interamente le associazioni tag↔trade.
        Ritorna la Trade aggiornata o None se non trovata.
        """
        # 1) Aggiorna i campi (se patch è vuota, salta update)
        if patch:
            stmt = (
                update(Trade)
                .where(Trade.id == trade_id, Trade.user_id == user_id)
                .values(**patch)
                .returning(Trade)
            )
            res = await self.db.execute(stmt)
            trade = res.scalar_one_or_none()
            if not trade:
                await self.db.rollback()
                return None
        else:
            # Se non ci sono campi da aggiornare, ricarica il trade (per coerenza con output)
            res = await self.db.execute(
                select(Trade).where(Trade.id == trade_id, Trade.user_id == user_id)
            )
            trade = res.scalars().first()
            if not trade:
                return None

        # 2) Se tag_names è presente, sostituisci i link
        if tag_names is not None:
            tag_ids = await self._ensure_tags_and_get_ids(user_id, tag_names)
            await self._replace_trade_tag_links(user_id, trade_id, tag_ids)

        await self.db.commit()
        await self.db.refresh(trade)
        return trade

    # ──────────────────────────────────────────────────────────────────────
    # DELETE
    # ──────────────────────────────────────────────────────────────────────
    async def delete(self, user_id: UUID, trade_id: UUID) -> bool:
        """
        Elimina il Trade (scoped per user_id). Ritorna True se almeno una riga è stata cancellata.
        Le righe nella tabella ponte vengono eliminate per ON DELETE CASCADE a livello DB.
        """
        stmt = delete(Trade).where(Trade.id == trade_id, Trade.user_id == user_id)
        res = await self.db.execute(stmt)
        await self.db.commit()
        return (res.rowcount or 0) > 0

    # ──────────────────────────────────────────────────────────────────────
    # CALENDAR DATA
    # ──────────────────────────────────────────────────────────────────────
    async def get_calendar_data(self, user_id: UUID) -> List[dict]:
        """
        Restituisce [{date: 'YYYY-MM-DD', pnl: float}, ...] aggregando per giorno (entry_timestamp)
        i P&L (p_l) dei trades dell'utente. Esclude i trade senza entry_timestamp.
        """
        day_alias = func.date_trunc("day", Trade.entry_timestamp).label("day")
        q = (
            select(day_alias, func.sum(Trade.p_l).label("daily_pnl"))
            .where(Trade.user_id == user_id)
            .where(Trade.entry_timestamp.is_not(None))
            .group_by(day_alias)
            .order_by(day_alias.asc())
        )
        res = await self.db.execute(q)
        rows = res.all()

        out = []
        for day, pnl in rows:
            # day è un datetime (00:00); serializza in 'YYYY-MM-DD'
            out.append({"date": day.date().isoformat(), "pnl": float(pnl or 0)})
        return out
