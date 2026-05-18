from fastapi import APIRouter

from app.api.v1.endpoints.auth import router as auth_router
from app.api.v1.endpoints.health import router as health_router
from app.api.v1.endpoints.rbac import router as rbac_router
from app.api.v1.endpoints.settings import router as settings_router
from app.api.v1.endpoints.tasks import router as tasks_router
from app.api.v1.endpoints.users import router as users_router

router = APIRouter()
router.include_router(health_router, tags=["health"])
router.include_router(auth_router, tags=["auth"])
router.include_router(rbac_router, tags=["rbac"])
router.include_router(settings_router, tags=["settings"])
router.include_router(tasks_router, tags=["tasks"])
router.include_router(users_router, prefix="/users", tags=["users"])
