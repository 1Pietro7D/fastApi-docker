# app/Router/routes.py

from fastapi import APIRouter, Depends
from app.Controllers.roles_controller import RolesController
from app.Controllers.user_roles_controller import UserRolesController
from app.Controllers.users_controller import UsersController
from app.Router.auth import require_roles

# Controller istanziati
roles = RolesController()
user_roles = UserRolesController()
users = UsersController()

# Router principale
router = APIRouter()

# ───────────────────────────────
#  USERS
# ───────────────────────────────
router_users = APIRouter(
    prefix="/api/v1/users",
    tags=["Users"],
    dependencies=[Depends(require_roles(["admin"]))],
)

router_users.get("/")                       (users.list_users)
router_users.get("/{user_id}")              (users.get_user)
router_users.post("/")                      (users.create_user)
router_users.put("/{user_id}")              (users.update_user)
router_users.delete("/{user_id}")           (users.delete_user)

router.include_router(router_users)

# ───────────────────────────────
#  ROLES
# ───────────────────────────────
router_roles = APIRouter(
    prefix="/api/v1/roles",
    tags=["Roles"],
    dependencies=[Depends(require_roles(["admin"]))],
)

router_roles.get("/")                       (roles.list_roles)
router_roles.get("/{role_id}")              (roles.get_role)
router_roles.post("/")                      (roles.create_role)
router_roles.put("/{role_id}")              (roles.update_role)
router_roles.delete("/{role_id}")           (roles.delete_role)

router.include_router(router_roles)

# ───────────────────────────────
#  USER ↔ ROLES
# ───────────────────────────────
router_user_roles = APIRouter(
    prefix="/api/v1",
    tags=["User-Roles"],
    dependencies=[Depends(require_roles(["admin"]))],
)

router_user_roles.get("/users/{user_id}/roles")                 (user_roles.list_user_roles)
router_user_roles.post("/users/assign-role")                    (user_roles.assign_role)
router_user_roles.delete("/users/{user_id}/roles/{role_id}")    (user_roles.unassign_role)

router.include_router(router_user_roles)
