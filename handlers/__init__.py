from aiogram import Router
from handlers.start import router as start_router
from handlers.menu import router as menu_router
from handlers.chat_member import router as chat_member_router
from handlers.admin import router as admin_router


def setup_routers() -> Router:
    root = Router()
    root.include_router(admin_router)  # admin first for pending text capture
    root.include_router(start_router)
    root.include_router(menu_router)
    root.include_router(chat_member_router)
    return root
