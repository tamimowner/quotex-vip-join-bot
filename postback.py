"""Quotex Partner postback receiver only (no web admin panel)."""
from fastapi import FastAPI, Request
from fastapi.responses import PlainTextResponse, JSONResponse
from datetime import datetime
from sqlalchemy import select
from database.models import User, PostbackLog
from database.db import async_session
from services.settings_store import get_min_deposit, get_vip_group_link
from services.messages import get_message_text
from locales import get_text
from config import settings
from aiogram import Bot
import json
import traceback

app = FastAPI(title="Quotex VIP Postback")
bot = Bot(token=settings.BOT_TOKEN)


def _pick(params: dict, *keys: str) -> str:
    lower_map = {str(k).lower(): v for k, v in params.items()}
    for key in keys:
        v = params.get(key)
        if v is None:
            v = lower_map.get(key.lower())
        if v is None:
            continue
        s = str(v).strip()
        if s and s not in (
            "{status}",
            "{click_id}",
            "{trader_id}",
            "{event_id}",
            "{country}",
            "{sumdep}",
            "{sumwithdraw}",
            "{uid}",
            "{cid}",
            "{eid}",
            "{lid}",
            "{site_id}",
            "{sid}",
        ):
            return s
    return ""


async def _read_params(request: Request) -> dict:
    params: dict = {}
    params.update(dict(request.query_params))
    if request.method == "POST":
        try:
            body = await request.json()
            if isinstance(body, dict):
                params.update(body)
                return params
        except Exception:
            pass
        try:
            form = await request.form()
            params.update({k: str(v) for k, v in dict(form).items()})
        except Exception:
            pass
        try:
            raw = await request.body()
            if raw:
                from urllib.parse import parse_qsl

                text = raw.decode("utf-8", errors="ignore")
                if text and "=" in text and not text.strip().startswith("{"):
                    params.update(dict(parse_qsl(text, keep_blank_values=True)))
        except Exception:
            pass
    return params


@app.get("/")
@app.get("/health")
async def health():
    return JSONResponse(
        {
            "status": "ok",
            "service": "quotex-vip-join-bot",
            "postback": "/postback",
            "admin": "Telegram /admin command only",
            "test": "/postback?status=reg&uid=TEST999&sumdep=0",
        }
    )


@app.api_route("/postback", methods=["GET", "POST", "HEAD"])
@app.api_route("/pb", methods=["GET", "POST", "HEAD"])
@app.api_route("/callback", methods=["GET", "POST", "HEAD"])
@app.api_route("/postback.php", methods=["GET", "POST", "HEAD"])
async def postback(request: Request):
    if request.method == "HEAD":
        return PlainTextResponse("OK", status_code=200)

    try:
        params = await _read_params(request)
    except Exception as e:
        print(f"POSTBACK param read error: {e}")
        params = dict(request.query_params)

    status = _pick(params, "status", "event", "type", "action").lower()
    click_id = _pick(
        params, "cid", "click_id", "clickid", "subid", "sub_id", "s1", "click"
    )
    trader_id = _pick(
        params,
        "uid",
        "trader_id",
        "traderid",
        "traderId",
        "user_id",
        "userid",
        "account_id",
        "accountid",
        "trader",
    )
    event_id = _pick(params, "eid", "event_id", "eventid", "id")
    country = _pick(params, "country", "geo", "cc")
    lid = _pick(params, "lid", "link_id")

    raw_sumdep = _pick(
        params, "sumdep", "deposit", "amount", "sum", "dep", "profit", "value"
    )
    raw_sumwd = _pick(params, "sumwithdraw", "withdraw", "withdrawal")
    try:
        sumdep = float(raw_sumdep or 0)
    except (TypeError, ValueError):
        sumdep = 0.0
    try:
        sumwithdraw = float(raw_sumwd or 0)
    except (TypeError, ValueError):
        sumwithdraw = 0.0

    print(
        f"POSTBACK hit method={request.method} status={status!r} "
        f"cid={click_id!r} uid={trader_id!r} lid={lid!r} sumdep={sumdep} "
        f"keys={list(params.keys())}"
    )

    try:
        min_dep = await get_min_deposit()
    except Exception as e:
        print(f"get_min_deposit failed: {e}")
        min_dep = 0.0

    try:
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
                print(
                    f"POSTBACK saved log only (no user match) "
                    f"uid={trader_id!r} cid={click_id!r}"
                )
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
            reg_ok = status in (
                "reg",
                "registration",
                "register",
                "signup",
                "sign_up",
                "email",
                "email_confirm",
                "email_confirmation",
            ) and bool(trader_id)
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
                            text=await get_message_text(
                                lang, "invite_ready", link=vip_link
                            ),
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

    except Exception:
        print("POSTBACK processing error:")
        traceback.print_exc()

    return PlainTextResponse("OK", status_code=200)
