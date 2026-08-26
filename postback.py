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

        if not click_id or sumdep <= 0:
            return PlainTextResponse("OK", status_code=200)

        try:
            telegram_id = int(click_id)
        except (ValueError, TypeError):
            return PlainTextResponse("OK", status_code=200)

        result = await session.execute(
            select(User).where(User.telegram_id == telegram_id)
        )
        user = result.scalar_one_or_none()

        if not user:
            return PlainTextResponse("OK", status_code=200)

        user.trader_id = str(trader_id) if trader_id else user.trader_id
        user.country = str(country) if country else user.country
        user.total_deposit = (user.total_deposit or 0) + sumdep
        user.total_withdraw = (user.total_withdraw or 0) + sumwithdraw
        user.last_deposit = sumdep
        user.last_event_id = str(event_id) if event_id else user.last_event_id

        just_verified = False
        if not user.is_verified and sumdep > 0:
            user.is_verified = True
            user.verified_at = datetime.utcnow()
            just_verified = True

        await session.commit()

        if just_verified:
            invite_link = await create_unique_invite(bot, telegram_id)
            if invite_link:
                lang = user.language or "bn"
                try:
                    await bot.send_message(
                        chat_id=telegram_id,
                        text=get_text(lang, "invite_ready", link=invite_link),
                        parse_mode="HTML",
                        disable_web_page_preview=True,
                    )
                except Exception as e:
                    print(f"Failed to send invite to {telegram_id}: {e}")

    return PlainTextResponse("OK", status_code=200)
