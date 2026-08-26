from fastapi import FastAPI, Request
from fastapi.responses import PlainTextResponse, JSONResponse
from datetime import datetime
from sqlalchemy import select
from database.models import User, PostbackLog
from database.db import async_session
from services.invite import create_unique_invite
from locales import get_text
from config import settings
from aiogram import Bot
import json

app = FastAPI(title="Quotex Postback Receiver")
bot = Bot(token=settings.BOT_TOKEN)

MIN_DEPOSIT = 20.0


@app.get("/")
@app.get("/health")
async def health():
    return JSONResponse({"status": "ok", "service": "quotex-vip-join-bot"})


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

    status = params.get("status") or params.get("{status}")
    click_id = params.get("cid") or params.get("click_id") or params.get("{click_id}")
    trader_id = params.get("uid") or params.get("trader_id") or params.get("{trader_id}")
    event_id = params.get("eid") or params.get("event_id") or params.get("{event_id}")
    country = params.get("country") or params.get("{country}")
    sumdep = float(params.get("sumdep") or params.get("{sumdep}") or 0)
    sumwithdraw = float(params.get("sumwithdraw") or params.get("{sumwithdraw}") or 0)

    print(f"POSTBACK: status={status} cid={click_id} uid={trader_id} sumdep={sumdep}")

    async with async_session() as session:
        log = PostbackLog(
            click_id=str(click_id) if click_id else None,
            trader_id=str(trader_id) if trader_id else None,
            status=str(status) if status else None,
            event_id=str(event_id) if event_id else None,
            sumdep=sumdep,
            sumwithdraw=sumwithdraw,
            country=str(country) if country else None,
            raw_data=json.dumps(params, ensure_ascii=False),
        )
        session.add(log)
        await session.commit()

        # Find user by click_id (telegram id) OR by trader_id already saved
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
                select(User).where(User.trader_id == str(trader_id))
            )
            user = result.scalar_one_or_none()

        if not user:
            return PlainTextResponse("OK", status_code=200)

        if trader_id:
            user.trader_id = str(trader_id)
        if country:
            user.country = str(country)
        if sumdep > 0:
            user.total_deposit = (user.total_deposit or 0) + sumdep
            user.last_deposit = sumdep
        if sumwithdraw > 0:
            user.total_withdraw = (user.total_withdraw or 0) + sumwithdraw
        if event_id:
            user.last_event_id = str(event_id)

        just_verified = False
        if not user.is_verified and (user.total_deposit or 0) >= MIN_DEPOSIT:
            user.is_verified = True
            user.verified_at = datetime.utcnow()
            just_verified = True

        await session.commit()

        if just_verified and not user.has_joined:
            invite_link = await create_unique_invite(bot, user.telegram_id)
            if invite_link:
                lang = user.language or "bn"
                try:
                    await bot.send_message(
                        chat_id=user.telegram_id,
                        text=get_text(lang, "invite_ready", link=invite_link),
                        parse_mode="HTML",
                        disable_web_page_preview=True,
                    )
                except Exception as e:
                    print(f"Failed to send invite to {user.telegram_id}: {e}")

    return PlainTextResponse("OK", status_code=200)
