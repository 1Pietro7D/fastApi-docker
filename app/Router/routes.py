# app/Router/routes.py

from fastapi import APIRouter, Depends

# Auth dependency per proteggere gruppi di rotte
from app.Router.auth import require_roles

# Controller
from app.Controllers.users_controller import UsersController
from app.Controllers.roles_controller import RolesController
from app.Controllers.user_roles_controller import UserRolesController

# Schemi per response_model
from app.Schemas.auth_user import AuthUserRead
from app.Schemas.role import RoleRead
from app.Schemas.user_role import UserRoleRead

# Istanze controller (stateless)
users = UsersController()
roles = RolesController()
user_roles = UserRolesController()

# Router aggregatore
router = APIRouter()

# ───────────────────────────────
# 👥 USERS (protetto: admin)
# ───────────────────────────────
router_users = APIRouter(
    prefix="/api/v1/users",
    tags=["Users"],
    dependencies=[Depends(require_roles(["admin"]))],  # protezione a livello di gruppo
)

router_users.get("/", response_model=list[AuthUserRead])          (users.list_users)
router_users.get("/{user_id}", response_model=AuthUserRead)       (users.get_user)
router_users.post("/", response_model=AuthUserRead)               (users.create_user)
router_users.put("/{user_id}", response_model=AuthUserRead)       (users.update_user)
router_users.delete("/{user_id}")                                 (users.delete_user)

router.include_router(router_users)

# ───────────────────────────────
# 🛂 ROLES (protetto: admin)
# ───────────────────────────────
router_roles = APIRouter(
    prefix="/api/v1/roles",
    tags=["Roles"],
    dependencies=[Depends(require_roles(["admin"]))],
)

router_roles.get("/", response_model=list[RoleRead])              (roles.list_roles)
router_roles.get("/{role_id}", response_model=RoleRead)           (roles.get_role)
router_roles.post("/", response_model=RoleRead)                   (roles.create_role)
router_roles.put("/{role_id}", response_model=RoleRead)           (roles.update_role)
router_roles.delete("/{role_id}")                                 (roles.delete_role)

router.include_router(router_roles)

# ───────────────────────────────
# 🔗 USER ↔ ROLES (protetto: admin)
# ───────────────────────────────
router_user_roles = APIRouter(
    prefix="/api/v1",
    tags=["User-Roles"],
    dependencies=[Depends(require_roles(["admin"]))],
)

# Ora questa rotta ritorna direttamente i RUOLI dell'utente (non il ponte)
router_user_roles.get(
    "/users/{user_id}/roles",
    response_model=list[RoleRead],
)(user_roles.list_user_roles)

router_user_roles.post(
    "/users/assign-role",
    response_model=UserRoleRead,
)(user_roles.assign_role)

router_user_roles.delete(
    "/users/{user_id}/roles/{role_id}",
)(user_roles.unassign_role)

router.include_router(router_user_roles)
