TEXTS = {
    "choose_language": "Please choose your language / অনুগ্রহ করে আপনার ভাষা নির্বাচন করুন:",
    "language_set": "Language set to English ✅",

    "welcome": (
        '<tg-emoji emoji-id="5188481279963715781">👋</tg-emoji> '
        "Welcome to <b>{botName}</b>! "
        '<tg-emoji emoji-id="5879757713658875847">✨</tg-emoji>\n\n'

        '<tg-emoji emoji-id="5217822164362739968">👑</tg-emoji> '
        "<b>To join the VIP group:</b>\n"
        "Create a Quotex account from the link below and send your "
        "<b>8-digit Trader ID</b>. "
        '<tg-emoji emoji-id="6300954126901577963">👇</tg-emoji>\n\n'

        '<tg-emoji emoji-id="5397782960512444700">📌</tg-emoji> '
        "A <b>deposit is required</b> to be added to VIP (if a minimum amount is set).\n\n"

        '<tg-emoji emoji-id="5215174853895660531">📢</tg-emoji> '
        "Want <b>Basic group only</b> (without VIP)? Use <b>All Social Media</b> or <b>Support</b> from the menu to join the basic groups.\n\n"

        '<tg-emoji emoji-id="5420323339723881652">⚠️</tg-emoji> '
        "Send only an English <b>8-digit</b> Quotex Trader ID.\n"
        "Example: <code>12345678</code>\n\n"

        "━━━━━━━━━━━━━━━━\n"
        '<tg-emoji emoji-id="5042101437237036298">🔗</tg-emoji> '
        "<b>Quotex account create link:</b>\n"
        "{register_url}\n"
        "━━━━━━━━━━━━━━━━"
    ),

    "main_menu": "Main Menu",

    # Button labels — NO normal emoji (add custom via Admin)
    "btn_premium": "VIP Join",
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
        "Invalid format.\n"
        "Send only an English <b>8-digit</b> Quotex Trader ID.\n"
        "Example: <code>12345678</code>"
    ),
    "trader_id_saved": (
        "Trader ID saved: <code>{trader_id}</code>"
    ),
    "account_created_success": (
        '<tg-emoji emoji-id="5206607081334906820">✅</tg-emoji> '
        "Your account has been created successfully "
        '<tg-emoji emoji-id="5206607081334906820">✅</tg-emoji>\n\n'
        "Trader ID: <code>{trader_id}</code>"
    ),
    "account_ok_need_deposit": (
        '<tg-emoji emoji-id="5206607081334906820">✅</tg-emoji> '
        "Your account has been created successfully "
        '<tg-emoji emoji-id="5206607081334906820">✅</tg-emoji>\n\n'
        '<tg-emoji emoji-id="5230979538975996530">❌</tg-emoji> '
        "No deposit has been made on your account yet\n\n"
        '<tg-emoji emoji-id="6217296801154731905">🟢</tg-emoji> '
        "Please deposit <b>${min_deposit}</b> to your account, then send your Trader ID to the bot again — you will receive the VIP group link "
        '<tg-emoji emoji-id="5397782960512444700">📌</tg-emoji>'
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
        '<tg-emoji emoji-id="5230979538975996530">❌</tg-emoji> '
        "No deposit has been made on your account yet\n\n"
        '<tg-emoji emoji-id="6217296801154731905">🟢</tg-emoji> '
        "Please deposit <b>${min_deposit}</b> to your account, then send your Trader ID to the bot again — you will receive the VIP group link "
        '<tg-emoji emoji-id="5397782960512444700">📌</tg-emoji>'
    ),

    "premium_info": (
        "<b>Premium / VIP Join Process</b>\n\n"
        "1. Click Register below\n"
        "2. Create a <b>new</b> Quotex account\n"
        "3. Make the minimum deposit (if required)\n"
        "4. Send your <b>8-digit</b> Trader ID to the bot\n"
        "5. Get VIP group link after verification\n\n"
        "Use only our Affiliate Link.\n"
        "Partner ID (lid): <code>1480996</code>"
    ),
    "waiting_deposit": "Waiting for your deposit...",
    "already_verified": "You are already verified!",

    "invite_ready": (
        '<tg-emoji emoji-id="5206607081334906820">✅</tg-emoji> '
        "<b>Verification successful!</b> "
        '<tg-emoji emoji-id="5206607081334906820">✅</tg-emoji>\n\n'
        "Your Trader ID:\n"
        "<code>{trader_id}</code>\n\n"
        '<tg-emoji emoji-id="5397782960512444700">📌</tg-emoji> '
        "Join the VIP group: "
        '<tg-emoji emoji-id="5397782960512444700">📌</tg-emoji>\n'
        '<tg-emoji emoji-id="5215174853895660531">📢</tg-emoji> '
        '<a href="{link}">Click here to join the VIP group</a>\n\n'
        '<tg-emoji emoji-id="5879757713658875847">✨</tg-emoji> '
        "Enjoy VIP benefits!\n"
        '<tg-emoji emoji-id="6300954126901577963">👇</tg-emoji> '
        "Questions? Contact: @SK_SupportOfficial"
    ),

    "already_joined": "You have already joined the VIP group.",

    "status_title": (
        '<tg-emoji emoji-id="6131664675214987967">📊</tg-emoji> '
        "<b>Your Account Status</b>\n\n"
    ),
    "status_not_verified": "Not verified yet. Register with our link and deposit first.",
    "status_verified": (
        '<tg-emoji emoji-id="5310024172926161438">🆔</tg-emoji> '
        "Trader ID: <code>{trader_id}</code>\n"
        '<tg-emoji emoji-id="6084845507304229827">🌍</tg-emoji> '
        "Country: {country}\n"
        '<tg-emoji emoji-id="6217732620076191135">✅</tg-emoji> '
        "Verified: Yes\n"
        '<tg-emoji emoji-id="5472279086657199080">📅</tg-emoji> '
        "Verified at: {verified_at}\n"
        '<tg-emoji emoji-id="5309844291105869907">👥</tg-emoji> '
        "Joined VIP: {joined}\n"
        '<tg-emoji emoji-id="6064542166103887096">💰</tg-emoji> '
        "Total Deposit: ${total_deposit:.2f}\n"
        '<tg-emoji emoji-id="6131928704034542549">📥</tg-emoji> '
        "Last Deposit: ${last_deposit:.2f}\n"
        '<tg-emoji emoji-id="6129731974291527294">💸</tg-emoji> '
        "Total Withdraw: ${total_withdraw:.2f}"
    ),
    "status_full": (
        '<tg-emoji emoji-id="5310024172926161438">🆔</tg-emoji> '
        "Trader ID: <code>{trader_id}</code>\n"
        '<tg-emoji emoji-id="6084845507304229827">🌍</tg-emoji> '
        "Country: {country}\n"
        '<tg-emoji emoji-id="6217732620076191135">✅</tg-emoji> '
        "Verified: {verified}\n"
        '<tg-emoji emoji-id="5472279086657199080">📅</tg-emoji> '
        "Verified at: {verified_at}\n"
        '<tg-emoji emoji-id="5309844291105869907">👥</tg-emoji> '
        "Joined VIP: {joined}\n"
        '<tg-emoji emoji-id="6064542166103887096">💰</tg-emoji> '
        "Total Deposit: ${total_deposit:.2f}\n"
        '<tg-emoji emoji-id="6131928704034542549">📥</tg-emoji> '
        "Last Deposit: ${last_deposit:.2f}\n"
        '<tg-emoji emoji-id="6129731974291527294">💸</tg-emoji> '
        "Total Withdraw: ${total_withdraw:.2f}"
    ),
    "history_title": "History (Postback)",
    "history_empty": "History: no postback yet.",

    "public_channel": (
        '<tg-emoji emoji-id="5856956664292315353">📢</tg-emoji> '
        "<b>TELEGRAM CHANNEL LINK</b>\n"
        "https://t.me/+qUD0MGB5Px1kOTRl\n\n"

        '<tg-emoji emoji-id="5855155960598762938">🎵</tg-emoji> '
        "<b>TikTok</b> "
        '<tg-emoji emoji-id="5382322671679708881">👤</tg-emoji>'
        '<tg-emoji emoji-id="6105018848434456662">✨</tg-emoji>\n'
        "https://www.tiktok.com/@sktraderasif.official\n\n"

        '<tg-emoji emoji-id="5855155960598762938">🎵</tg-emoji> '
        "<b>TikTok</b> "
        '<tg-emoji emoji-id="5381990043642502553">👤</tg-emoji>'
        '<tg-emoji emoji-id="6105018848434456662">✨</tg-emoji>\n'
        "https://www.tiktok.com/@sktraderasifofficial\n\n"

        '<tg-emoji emoji-id="5855155960598762938">🎵</tg-emoji> '
        "<b>TikTok</b> "
        '<tg-emoji emoji-id="5381879959335738545">👤</tg-emoji>'
        '<tg-emoji emoji-id="6105018848434456662">✨</tg-emoji>\n'
        "https://www.tiktok.com/@trader.asif.official\n\n"

        '<tg-emoji emoji-id="5775988670972563213">📘</tg-emoji> '
        "<b>Fb Page:</b> "
        '<tg-emoji emoji-id="5843926068523703404">📄</tg-emoji>\n'
        "https://www.facebook.com/share/1BUTtViLNy/\n\n"

        '<tg-emoji emoji-id="5775988670972563213">📘</tg-emoji> '
        "<b>Fb Page:</b> "
        '<tg-emoji emoji-id="5845852820917460595">📄</tg-emoji>\n'
        "https://www.facebook.com/share/17N4AAUddg/\n\n"

        '<tg-emoji emoji-id="5814161253672687027">▶️</tg-emoji> '
        "<b>Youtube:</b>\n"
        "https://youtube.com/@sktraderasifofficial\n\n"

        '<tg-emoji emoji-id="5397782960512444700">📌</tg-emoji> '
        "Join the Support & Discussion Group "
        '<tg-emoji emoji-id="5449683594425410231">💬</tg-emoji>\n'
        "https://t.me/SKofficialdiscussionsupport\n\n"

        '<tg-emoji emoji-id="5039783602301175152">📩</tg-emoji> '
        "<b>Contact Me:</b> @Sk_TraderAsif_Official "
        '<tg-emoji emoji-id="5278488293950889949">✅</tg-emoji>'
    ),

    "support": (
        '<tg-emoji emoji-id="6274034641984820525">🔤</tg-emoji>'
        '<tg-emoji emoji-id="6275947023418003921">🔤</tg-emoji>'
        '<tg-emoji emoji-id="6276161149012546258">🔤</tg-emoji>'
        '<tg-emoji emoji-id="5303489294285941333">➡️</tg-emoji>'
        '<tg-emoji emoji-id="5303489294285941333">➡️</tg-emoji>'
        "@SK_SupportOfficial "
        '<tg-emoji emoji-id="6217685925191750376">✅</tg-emoji>'
    ),

    "exness_info": (
        '<tg-emoji emoji-id="5217822164362739968">👑</tg-emoji>'
        "If you trade Forex with me, please open an <b>EXNESS</b> account using the link below "
        '<tg-emoji emoji-id="5406745015365943482">⬇️</tg-emoji>\n\n'
        "https://one.exnessonelink.com/a/a16d50an4d\n\n"
        "If you need an EXNESS Partner Code, use this code to connect with me:\n\n"
        "<b>PARTNER CODE</b> "
        '<tg-emoji emoji-id="5416117059207572332">➡️</tg-emoji> '
        "<code>a16d50an4d</code>\n\n"
        '<tg-emoji emoji-id="6274034641984820525">🔤</tg-emoji>'
        '<tg-emoji emoji-id="6275947023418003921">🔤</tg-emoji>'
        '<tg-emoji emoji-id="6276161149012546258">🔤</tg-emoji>'
        '<tg-emoji emoji-id="6275878355480875380">🔤</tg-emoji>'
        '<tg-emoji emoji-id="5303489294285941333">➡️</tg-emoji>'
        "@SK_SupportOfficial"
        '<tg-emoji emoji-id="6217685925191750376">✅</tg-emoji>'
    ),

    "create_account_guide": (
        '<tg-emoji emoji-id="6129909635613726974">⭐</tg-emoji> '
        "<b>How to create a new Quotex account</b>\n\n"
        '<tg-emoji emoji-id="6217713374327738118">•</tg-emoji> '
        "Click the Register button below\n"
        '<tg-emoji emoji-id="6217713374327738118">•</tg-emoji> '
        "Fill the form with a new email/phone\n"
        '<tg-emoji emoji-id="6217713374327738118">•</tg-emoji> '
        "Complete registration\n"
        '<tg-emoji emoji-id="6217713374327738118">•</tg-emoji> '
        "Make minimum deposit <b>${min_deposit}</b>\n"
        '<tg-emoji emoji-id="6217713374327738118">•</tg-emoji> '
        "Send Trader ID to the bot\n\n"
        '<tg-emoji emoji-id="5938264290740933445">🔗</tg-emoji> '
        "Only our Affiliate Link = {register_url}\n"
        "is accepted. "
        '<tg-emoji emoji-id="6217732620076191135">✅</tg-emoji>'
    ),

    "delete_account_guide": (
        '<tg-emoji emoji-id="5298742255912235479">❌</tg-emoji> '
        "<b>How to delete old Quotex account</b>\n\n"
        '<tg-emoji emoji-id="5235547326889608764">1</tg-emoji> '
        "Login to old account\n"
        '<tg-emoji emoji-id="5235547326889608764">2</tg-emoji> '
        "Profile / Settings\n"
        '<tg-emoji emoji-id="5235919365546724452">3</tg-emoji> '
        "Request account deletion\n"
        '<tg-emoji emoji-id="5238105937692085546">4</tg-emoji> '
        "Create a new account with our link"
    ),
}
