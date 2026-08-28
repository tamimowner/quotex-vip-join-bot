"""
Web Admin Panel — normal website login (username + password).
Env:
  ADMIN_USERNAME (default: admin)
  ADMIN_PASSWORD (required for security; fallback ADMIN_WEB_TOKEN)
"""
from __future__ import annotations

import hashlib
import hmac
import os
import secrets
import time
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

SESSION_TTL = 7 * 24 * 3600


def _admin_username() -> str:
    return (os.getenv("ADMIN_USERNAME") or "admin").strip()


def _admin_password() -> str:
    return (
        (os.getenv("ADMIN_PASSWORD") or "").strip()
        or (os.getenv("ADMIN_WEB_TOKEN") or "").strip()
        or (os.getenv("POSTBACK_SECRET") or "").strip()
    )


def _session_secret() -> bytes:
    raw = (settings.BOT_TOKEN or "") + "|" + _admin_password() + "|admin-web"
    return hashlib.sha256(raw.encode()).digest()


def _make_session(username: str) -> str:
    exp = int(time.time()) + SESSION_TTL
    nonce = secrets.token_hex(8)
    payload = f"{username}:{exp}:{nonce}"
    sig = hmac.new(_session_secret(), payload.encode(), hashlib.sha256).hexdigest()[:40]
    return f"{payload}:{sig}"


def _verify_session(session: str | None) -> str | None:
    if not session:
        return None
    parts = session.split(":")
    if len(parts) != 4:
        return None
    username, exp_s, nonce, sig = parts
    try:
        exp = int(exp_s)
    except ValueError:
        return None
    if exp < int(time.time()):
        return None
    payload = f"{username}:{exp}:{nonce}"
    expect = hmac.new(_session_secret(), payload.encode(), hashlib.sha256).hexdigest()[:40]
    if not hmac.compare_digest(expect, sig):
        return None
    if not hmac.compare_digest(username, _admin_username()):
        return None
    return username


async def require_admin(
    request: Request,
    x_admin_session: str | None = Header(default=None, alias="X-Admin-Session"),
):
    sess = x_admin_session or request.cookies.get("admin_session")
    user = _verify_session(sess)
    if user:
        return user
    raise HTTPException(status_code=401, detail="Unauthorized — login required")


class LoginBody(BaseModel):
    username: str
    password: str


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


@router.post("/api/auth/login")
async def api_auth_login(body: LoginBody):
    expected_user = _admin_username()
    expected_pass = _admin_password()
    if not expected_pass:
        raise HTTPException(
            500,
            "ADMIN_PASSWORD not set on server. Set ADMIN_PASSWORD in Railway env.",
        )
    ok_user = hmac.compare_digest((body.username or "").strip(), expected_user)
    ok_pass = hmac.compare_digest((body.password or "").strip(), expected_pass)
    if not (ok_user and ok_pass):
        raise HTTPException(401, "Wrong username or password")
    session = _make_session(expected_user)
    return {
        "ok": True,
        "session": session,
        "user": {"username": expected_user},
    }


@router.post("/api/auth/logout")
async def api_auth_logout():
    return {"ok": True}


@router.get("/api/ping")
async def api_ping(admin: str = Depends(require_admin)):
    return {
        "ok": True,
        "service": "admin",
        "user": admin,
        "time": datetime.utcnow().isoformat(),
    }


@router.get("/api/settings")
async def api_get_settings(_: str = Depends(require_admin)):
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
async def api_set_setting(body: SettingBody, _: str = Depends(require_admin)):
    key = body.key.strip()
    if not key:
        raise HTTPException(400, "key required")
    await set_setting(key, body.value)
    return {"ok": True, "key": key}


@router.post("/api/settings/bulk")
async def api_bulk_settings(body: BulkSettingsBody, _: str = Depends(require_admin)):
    for k, v in body.items.items():
        await set_setting(str(k).strip(), str(v))
    return {"ok": True, "count": len(body.items)}


@router.get("/api/messages")
async def api_get_messages(_: str = Depends(require_admin)):
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
async def api_set_message(body: MessageBody, _: str = Depends(require_admin)):
    lang = body.lang.lower()
    if lang not in ("bn", "en"):
        raise HTTPException(400, "lang must be bn or en")
    if body.key not in MESSAGE_KEYS:
        raise HTTPException(400, f"key must be one of {MESSAGE_KEYS}")
    await set_setting(f"msg_{body.key}_{lang}", body.value)
    return {"ok": True, "key": f"msg_{body.key}_{lang}"}


@router.get("/api/stats")
async def api_stats(_: str = Depends(require_admin)):
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
    _: str = Depends(require_admin),
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


@router.get("/api/postbacks")
async def api_postbacks(
    limit: int = Query(50, ge=1, le=200),
    _: str = Depends(require_admin),
):
    async with async_session() as session:
        result = await session.execute(
            select(PostbackLog).order_by(desc(PostbackLog.id)).limit(limit)
        )
        rows = result.scalars().all()
    return {
        "postbacks": [
            {
                "id": r.id,
                "click_id": r.click_id,
                "trader_id": r.trader_id,
                "status": r.status,
                "event_id": r.event_id,
                "sumdep": r.sumdep,
                "sumwithdraw": r.sumwithdraw,
                "country": r.country,
                "raw_data": r.raw_data,
                "created_at": r.created_at.isoformat() if r.created_at else None,
            }
            for r in rows
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
async def api_ai_caption(body: CaptionRequest, _: str = Depends(require_admin)):
    topic = (body.topic or "VIP").strip()
    lang = body.lang if body.lang in ("bn", "en") else "bn"
    prem = body.include_tg_emoji
    err = None
    openai_key = os.getenv("OPENAI_API_KEY", "")
    if openai_key:
        try:
            import httpx

            async with httpx.AsyncClient(timeout=30) as client:
                r = await client.post(
                    "https://api.openai.com/v1/chat/completions",
                    headers={"Authorization": f"Bearer {openai_key}"},
                    json={
                        "model": os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
                        "messages": [
                            {
                                "role": "system",
                                "content": "Telegram HTML captions only. Under 800 chars.",
                            },
                            {
                                "role": "user",
                                "content": f"lang={lang} tone={body.tone} topic={topic} premium={prem}",
                            },
                        ],
                    },
                )
                r.raise_for_status()
                return {
                    "ok": True,
                    "source": "openai",
                    "html": r.json()["choices"][0]["message"]["content"].strip(),
                }
        except Exception as e:
            err = str(e)

    if lang == "bn":
        html = (
            f'{_e("wave", prem)} <b>{topic}</b> {_e("spark", prem)}\n\n'
            f'{_e("megaphone", prem)} VIP চ্যানেলে যোগ দিতে ধাপগুলো ফলো করুন। {_e("down", prem)}'
        )
    else:
        html = (
            f'{_e("wave", prem)} Welcome to <b>{topic}</b>! {_e("spark", prem)}\n\n'
            f'{_e("megaphone", prem)} Follow the steps to join VIP. {_e("down", prem)}'
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
