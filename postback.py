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


def _pick(params: dict, *keys: str) -> str:
    """First non-empty value among keys (case-insensitive key match)."""
    lower_map = {str(k).lower(): v for k, v in params.items()}
    for key in keys:
        v = params.get(key)
        if v is None:
            v = lower_map.get(key.lower())
        if v is None:
            continue
        s = str(v).strip()
        if s and s not in ("{status}", "{click_id}", "{trader_id}", "{event_id}", "{country}", "{sumdep}", "{sumwithdraw}"):
            return s
    return ""


@app.get("/")
@app.get("/health")
async def health():
    return JSONResponse({
        "status": "ok",
        "service": "quotex-vip-join-bot",
        "admin": "/admin",
        "postback": "/postback",
    })


@app.api_route("/postback", methods=["GET", "POST"])
@app.api_route("/pb", methods=["GET", "POST"])
@app.api_route("/callback", methods=["GET", "POST"])
async def postback(request: Request):
    if request.method == "GET":
        params = dict(request.query_params)
    else:
        params = {}
        # JSON body
        try:
            body = await request.json()
            if isinstance(body, dict):
                params.update(body)
        except Exception:
            pass
        # form body
        try:
            form = await request.form()
            params.update(dict(form))
        except Exception:
            pass
        # also merge query string on POST
        params.update(dict(request.query_params))

    status = _pick(params, "status", "{status}", "event", "type", "action").lower()
    click_id = _pick(params, "cid", "click_id", "clickid", "{click_id}", "subid", "sub_id", "s1")
    trader_id = _pick(
        params,
        "uid", "trader_id", "traderid", "traderId", "user_id", "userid",
        "{trader_id}", "account_id", "accountid",
    )
    event_id = _pick(params, "eid", "event_id", "eventid", "{event_id}", "id")
    country = _pick(params, "country", "{country}", "geo", "cc")

    raw_sumdep = _pick(params, "sumdep", "{sumdep}", "deposit", "amount", "sum", "dep", "profit")
    raw_sumwd = _pick(params, "sumwithdraw", "{sumwithdraw}", "withdraw", "withdrawal")
    try:
        sumdep = float(raw_sumdep or 0)
    except (TypeError, ValueError):
        sumdep = 0.0
    try:
        sumwithdraw = float(raw_sumwd or 0)
    except (TypeError, ValueError):
        sumwithdraw = 0.0

    print(
        f"POSTBACK hit method={request.method} "
        f"status={status!r} cid={click_id!r} uid={trader_id!r} "
        f"sumdep={sumdep} country={country!r} keys={list(params.keys())}"
    )

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
            raw_data=json.dumps(params, ensure_ascii=False, default=str),
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
            # Still OK — log saved; user can link later by sending trader_id
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
        reg_ok = status in ("reg", "registration", "register", "signup", "sign_up") and bool(trader_id)
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
