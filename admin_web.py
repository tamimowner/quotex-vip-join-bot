"""
Web Admin Panel API for Quotex VIP Join Bot.
URL: /admin  (HTML)  |  /admin/api/*  (JSON)
Auth: header X-Admin-Token or query ?token=  (ADMIN_WEB_TOKEN env)
"""
from __future__ import annotations

import os
from datetime import datetime
from typing import Any

from fastapi import APIRouter, Depends, Header, HTTPException, Query, Request
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from sqlalchemy import select, func, desc

from config import settings
from database.db import async_session
from database.models import User, PostbackLog
from services.settings_store import (
    get_setting,
    set_setting,
    get_min_deposit,
    get_vip_group_link,
    get_affiliate_url,
    BUTTON_KEYS,
    DEFAULTS,
)
from locales import get_text
from locales.bn import TEXTS as BN_TEXTS
from locales.en import TEXTS as EN_TEXTS

router = APIRouter(prefix="/admin", tags=["admin"])

# All user-facing captions / page bodies (HTML + tg-emoji)
MESSAGE_KEYS = [
    "welcome",
    "premium_info",
    "invite_ready",
    "not_from_our_link",
    "account_created_success",
    "need_deposit_hint",
    "deposit_received_need_more",
    "create_account_guide",
    "delete_account_guide",
    "support",
    "settings_title",
    "choose_language",
    "language_set",
    "invalid_trader_id",
    "trader_id_saved",
    "waiting_deposit",
    "already_verified",
    "already_joined",
    "status_title",
    "status_not_verified",
    "status_verified",
    "status_full",
    "history_title",
    "history_empty",
    "public_channel",
]

SETTING_KEYS = [
    "affiliate_link_base",
    "vip_group_link",
    "min_deposit",
    "site_id",
    "public_channel",
    "support_text_bn",
    "support_text_en",
    "welcome_photo_url",
]


def _admin_token() -> str:
    return (
        getattr(settings, "ADMIN_WEB_TOKEN", None)
        or os.getenv("ADMIN_WEB_TOKEN", "")
        or os.getenv("POSTBACK_SECRET", "")
        or "changeme"
    )


async def require_admin(
    request: Request,
    x_admin_token: str | None = Header(default=None, alias="X-Admin-Token"),
    token: str | None = Query(default=None),
):
    expected = _admin_token()
    got = x_admin_token or token or request.cookies.get("admin_token")
    if got != expected:
        raise HTTPException(status_code=401, detail="Unauthorized — set X-Admin-Token or ?token=")
    return True


class SettingBody(BaseModel):
    key: str
    value: str


class BulkSettingsBody(BaseModel):
    items: dict[str, str]


class MessageBody(BaseModel):
    key: str
    lang: str  # bn | en
    value: str


class CaptionRequest(BaseModel):
    topic: str = "VIP join"
    lang: str = "bn"
    tone: str = "friendly"
    include_tg_emoji: bool = True


@router.get("", response_class=HTMLResponse)
@router.get("/", response_class=HTMLResponse)
async def admin_page():
    path = os.path.join(os.path.dirname(__file__), "static", "admin", "index.html")
    if not os.path.isfile(path):
        return HTMLResponse("<h1>Admin UI missing</h1>", status_code=500)
    with open(path, "r", encoding="utf-8") as f:
        return HTMLResponse(f.read())


@router.get("/api/ping")
async def api_ping(_: bool = Depends(require_admin)):
    return {"ok": True, "service": "admin", "time": datetime.utcnow().isoformat()}


