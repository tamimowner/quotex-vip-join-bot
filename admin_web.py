"""
Web Admin Panel API.
Auth priority:
  1) Telegram WebApp initData → user id in ADMIN_IDS
  2) Optional fallback: ADMIN_WEB_TOKEN (browser only)
"""
from __future__ import annotations

import hashlib
import hmac
import json
import os
import time
from datetime import datetime
from typing import Any
from urllib.parse import parse_qsl

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

SESSION_TTL = 7 * 24 * 3600  # 7 days


def _session_secret() -> bytes:
    raw = (settings.BOT_TOKEN or "") + "|admin-session"
    return hashlib.sha256(raw.encode()).digest()


def _make_session(user_id: int) -> str:
    exp = int(time.time()) + SESSION_TTL
    payload = f"{user_id}:{exp}"
    sig = hmac.new(_session_secret(), payload.encode(), hashlib.sha256).hexdigest()[:32]
    return f"{payload}:{sig}"


def _verify_session(session: str | None) -> int | None:
    if not session or session.count(":") != 2:
        return None
    uid_s, exp_s, sig = session.split(":", 2)
    try:
        uid = int(uid_s)
        exp = int(exp_s)
    except ValueError:
        return None
    if exp < int(time.time()):
        return None
    payload = f"{uid}:{exp}"
    expect = hmac.new(_session_secret(), payload.encode(), hashlib.sha256).hexdigest()[:32]
    if not hmac.compare_digest(expect, sig):
        return None
    if uid not in settings.admin_ids:
        return None
    return uid


def _validate_webapp_init_data(init_data: str) -> dict[str, Any] | None:
    """Validate Telegram WebApp initData; return parsed user dict or None."""
    if not init_data or not settings.BOT_TOKEN:
        return None
    try:
        pairs = dict(parse_qsl(init_data, keep_blank_values=True))
    except Exception:
        return None
    received_hash = pairs.pop("hash", None)
    if not received_hash:
        return None
    data_check = "\n".join(f"{k}={v}" for k, v in sorted(pairs.items()))
    secret_key = hmac.new(b"WebAppData", settings.BOT_TOKEN.encode(), hashlib.sha256).digest()
    calc = hmac.new(secret_key, data_check.encode(), hashlib.sha256).hexdigest()
    if not hmac.compare_digest(calc, received_hash):
        return None
    # optional freshness (24h)
    try:
        auth_date = int(pairs.get("auth_date") or 0)
        if auth_date and abs(time.time() - auth_date) > 86400:
            return None
    except ValueError:
        pass
    user_raw = pairs.get("user")
    if not user_raw:
        return None
    try:
        return json.loads(user_raw)
    except Exception:
        return None


def _legacy_token() -> str:
    return (
        os.getenv("ADMIN_WEB_TOKEN", "")
        or os.getenv("POSTBACK_SECRET", "")
        or ""
    )


async def require_admin(
    request: Request,
    x_admin_session: str | None = Header(default=None, alias="X-Admin-Session"),
    x_admin_token: str | None = Header(default=None, alias="X-Admin-Token"),
    token: str | None = Query(default=None),
):
    # 1) Session from Telegram-verified login
    sess = x_admin_session or request.cookies.get("admin_session")
    uid = _verify_session(sess)
    if uid is not None:
        return uid

    # 2) Optional legacy token (browser fallback)
    expected = _legacy_token()
    got = x_admin_token or token or request.cookies.get("admin_token")
    if expected and got and hmac.compare_digest(str(got), str(expected)):
        return 0  # token auth, no specific user

    raise HTTPException(
        status_code=401,
        detail="Unauthorized — open Web App from Telegram /admin (ADMIN_IDS)",
    )


class TgAuthBody(BaseModel):
    init_data: str


class SettingBody(BaseModel):
    key: str
    value: str


class BulkSettingsBody(BaseModel):
    items: dict[str, str]


class MessageBody(BaseModel):
    key: str
    lang: str
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


@router.post("/api/auth/telegram")
async def api_auth_telegram(body: TgAuthBody):
    """Verify WebApp initData; only ADMIN_IDS may get a session."""
    user = _validate_webapp_init_data(body.init_data or "")
    if not user:
        raise HTTPException(401, "Invalid Telegram initData")
    try:
        uid = int(user.get("id") or 0)
    except (TypeError, ValueError):
        raise HTTPException(401, "Invalid user")
    if uid not in settings.admin_ids:
        raise HTTPException(403, f"Not an admin (id={uid}). Set ADMIN_IDS.")
    session = _make_session(uid)
    return {
        "ok": True,
        "session": session,
        "user": {
            "id": uid,
            "username": user.get("username"),
            "first_name": user.get("first_name"),
            "last_name": user.get("last_name"),
        },
    }


