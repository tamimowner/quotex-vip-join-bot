from fastapi import FastAPI, Request
from fastapi.responses import PlainTextResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from datetime import datetime
from sqlalchemy import select
from database.models import User, PostbackLog
from database.db import async_session
from services.settings_store import get_min_deposit, get_vip_group_link
from locales import get_text
from config import settings
from aiogram import Bot
import json
import os

from admin_web import router as admin_router, get_message_text

app = FastAPI(title="Quotex Postback + Admin")
bot = Bot(token=settings.BOT_TOKEN)

# Web admin UI + API
app.include_router(admin_router)

_static_dir = os.path.join(os.path.dirname(__file__), "static")
if os.path.isdir(_static_dir):
    app.mount("/static", StaticFiles(directory=_static_dir), name="static")


@app.get("/")
@app.get("/health")
async def health():
    return JSONResponse({
        "status": "ok",
        "service": "quotex-vip-join-bot",
        "admin": "/admin",
    })


@app.api_route("/postback", methods=["GET", "POST"])
async def postback(request: Request):
    if request.method == "GET":
        params = dict(request.query_params)
    else:
        try:
            body = await request.json()
            params = body if isinstance(body, dict) else {}
        except Exception:
            form = await request.form()
            params = dict(form)

    status = params.get("status") or params.get("{status}") or ""
    click_id = params.get("cid") or params.get("click_id") or params.get("{click_id}") or ""
    trader_id = params.get("uid") or params.get("trader_id") or params.get("{trader_id}") or ""
    event_id = params.get("eid") or params.get("event_id") or params.get("{event_id}") or ""
    country = params.get("country") or params.get("{country}") or ""
    try:
        sumdep = float(params.get("sumdep") or params.get("{sumdep}") or 0)
    except (TypeError, ValueError):
        sumdep = 0.0
    try:
        sumwithdraw = float(params.get("sumwithdraw") or params.get("{sumwithdraw}") or 0)
    except (TypeError, ValueError):
        sumwithdraw = 0.0

    status = str(status).strip().lower()
    click_id = str(click_id).strip()
    trader_id = str(trader_id).strip()
    country = str(country).strip()

    print(f"POSTBACK: status={status} cid={click_id} uid={trader_id} sumdep={sumdep} country={country}")

    min_dep = await get_min_deposit()

    async with async_session() as session:
        log = PostbackLog(
            click_id=click_id or None,
            trader_id=trader_id or None,
            status=status or None,
            event_id=str(event_id) if event_id else None,
            sumdep=sumdep,
            sumwithdraw=sumwithdraw,
            country=country or None,
            raw_data=json.dumps(params, ensure_ascii=False),
        )
        session.add(log)
        await session.commit()

        user = None
        if click_id:
            try:
                telegram_id = int(click_id)
                result = await session.execute(
                    select(User).where(User.telegram_id == telegram_id)
                )
                user = result.scalar_one_or_none()
            except (ValueError, TypeError):
                pass

        if not user and trader_id:
            result = await session.execute(
                select(User).where(User.trader_id == trader_id)
            )
            user = result.scalar_one_or_none()

        if not user:
            return PlainTextResponse("OK", status_code=200)

        had_trader = bool(user.trader_id)
        prev_deposit = float(user.total_deposit or 0)

        if trader_id:
            user.trader_id = trader_id
        if country:
            user.country = country
        if sumdep > 0:
            user.total_deposit = prev_deposit + sumdep
            user.last_deposit = sumdep
        if sumwithdraw > 0:
            user.total_withdraw = float(user.total_withdraw or 0) + sumwithdraw
        if event_id:
            user.last_event_id = str(event_id)

        just_verified = False
        total_now = float(user.total_deposit or 0)
        reg_ok = status in ("reg", "registration", "register") and bool(trader_id)
        deposit_ok = total_now >= min_dep

        if not user.is_verified and (deposit_ok or (reg_ok and min_dep <= 0)):
            user.is_verified = True
            user.verified_at = datetime.utcnow()
            just_verified = True

        await session.commit()

        lang = user.language or "bn"

        try:
            if just_verified:
                vip_link = await get_vip_group_link()
                if vip_link:
                    await bot.send_message(
                        chat_id=user.telegram_id,
                        text=await get_message_text(lang, "invite_ready", link=vip_link),
                        parse_mode="HTML",
                        disable_web_page_preview=True,
                    )
                else:
                    await bot.send_message(
                        chat_id=user.telegram_id,
                        text=get_text(lang, "already_verified"),
                        parse_mode="HTML",
                    )
            elif not user.is_verified:
                if trader_id and (not had_trader or sumdep == 0):
                    await bot.send_message(
                        chat_id=user.telegram_id,
                        text=await get_message_text(
                            lang,
                            "account_created_success",
                            trader_id=trader_id,
                            min_deposit=int(min_dep),
                        ),
                        parse_mode="HTML",
                    )
                elif sumdep > 0 and total_now < min_dep:
                    await bot.send_message(
                        chat_id=user.telegram_id,
                        text=get_text(
                            lang,
                            "deposit_received_need_more",
                            amount=sumdep,
                            total=total_now,
                            min_deposit=int(min_dep),
                        ),
                        parse_mode="HTML",
                    )
        except Exception as e:
            print(f"Notify failed: {e}")

    return PlainTextResponse("OK", status_code=200)