@router.get("/api/settings")
async def api_get_settings(_: bool = Depends(require_admin)):
    data: dict[str, Any] = {}
    for k in SETTING_KEYS:
        data[k] = await get_setting(k, DEFAULTS.get(k, ""))
    data["min_deposit"] = str(await get_min_deposit())
    data["vip_group_link"] = await get_vip_group_link()
    data["affiliate_link_preview"] = await get_affiliate_url()
    buttons = {}
    for bk in BUTTON_KEYS:
        buttons[f"{bk}_bn"] = await get_setting(f"{bk}_bn", "") or get_text("bn", bk)
        buttons[f"{bk}_en"] = await get_setting(f"{bk}_en", "") or get_text("en", bk)
        buttons[f"style_{bk}"] = await get_setting(f"style_{bk}", "primary")
        buttons[f"icon_{bk}"] = await get_setting(f"icon_{bk}", "")
    data["buttons"] = buttons
    return data


@router.post("/api/settings")
async def api_set_setting(body: SettingBody, _: bool = Depends(require_admin)):
    key = body.key.strip()
    if not key:
        raise HTTPException(400, "key required")
    await set_setting(key, body.value)
    return {"ok": True, "key": key}


@router.post("/api/settings/bulk")
async def api_bulk_settings(body: BulkSettingsBody, _: bool = Depends(require_admin)):
    for k, v in body.items.items():
        await set_setting(str(k).strip(), str(v))
    return {"ok": True, "count": len(body.items)}


@router.get("/api/messages")
async def api_get_messages(_: bool = Depends(require_admin)):
    out = {}
    for key in MESSAGE_KEYS:
        for lang, defaults in (("bn", BN_TEXTS), ("en", EN_TEXTS)):
            sk = f"msg_{key}_{lang}"
            custom = await get_setting(sk, "")
            fallback = defaults.get(key, "")
            out[sk] = custom if custom else fallback
            out[f"{sk}__source"] = "db" if custom else "locale"
    return {"keys": MESSAGE_KEYS, "messages": out}


@router.post("/api/messages")
async def api_set_message(body: MessageBody, _: bool = Depends(require_admin)):
    lang = body.lang.lower()
    if lang not in ("bn", "en"):
        raise HTTPException(400, "lang must be bn or en")
    if body.key not in MESSAGE_KEYS:
        raise HTTPException(400, f"key must be one of {MESSAGE_KEYS}")
    sk = f"msg_{body.key}_{lang}"
    await set_setting(sk, body.value)
    return {"ok": True, "key": sk}


@router.get("/api/stats")
async def api_stats(_: bool = Depends(require_admin)):
    async with async_session() as session:
        total = await session.scalar(select(func.count()).select_from(User)) or 0
        verified = await session.scalar(
            select(func.count()).select_from(User).where(User.is_verified.is_(True))
        ) or 0
        joined = await session.scalar(
            select(func.count()).select_from(User).where(User.has_joined.is_(True))
        ) or 0
        posts = await session.scalar(select(func.count()).select_from(PostbackLog)) or 0
        deposits = await session.scalar(
            select(func.coalesce(func.sum(User.total_deposit), 0))
        ) or 0
    return {
        "total_users": total,
        "verified": verified,
        "joined": joined,
        "postbacks": posts,
        "total_deposit": float(deposits),
        "min_deposit": await get_min_deposit(),
    }


@router.get("/api/users")
async def api_users(
    limit: int = Query(30, ge=1, le=100),
    _: bool = Depends(require_admin),
):
    async with async_session() as session:
        result = await session.execute(
            select(User).order_by(desc(User.id)).limit(limit)
        )
        users = result.scalars().all()
    return {
        "users": [
            {
                "id": u.id,
                "telegram_id": u.telegram_id,
                "username": u.username,
                "full_name": u.full_name,
                "language": u.language,
                "trader_id": u.trader_id,
                "country": u.country,
                "total_deposit": u.total_deposit,
                "is_verified": u.is_verified,
                "has_joined": u.has_joined,
                "created_at": u.created_at.isoformat() if u.created_at else None,
            }
            for u in users
        ]
    }