@router.get("/api/ping")
async def api_ping(admin_id: int = Depends(require_admin)):
    return {
        "ok": True,
        "service": "admin",
        "admin_id": admin_id,
        "time": datetime.utcnow().isoformat(),
    }


@router.get("/api/settings")
async def api_get_settings(_: int = Depends(require_admin)):
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
async def api_set_setting(body: SettingBody, _: int = Depends(require_admin)):
    key = body.key.strip()
    if not key:
        raise HTTPException(400, "key required")
    await set_setting(key, body.value)
    return {"ok": True, "key": key}


@router.post("/api/settings/bulk")
async def api_bulk_settings(body: BulkSettingsBody, _: int = Depends(require_admin)):
    for k, v in body.items.items():
        await set_setting(str(k).strip(), str(v))
    return {"ok": True, "count": len(body.items)}


@router.get("/api/messages")
async def api_get_messages(_: int = Depends(require_admin)):
    out = {}
    for key in MESSAGE_KEYS:
        for lang, defaults in (("bn", BN_TEXTS), ("en", EN_TEXTS)):
            sk = f"msg_{key}_{lang}"
            custom = await get_setting(sk, "")
            fallback = defaults.get(key, "")")
            out[sk] = custom if custom else fallback
            out[f"{sk}__source"] = "db" if custom else "locale"
    return {"keys": MESSAGE_KEYS, "messages": out}


@router.post("/api/messages")
async def api_set_message(body: MessageBody, _: int = Depends(require_admin)):
    lang = body.lang.lower()
    if lang not in ("bn", "en"):
        raise HTTPException(400, "lang must be bn or en")
    if body.key not in MESSAGE_KEYS:
        raise HTTPException(400, f"key must be one of {MESSAGE_KEYS}")
    sk = f"msg_{body.key}_{lang}"
    await set_setting(sk, body.value)
    return {"ok": True, "key": sk}


@router.get("/api/stats")
async def api_stats(_: int = Depends(require_admin)):
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
    _: int = Depends(require_admin),
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
async def api_ai_caption(body: CaptionRequest, _: int = Depends(require_admin)):
    topic = (body.topic or "VIP").strip()
    lang = body.lang if body.lang in ("bn", "en") else "bn"
    prem = body.include_tg_emoji
    err = None

    openai_key = os.getenv("OPENAI_API_KEY", "")
    if openai_key:
        try:
            import httpx

            system = (
                "You write Telegram bot messages in HTML parse_mode. "
                "Use <b>, <i>, <code>, <a href>, <tg-emoji emoji-id=\"ID\">fb</tg-emoji>. "
                "Under 800 chars. No markdown."
            )
            user_prompt = (
                f"Language: {lang}. Tone: {body.tone}. Topic: {topic}. "
                f"Premium tg-emoji: {prem}."
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

    if lang == "bn":
        html = (
            f'{_e("wave", prem)} <b>{topic}</b> {_e("spark", prem)}\n\n'
            f'{_e("megaphone", prem)} VIP চ্যানেলে যোগ দিতে নিচের ধাপগুলো ফলো করুন। {_e("down", prem)}\n\n'
            f'{_e("pin", prem)} আমাদের Affiliate Link দিয়ে অ্যাকাউন্ট খুলুন।\n\n'
            f'{_e("warn", prem)} শুধু 6–12 ডিজিটের Trader ID পাঠাবেন।'
        )
    else:
        html = (
            f'{_e("wave", prem)} Welcome to <b>{topic}</b>! {_e("spark", prem)}\n\n'
            f'{_e("megaphone", prem)} Follow the steps to join VIP. {_e("down", prem)}\n\n'
            f'{_e("pin", prem)} Open an account with our Affiliate Link.\n\n'
            f'{_e("warn", prem)} Send only a 6–12 digit Trader ID.'
        )
    return {"ok": True, "source": "template", "html": html, "note": err}


async def get_message_text(lang: str, key: str, **kwargs) -> str:
    lang = (lang or "bn").lower()
    if lang not in ("bn", "en"):
        lang = "bn"
    custom = await get_setting(f"msg_{key}_{lang}", "")
    text = custom if custom else get_text(lang, key)
    if kwargs:
        try:
            return text.format(**kwargs)
        except Exception:
            return text
    return text
