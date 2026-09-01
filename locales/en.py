TEXTS = {
    "choose_language": "Please choose your language / অনুগ্রহ করে আপনার ভাষা নির্বাচন করুন:",
    "language_set": "Language set to English ✅",

    "welcome": (
        '<tg-emoji emoji-id="6131722652978517042">✨</tg-emoji> '
        "Welcome to <b>{botName}</b>! "
        '<tg-emoji emoji-id="6131732243640489932">👑</tg-emoji>\n\n'

        '<tg-emoji emoji-id="6131935223794897558">👑</tg-emoji> '
        "<b>To join the VIP group:</b>\n"
        "Create a Quotex account from the link below and send your "
        "<b>8-digit Trader ID</b>. "
        '<tg-emoji emoji-id="6131950423684157862">⬇️</tg-emoji>\n\n'

        '<tg-emoji emoji-id="6131865357561893257">📌</tg-emoji> '
        "<b>Minimum deposit required for VIP:</b> "
        '<tg-emoji emoji-id="6131899841854313732">💰</tg-emoji> '
        "<b>${min_deposit}</b>\n\n"

        '<tg-emoji emoji-id="6131940386345588326">📢</tg-emoji> '
        "Want <b>Basic / Course group only</b>? Use the <b>Basic / Course Group</b> button in the menu.\n\n"

        '<tg-emoji emoji-id="6132056066994737954">⚠️</tg-emoji> '
        "Send only an English <b>8-digit</b> Quotex Trader ID.\n"
        "Example: <code>12345678</code>\n\n"

        "━━━━━━━━━━━━━━━━\n"
        '<tg-emoji emoji-id="6132162165571851142">🔗</tg-emoji> '
        "<b>Quotex account create link:</b>\n"
        "{register_url}\n"
        "━━━━━━━━━━━━━━━━"
    ),

    "main_menu": "Main Menu",

    "btn_premium": "VIP Join",
    "btn_basic": "Basic / Course Group",
    "btn_create_account": "New Quotex Account",
    "btn_delete_account": "Delete Account",
    "btn_public": "All Social Media",
    "btn_support": "Support",
    "btn_status": "Status",
    "btn_back": "Back",
    "btn_tutorial": "Watch Tutorial",
    "btn_open_account": "Open Quotex Account",
    "btn_register": "Register & Deposit",
    "btn_settings": "Settings",
    "btn_change_language": "Change Language",
    "btn_exness": "Exness Account",
    "btn_exness_open": "Open Exness Account",

    "settings_title": (
        "<b>Settings</b>\n\n"
        "You can change language here.\n"
        "More options are below."
    ),

    "invalid_trader_id": (
        '<tg-emoji emoji-id="6132121822944040490">❌</tg-emoji> '
        "Invalid format.\n"
        "Send only an English <b>8-digit</b> Quotex Trader ID.\n"
        "Example: <code>12345678</code>"
    ),
    "trader_id_saved": (
        "Trader ID saved: <code>{trader_id}</code>"
    ),
    "account_created_success": (
        '<tg-emoji emoji-id="6132160039563040830">✅</tg-emoji> '
        "Your account has been created successfully\n\n"
        "Trader ID: <code>{trader_id}</code>"
    ),
    "account_ok_need_deposit": (
        '<tg-emoji emoji-id="6132160039563040830">✅</tg-emoji> '
        "Your account has been created successfully\n\n"
        '<tg-emoji emoji-id="6132121822944040490">❌</tg-emoji> '
        "No deposit has been made on your account yet\n\n"
        '<tg-emoji emoji-id="6131729658070177295">🟢</tg-emoji> '
        "Please deposit <b>${min_deposit}</b> to your account, then send your Trader ID again — you will receive the VIP group link "
        '<tg-emoji emoji-id="6131865357561893257">📌</tg-emoji>'
    ),
    "deposit_received_need_more": (
        "Deposit received: <b>${amount:.2f}</b>\n"
        "Total: <b>${total:.2f}</b> / Required: <b>${min_deposit}</b>\n\n"
        "Please deposit more, then send Trader ID or wait."
    ),
    "not_from_our_link": (
        '<tg-emoji emoji-id="6131671482738152492">👎</tg-emoji> '
        "<b>Trader ID not found</b>\n\n"
        "Your Trader ID was not found in our system.\n"
        "Please create an account from the designated link and send the Trader ID to us again.\n\n"
        '<tg-emoji emoji-id="6131867157153191252">✔️</tg-emoji> '
        "After creating an account and sending the Trader ID, you will be added to the "
        "<b>Basic Group / Basic Class Group</b>.\n\n"
        '<tg-emoji emoji-id="6132168784116454807">🔥</tg-emoji> '
        "Once the Trader ID is sent correctly, our team will verify your details and share the next instructions.\n\n"
        '<tg-emoji emoji-id="6132162165571851142">🔗</tg-emoji> '
        "<b>Account Create Link:</b>\n"
        "{register_url}"
    ),
    "need_deposit_hint": (
        '<tg-emoji emoji-id="6132121822944040490">❌</tg-emoji> '
        "No deposit has been made on your account yet\n\n"
        "Please deposit <b>${min_deposit}</b> then send Trader ID again."
    ),

    "premium_info": (
        '<tg-emoji emoji-id="6131732243640489932">👑</tg-emoji> '
        "<b>Premium / VIP Join Process</b> "
        '<tg-emoji emoji-id="6131722652978517042">✨</tg-emoji>\n\n'

        '<tg-emoji emoji-id="6131968569920984974">➡️</tg-emoji> '
        "1. Click Register below\n\n"

        '<tg-emoji emoji-id="6131968569920984974">➡️</tg-emoji> '
        "2. Create a <b>new</b> Quotex account\n\n"

        '<tg-emoji emoji-id="6131968569920984974">➡️</tg-emoji> '
        "3. Make the minimum deposit: <b>${min_deposit}</b>\n\n"

        '<tg-emoji emoji-id="6131968569920984974">➡️</tg-emoji> '
        "4. Send your <b>8-digit</b> Trader ID to the bot\n\n"

        '<tg-emoji emoji-id="6131968569920984974">➡️</tg-emoji> '
        "5. Get VIP group link after verification\n\n"

        '<tg-emoji emoji-id="6131867157153191252">✔️</tg-emoji> '
        "Use only our Affiliate Link.\n\n"

        "━━━━━━━━━━━━━━━━\n"
        '<tg-emoji emoji-id="6132162165571851142">🔗</tg-emoji> '
        "<b>Account Create Link:</b>\n"
        "{register_url}\n"
        "━━━━━━━━━━━━━━━━"
    ),

    "basic_info": (
        '<tg-emoji emoji-id="6131940386345588326">📢</tg-emoji> '
        "<b>Basic Group / Course Group Join</b> "
        '<tg-emoji emoji-id="6131722652978517042">✨</tg-emoji>\n\n'

        '<tg-emoji emoji-id="6131865357561893257">📌</tg-emoji> '
        "<b>Simple rules:</b>\n\n"

        '<tg-emoji emoji-id="6131968569920984974">➡️</tg-emoji> '
        "1. Create a Quotex account with the <b>Affiliate Link</b> below\n\n"

        '<tg-emoji emoji-id="6131968569920984974">➡️</tg-emoji> '
        "2. Verify your account\n\n"

        '<tg-emoji emoji-id="6131968569920984974">➡️</tg-emoji> '
        "3. Send your <b>8-digit Trader ID</b> to the bot\n\n"

        '<tg-emoji emoji-id="6131867157153191252">✔️</tg-emoji> '
        "<b>Just create an account and send the Trader ID</b> — "
        "you will be added to the <b>Basic Group / Basic Course Group</b>.\n\n"

        '<tg-emoji emoji-id="6132056066994737954">⚠️</tg-emoji> '
        "VIP has separate rules and may require a deposit — "
        "use the <b>VIP Join</b> button for VIP.\n\n"

        "━━━━━━━━━━━━━━━━\n"
        '<tg-emoji emoji-id="6132162165571851142">🔗</tg-emoji> '
        "<b>Account Create Link:</b>\n"
        "{register_url}\n"
        "━━━━━━━━━━━━━━━━"
    ),

    "waiting_deposit": "Waiting for your deposit...",
    "already_verified": "You are already verified!",

    "trader_id_already_used": (
        '<tg-emoji emoji-id="6132121822944040490">❌</tg-emoji> '
        "<b>This Trader ID is already in use</b>\n\n"
        "Trader ID: <code>{trader_id}</code>\n\n"
        "One Trader ID can only be used on <b>one Telegram account</b>.\n"
        "This ID is already verified on another account.\n\n"
        "Questions? Contact: @SK_SupportOfficial"
    ),

    "invite_ready": (
        '<tg-emoji emoji-id="6132160039563040830">✅</tg-emoji> '
        "<b>Verification successful!</b>\n\n"
        "Your Trader ID:\n"
        "<code>{trader_id}</code>\n\n"
        "━━━━━━━━━━━━━━━━\n"
        '<tg-emoji emoji-id="6131732243640489932">👑</tg-emoji> '
        "<b>VIP Group</b>\n"
        '<a href="{link}">Click here to join the VIP group</a>\n\n'
        '<tg-emoji emoji-id="6132168784116454807">🔥</tg-emoji> '
        "<b>ADVANCE Course Group</b>\n"
        '<a href="https://t.me/+bHS9UDzwZM4wMjRl">Click here to join the ADVANCE group</a>\n'
        "https://t.me/+bHS9UDzwZM4wMjRl\n\n"
        '<tg-emoji emoji-id="6131865357561893257">📌</tg-emoji> '
        "<b>Rules & Regulations</b> (must follow)\n"
        '<a href="https://t.me/+QENouQFoo-E4NGE1">Click here to view Rules</a>\n'
        "https://t.me/+QENouQFoo-E4NGE1\n"
        "━━━━━━━━━━━━━━━━\n\n"
        "Enjoy VIP & ADVANCE benefits!\n"
        "Questions? Contact: @SK_SupportOfficial"
    ),

    "already_joined": "You have already joined the VIP group.",

    "status_title": (
        "<b>Your Account Status</b>\n\n"
    ),
    "status_not_verified": "Not verified yet. Register with our link and deposit first.",
    "status_verified": (
        "Trader ID: <code>{trader_id}</code>\n"
        "Country: {country}\n"
        "Verified: Yes\n"
        "Verified at: {verified_at}\n"
        "Joined VIP: {joined}\n"
        "Total Deposit: ${total_deposit:.2f}\n"
        "Last Deposit: ${last_deposit:.2f}\n"
        "Total Withdraw: ${total_withdraw:.2f}"
    ),
    "status_full": (
        "Trader ID: <code>{trader_id}</code>\n"
        "Country: {country}\n"
        "Verified: {verified}\n"
        "Verified at: {verified_at}\n"
        "Joined VIP: {joined}\n"
        "Total Deposit: ${total_deposit:.2f}\n"
        "Last Deposit: ${last_deposit:.2f}\n"
        "Total Withdraw: ${total_withdraw:.2f}"
    ),
    "history_title": "History (Postback)",
    "history_empty": "History: no postback yet.",

    "public_channel": (
        "<b>TELEGRAM CHANNEL LINK</b>\n"
        "https://t.me/+qUD0MGB5Px1kOTRl\n\n"
        "<b>TikTok</b>\n"
        "https://www.tiktok.com/@sktraderasif.official\n\n"
        "https://www.tiktok.com/@sktraderasifofficial\n\n"
        "https://www.tiktok.com/@trader.asif.official\n\n"
        "<b>Fb Page:</b>\n"
        "https://www.facebook.com/share/1BUTtViLNy/\n\n"
        "https://www.facebook.com/share/17N4AAUddg/\n\n"
        "<b>Youtube:</b>\n"
        "https://youtube.com/@sktraderasifofficial\n\n"
        "Support & Discussion: https://t.me/SKofficialdiscussionsupport\n\n"
        "<b>Contact Me:</b> @Sk_TraderAsif_Official"
    ),

    "support": (
        "@SK_SupportOfficial "
        '<tg-emoji emoji-id="6132160039563040830">✅</tg-emoji>'
    ),

    "exness_info": (
        '<tg-emoji emoji-id="6131732243640489932">👑</tg-emoji> '
        "If you trade Forex with me, please open an <b>EXNESS</b> account using the link below "
        '<tg-emoji emoji-id="6131950423684157862">⬇️</tg-emoji>\n\n'
        "https://one.exnessonelink.com/a/a16d50an4d\n\n"
        "Partner Code: <code>a16d50an4d</code>\n\n"
        "@SK_SupportOfficial"
    ),

    "create_account_guide": (
        '<tg-emoji emoji-id="6131722652978517042">✨</tg-emoji> '
        "<b>How to create a new Quotex account</b>\n\n"
        '<tg-emoji emoji-id="6131968569920984974">➡️</tg-emoji> '
        "Click the Register button below\n"
        "Fill the form with a new email/phone\n"
        "Complete registration\n"
        "Make minimum deposit <b>${min_deposit}</b>\n"
        "Send Trader ID to the bot\n\n"
        '<tg-emoji emoji-id="6132162165571851142">🔗</tg-emoji> '
        "Only our Affiliate Link = {register_url}"
    ),

    "delete_account_guide": (
        '<tg-emoji emoji-id="6132121822944040490">❌</tg-emoji> '
        "<b>How to delete old Quotex account</b>\n\n"
        "1. Login to old account\n"
        "2. Profile / Settings\n"
        "3. Request account deletion\n"
        "4. Create a new account with our link"
    ),
}