TG_EMOJIS = {
    "wave": ('<tg-emoji emoji-id="5188481279963715781">👋</tg-emoji>', "👋"),
    "spark": ('<tg-emoji emoji-id="5879757713658875847">✨</tg-emoji>', "✨"),
    "megaphone": ('<tg-emoji emoji-id="5215174853895660531">📢</tg-emoji>', "📢"),
    "down": ('<tg-emoji emoji-id="6300954126901577963">👇</tg-emoji>', "👇"),
    "pin": ('<tg-emoji emoji-id="5397782960512444700">📌</tg-emoji>', "📌"),
    "warn": ('<tg-emoji emoji-id="5420323339723881652">⚠️</tg-emoji>', "⚠️"),
}


def _e(name: str, premium: bool) -> str:
    prem, plain = TG_EMOJIS.get(name, ("✨", "✨"))
    return prem if premium else plain


@router.post("/api/ai/caption")
async def api_ai_caption(body: CaptionRequest, _: bool = Depends(require_admin)):
    topic = (body.topic or "VIP").strip()
    lang = body.lang if body.lang in ("bn", "en") else "bn"
    prem = body.include_tg_emoji

    openai_key = os.getenv("OPENAI_API_KEY", "")
    if openai_key:
        try:
            import httpx

            system = (
                "You write Telegram bot messages in HTML parse_mode. "
                "You may use <b>, <i>, <code>, <a href>, and "
                "<tg-emoji emoji-id=\"ID\">fallback</tg-emoji>. "
                "Keep under 800 chars. No markdown."
            )
            user_prompt = (
                f"Language: {lang}. Tone: {body.tone}. Topic: {topic}. "
                f"Include premium tg-emoji: {prem}. "
                "Known emoji ids: wave 5188481279963715781, spark 5879757713658875847, "
                "megaphone 5215174853895660531, down 6300954126901577963, "
                "pin 5397782960512444700, warn 5420323339723881652."
            )
            async with httpx.AsyncClient(timeout=30) as client:
                r = await client.post(
                    "https://api.openai.com/v1/chat/completions",
                    headers={"Authorization": f"Bearer {openai_key}"},
                    json={
                        "model": os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
                        "messages": [
                            {"role": "system", "content": system},
                            {"role": "user", "content": user_prompt},
                        ],
                        "temperature": 0.7,
                    },
                )
                r.raise_for_status()
                text = r.json()["choices"][0]["message"]["content"].strip()
                return {"ok": True, "source": "openai", "html": text}
        except Exception as e:
            err = str(e)
    else:
        err = None

    if lang == "bn":
        html = (
            f'{_e("wave", prem)} <b>{topic}</b> {_e("spark", prem)}\n\n'
            f'{_e("megaphone", prem)} VIP চ্যানেলে যোগ দিতে নিচের ধাপগুলো ফলো করুন। {_e("down", prem)}\n\n'
            f'{_e("pin", prem)} আমাদের Affiliate Link দিয়ে অ্যাকাউন্ট খুলুন, Verify করুন, '
            f'তারপর বটে <b>Trader ID</b> পাঠান।\n\n'
            f'{_e("warn", prem)} শুধু 6–12 ডিজিটের ইংরেজি Trader ID পাঠাবেন।'
        )
    else:
        html = (
            f'{_e("wave", prem)} Welcome to <b>{topic}</b>! {_e("spark", prem)}\n\n'
            f'{_e("megaphone", prem)} Follow the steps below to join VIP. {_e("down", prem)}\n\n'
            f'{_e("pin", prem)} Open an account with our Affiliate Link, verify, '
            f'then send your <b>Trader ID</b> to the bot.\n\n'
            f'{_e("warn", prem)} Send only a 6–12 digit English Trader ID.'
        )
    return {"ok": True, "source": "template", "html": html, "note": err}


async def get_message_text(lang: str, key: str, **kwargs) -> str:
    """Prefer DB override msg_{key}_{lang}, else locale file."""
    lang = (lang or "bn").lower()
    if lang not in ("bn", "en"):
        lang = "bn"
    custom = await get_setting(f"msg_{key}_{lang}", "")
    if custom:
        text = custom
    else:
        text = get_text(lang, key)
    if kwargs:
        try:
            return text.format(**kwargs)
        except Exception:
            return text
    return text
