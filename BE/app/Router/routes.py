# app/Router/routes.py
# Router aggregatore principale: Auth, Users, Roles, User↔Roles, Trades

from __future__ import annotations

from fastapi import APIRouter, Depends

# 🔒 Dipendenze per proteggere route con ruoli / autenticazione
from app.Router.auth import require_roles, get_current_claims

# 📦 Controller applicativi
from app.Controllers.users_controller import UsersController
from app.Controllers.roles_controller import RolesController
from app.Controllers.user_roles_controller import UserRolesController
from app.Controllers.auth_controller import AuthController
from app.Controllers.trades_controller import TradesController

# 📦 Schemi per le response (tipi Pydantic)
from app.Schemas.auth_user import AuthUserRead
from app.Schemas.role import RoleRead
from app.Schemas.trade import TradeRead
from app.Schemas.auth_session import (
    LoginResponse,
    RegisterResponse,
    LogoutResponse,
)

# Istanze controller (stateless)
users = UsersController()
roles = RolesController()
user_roles = UserRolesController()
auth = AuthController()
trades = TradesController()

# Router aggregatore principale
router = APIRouter()

# ───────────────────────────────
# 🔐 AUTH (pubblico per login/register; autenticato per logout)
# ───────────────────────────────
router_auth = APIRouter(
    prefix="/api/v1/auth",
    tags=["Auth"],
)

# LOGIN: password grant verso Supabase (in questa codebase → sempre service key)
router_auth.post("/login", response_model=LoginResponse)(auth.login)

# REGISTER: crea utente; in dev può auto-confermare email
router_auth.post("/register", response_model=RegisterResponse)(auth.register)

# LOGOUT: revoca refresh token dell'utente corrente (serve solo essere autenticati)
router_auth.post(
    "/logout",
    response_model=LogoutResponse,
    dependencies=[Depends(get_current_claims)],
)(auth.logout)

# monta il blocco auth nel router principale
router.include_router(router_auth)

# ───────────────────────────────
# 👥 USERS (protetto: admin)
# ───────────────────────────────
router_users = APIRouter(
    prefix="/api/v1/users",
    tags=["Users"],
    dependencies=[Depends(require_roles(["admin"]))],
)

router_users.get("/", response_model=list[AuthUserRead])(users.list_users)
router_users.get("/{user_id}", response_model=AuthUserRead)(users.get_user)
router_users.post("/", response_model=AuthUserRead)(users.create_user)
router_users.put("/{user_id}", response_model=AuthUserRead)(users.update_user)
router_users.delete("/{user_id}")(users.delete_user)

router.include_router(router_users)

# ───────────────────────────────
# 🛂 ROLES (protetto: admin)
# ───────────────────────────────
router_roles = APIRouter(
    prefix="/api/v1/roles",
    tags=["Roles"],
    dependencies=[Depends(require_roles(["admin"]))],
)

router_roles.get("/", response_model=list[RoleRead])(roles.list_roles)
router_roles.get("/{role_id}", response_model=RoleRead)(roles.get_role)
router_roles.post("/", response_model=RoleRead)(roles.create_role)
router_roles.put("/{role_id}", response_model=RoleRead)(roles.update_role)
router_roles.delete("/{role_id}")(roles.delete_role)

router.include_router(router_roles)

# ───────────────────────────────
# 🔗 USER ↔ ROLES (protetto: admin)
# ───────────────────────────────
router_user_roles = APIRouter(
    prefix="/api/v1",
    tags=["User-Roles"],
    dependencies=[Depends(require_roles(["admin"]))],
)

# Ritorna direttamente i RUOLI (RoleRead) assegnati all'utente
router_user_roles.get(
    "/users/{user_id}/roles",
    response_model=list[RoleRead],
)(user_roles.list_user_roles)

# Assegna un ruolo a un utente, e restituisce il ruolo assegnato
router_user_roles.post(
    "/users/assign-role",
    response_model=RoleRead,
)(user_roles.assign_role)

# Rimuove un ruolo da un utente
router_user_roles.delete(
    "/users/{user_id}/roles/{role_id}",
)(user_roles.unassign_role)

# monta il blocco user-roles nel router principale
router.include_router(router_user_roles)

# ───────────────────────────────
# 📈 TRADES (pubblico: nessuna dipendenza auth/ruoli)
# ───────────────────────────────
router_trades = APIRouter(
    prefix="/api/v1/trades",
    tags=["Trades"],
)

router_trades.get("/", response_model=list[TradeRead])(trades.list_trades)
router_trades.get("/{trade_id}", response_model=TradeRead)(trades.get_trade)
router_trades.post("/", response_model=TradeRead, status_code=201)(trades.create_trade)
router_trades.put("/{trade_id}", response_model=TradeRead)(trades.update_trade)
router_trades.get("/calendar/data")(trades.calendar_data)
router_trades.get("/performance/vantage-score")(trades.vantage_score)

router.include_router(router_trades)
