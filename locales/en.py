TEXTS = {
    "choose_language": "Please choose your language / অনুগ্রহ করে আপনার ভাষা নির্বাচন করুন:",
    "language_set": "Language set to English ✅",

    "welcome": (
        '<tg-emoji emoji-id="5188481279963715781">👋</tg-emoji> '
        "Welcome to <b>{botName}</b>! "
        '<tg-emoji emoji-id="5879757713658875847">✨</tg-emoji>\n\n'
        '<tg-emoji emoji-id="5215174853895660531">📢</tg-emoji> '
        "To join the VIP Channel, send your Quotex <b>Trader ID</b>. "
        '<tg-emoji emoji-id="6300954126901577963">👇</tg-emoji>\n\n'
        '<tg-emoji emoji-id="5397782960512444700">📌</tg-emoji> '
        "If you have not opened an account with our Affiliate Link:\n\n"
        "• Create a new Account using our Link\n"
        "• Verify your Account\n"
        "• Make the minimum deposit (if required)\n\n"
        '<tg-emoji emoji-id="5420323339723881652">⚠️</tg-emoji> '
        "Send only an English 6–12 digit Trader ID.\n\n"
        "━━━━━━━━━━━━━━━━\n"
        "🔗 <b>Quotex account create link:</b>\n"
        "{register_url}\n"
        "━━━━━━━━━━━━━━━━"
    ),

    "main_menu": "Main Menu",
    "btn_premium": "🎁 VIP Join",
    "btn_create_account": "⭐ New Account",
    "btn_delete_account": "❌ Delete Account",
    "btn_public": "🔗 Public Channel",
    "btn_support": "📢 Support",
    "btn_status": "📊 Status",
    "btn_back": "⬅️ Back",
    "btn_tutorial": "📘 Tutorial",
    "btn_register": "📝 Register & Deposit",
    "btn_settings": "⚙️ Settings",
    "btn_change_language": "🌐 Change Language",
    "settings_title": (
        "⚙️ <b>Settings</b>\n\n"
        "You can change language here.\n"
        "More options are below."
    ),

    "invalid_trader_id": (
        "❌ Invalid format.\n"
        "Send only an English <b>6–12 digit</b> Trader ID.\n"
        "Example: <code>12345678</code>"
    ),
    "trader_id_saved": (
        "✅ Trader ID saved: <code>{trader_id}</code>"
    ),
    "account_created_success": (
        "✅ <b>Success!</b> Account found via our Affiliate Link.\n\n"
        "🆔 Trader ID: <code>{trader_id}</code>\n\n"
        "Now deposit at least <b>${min_deposit}</b> (if required).\n"
        "After registration/deposit match you will get the VIP group link."
    ),
    "deposit_received_need_more": (
        "💰 Deposit received: <b>${amount:.2f}</b>\n"
        "Total: <b>${total:.2f}</b> / Required: <b>${min_deposit}</b>\n\n"
        "Please deposit more, then send Trader ID or wait."
    ),
    "not_from_our_link": (
        "❌ <b>Account was not created with our Affiliate Link</b>\n\n"
        "Trader ID: <code>{trader_id}</code>\n\n"
        "You did not open the account via our link, or it is not in our system yet.\n\n"
        "✅ What to do:\n"
        "1️⃣ Click the button and create a <b>new</b> account\n"
        "2️⃣ Verify your account\n"
        "3️⃣ Make the minimum deposit (if required)\n"
        "4️⃣ Send your Trader ID again\n\n"
        "⚠️ Old accounts or other partners' links are not accepted."
    ),
    "need_deposit_hint": (
        "⏳ Not verified yet.\n\n"
        "Deposit at least <b>${min_deposit}</b>.\n"
        "When deposit + Trader ID match, you will get the VIP link."
    ),

    "premium_info": (
        "🎁 <b>Premium / VIP Join Process</b>\n\n"
        "1️⃣ Click Register below\n"
        "2️⃣ Create a <b>new</b> Quotex account\n"
        "3️⃣ Make the minimum deposit (if required)\n"
        "4️⃣ Send Trader ID to the bot\n"
        "5️⃣ Get VIP group link after verification\n\n"
        "⚠️ Use only our Affiliate Link.\n"
        "Partner ID (lid): <code>1480996</code>"
    ),
    "waiting_deposit": "⏳ Waiting for your deposit...",
    "already_verified": "✅ You are already verified!",
    "invite_ready": (
        "🎉 <b>Congratulations!</b>\n\n"
        "Your account has been verified.\n"
        "Join the VIP group:\n\n"
        "{link}\n\n"
        "✅ Click the link to join."
    ),
    "already_joined": "✅ You have already joined the VIP group.",
    "status_title": "📊 <b>Your Account Status</b>\n\n",
    "status_not_verified": "❌ Not verified yet. Register with our link and deposit first.",
    "status_verified": (
        "✅ Status: <b>Verified</b>\n"
        "🆔 Trader ID: <code>{trader_id}</code>\n"
        "🌍 Country: {country}\n"
        "💰 Total Deposit: ${total_deposit:.2f}\n"
        "💸 Total Withdraw: ${total_withdraw:.2f}\n"
        "📥 Last Deposit: ${last_deposit:.2f}\n"
        "📅 Verified at: {verified_at}\n"
        "👥 Joined VIP: {joined}"
    ),
    "status_full": (
        "🆔 Trader ID: <code>{trader_id}</code>\n"
        "🌍 Country: {country}\n"
        "✅ Verified: {verified}\n"
        "📅 Verified at: {verified_at}\n"
        "👥 Joined VIP: {joined}\n"
        "💰 Total Deposit: ${total_deposit:.2f}\n"
        "📥 Last Deposit: ${last_deposit:.2f}\n"
        "💸 Total Withdraw: ${total_withdraw:.2f}\n"
        "🎯 Minimum required: ${min_deposit}"
    ),
    "history_title": "📜 <b>History (Postback)</b>",
    "history_empty": "📜 History: no postback yet.",
    "public_channel": "🔗 Free Signal Public Channel:\nhttps://t.me/+gLV8BLij6PAxYjE1",
    "support": "Any problem? Contact admin: @TEADMIN9",
    "create_account_guide": (
        "⭐ <b>How to create new Quotex account</b>\n\n"
        "1. Click <b>Register</b> below\n"
        "2. Fill form with new email/phone\n"
        "3. Complete registration\n"
        "4. Make minimum deposit (if required)\n"
        "5. Send Trader ID to the bot\n\n"
        "Only our Affiliate Link (lid=<code>1480996</code>) is accepted."
    ),
    "delete_account_guide": (
        "❌ <b>How to delete old Quotex account</b>\n\n"
        "1. Login to old account\n"
        "2. Profile / Settings\n"
        "3. Request deletion\n"
        "4. Create new account with our link"
    ),
}
