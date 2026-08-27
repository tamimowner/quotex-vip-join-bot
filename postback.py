from fastapi import FastAPI, Request
from fastapi.responses import PlainTextResponse, JSONResponse
from datetime import datetime
from sqlalchemy import select
from database.models import User, PostbackLog
from database.db import async_session
from services.settings_store import get_min_deposit, get_vip_group_link
from locales import get_text
from config import settings
from aiogram import Bot
import json

app = FastAPI(title="Quotex Postback Receiver")
bot = Bot(token=settings.BOT_TOKEN)


@app.get("/")
@app.get("/health")
async def health():
    return JSONResponse({"status": "ok", "service": "quotex-vip-join-bot"})


@app.api_route("/postback", methods=["GET", "POST"])
async def postback(request: Request):
    """
    Quotex Partner Postback receiver (PHP-style logic).

    - Always saves every postback to postback_logs
    - Matches user by click_id (Telegram ID) or trader_id
    - On reg / deposit → marks verified when min_deposit met (default 0 = reg is enough)
    - Does NOT auto-send unique invite; user sends Trader ID in bot to get static VIP link
    """
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
        # 1) Always log
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

        # 2) Try match existing Telegram user
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
            # No Telegram user yet — log is enough.
            # User will send Trader ID later in the bot (PHP style).
            return PlainTextResponse("OK", status_code=200)

        # 3) Update user fields
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

        # Verify when deposit reaches min (min_deposit=0 means reg is enough)
        just_verified = False
        total_now = float(user.total_deposit or 0)

        # PHP style: status=reg alone can verify when min_deposit <= 0
        reg_ok = status in ("reg", "registration", "register") and bool(trader_id)
        deposit_ok = total_now >= min_dep

        if not user.is_verified and (deposit_ok or (reg_ok and min_dep <= 0)):
            user.is_verified = True
            user.verified_at = datetime.utcnow()
            just_verified = True

        await session.commit()

        lang = user.language or "bn"

        # 4) Optional notify (no unique invite — user must send Trader ID for link)
        try:
            if just_verified:
                vip_link = await get_vip_group_link()
                if vip_link:
                    await bot.send_message(
                        chat_id=user.telegram_id,
                        text=get_text(lang, "invite_ready", link=vip_link),
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
                        text=get_text(
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
