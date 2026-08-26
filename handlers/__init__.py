from aiogram import Router
from handlers.start import router as start_router
from handlers.menu import router as menu_router


def setup_routers() -> Router:
    root = Router()
    root.include_router(start_router)
    root.include_router(menu_router)
    return root
