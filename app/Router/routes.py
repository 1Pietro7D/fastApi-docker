from fastapi import APIRouter, Depends
from app.Controllers.roles_controller import RolesController
from app.Controllers.user_roles_controller import UserRolesController
from app.Controllers.users_controller import UsersController
from app.Router.auth import require_roles

roles = RolesController()
user_roles = UserRolesController()
users = UsersController()

router = APIRouter(prefix="/api/v1")

# Roles (admin)
router.get("/roles")(roles.list_roles)
router.get("/roles/{role_id}")(roles.get_role)
router.post("/roles")(roles.create_role)
router.put("/roles/{role_id}")(roles.update_role)
router.delete("/roles/{role_id}")(roles.delete_role)

# Role assignments (admin)
router.get("/users/{user_id}/roles")(user_roles.list_user_roles)
router.post("/users/assign-role")(user_roles.assign_role)
router.delete("/users/{user_id}/roles/{role_id}")(user_roles.unassign_role)

# Users (admin)
router.get("/users")(users.list_users)
router.get("/users/{user_id}")(users.get_user)
router.post("/users")(users.create_user)           # crea via Supabase service
router.put("/users/{user_id}")(users.update_user)
router.delete("/users/{user_id}")(users.delete_user)
