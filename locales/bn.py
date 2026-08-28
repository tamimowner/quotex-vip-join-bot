TEXTS = {
    "choose_language": "Please choose your language / অনুগ্রহ করে আপনার ভাষা নির্বাচন করুন:",
    "language_set": "ভাষা বাংলায় সেট করা হয়েছে ✅",

    "welcome": (
        '<tg-emoji emoji-id="5188481279963715781">👋</tg-emoji> '
        "<b>{botName}</b> -এ স্বাগতম! "
        '<tg-emoji emoji-id="5879757713658875847">✨</tg-emoji>\n\n'
        '<tg-emoji emoji-id="5215174853895660531">📢</tg-emoji> '
        "VIP Channel-এ যুক্ত হতে আপনার Quotex <b>Trader ID</b> পাঠান। "
        '<tg-emoji emoji-id="6300954126901577963">👇</tg-emoji>\n\n'
        '<tg-emoji emoji-id="5397782960512444700">📌</tg-emoji> '
        "যদি আমাদের Affiliate Link দিয়ে Account খোলা না থাকে:\n\n"
        "• আমাদের Link দিয়ে নতুন Account তৈরি করুন\n"
        "• Account Verify করুন\n"
        "• ন্যূনতম ডিপোজিট করুন (যদি লাগে)\n\n"
        '<tg-emoji emoji-id="5420323339723881652">⚠️</tg-emoji> '
        "শুধুমাত্র ইংরেজি 6–12 সংখ্যার Trader ID পাঠাবেন।\n\n"
        "━━━━━━━━━━━━━━━━\n"
        "🔗 <b>Quotex অ্যাকাউন্ট তৈরি লিংক:</b>\n"
        "{register_url}\n"
        "━━━━━━━━━━━━━━━━"
    ),

    "main_menu": "মেইন মেনু",
    "btn_premium": "🎁 VIP জয়েন",
    "btn_create_account": "⭐ নতুন অ্যাকাউন্ট",
    "btn_delete_account": "❌ অ্যাকাউন্ট ডিলিট",
    "btn_public": "🌐 সব সোশ্যাল মিডিয়া",
    "btn_support": "📢 সাপোর্ট",
    "btn_status": "📊 স্ট্যাটাস",
    "btn_back": "⬅️ ফিরে যান",
    "btn_tutorial": "Tutorial দেখুন",
    "btn_open_account": "Quotex Account খুলুন",
    "btn_register": "📝 রেজিস্টার ও ডিপোজিট",
    "btn_settings": "⚙️ সেটিংস",
    "btn_change_language": "🌐 ভাষা পরিবর্তন",
    "settings_title": (
        "⚙️ <b>সেটিংস</b>\n\n"
        "এখান থেকে ভাষা পরিবর্তন করতে পারবেন।\n"
        "আরও অপশন নিচে পাবেন।"
    ),

    "invalid_trader_id": (
        "❌ ভুল ফরম্যাট।\n"
        "শুধুমাত্র ইংরেজি <b>6–12 সংখ্যার</b> Trader ID পাঠান।\n"
        "উদাহরণ: <code>12345678</code>"
    ),
    "trader_id_saved": (
        "✅ Trader ID সেভ হয়েছে: <code>{trader_id}</code>"
    ),
    "account_created_success": (
        "✅ <b>সফল!</b> আমাদের Affiliate Link থেকে অ্যাকাউন্ট পাওয়া গেছে।\n\n"
        "🆔 Trader ID: <code>{trader_id}</code>\n\n"
        "এখন ন্যূনতম <b>${min_deposit}</b> Deposit করুন (যদি লাগে)।\n"
        "ডিপোজিট/রেজিস্ট্রেশন মিললে VIP গ্রুপের লিংক পাবেন।"
    ),
    "deposit_received_need_more": (
        "💰 ডিপোজিট পেয়েছি: <b>${amount:.2f}</b>\n"
        "মোট: <b>${total:.2f}</b> / প্রয়োজন: <b>${min_deposit}</b>\n\n"
        "আরও ডিপোজিট করুন, তারপর Trader ID পাঠান বা অপেক্ষা করুন।"
    ),
    "not_from_our_link": (
        '<tg-emoji emoji-id="5230979538975996530">❌</tg-emoji> '
        "<b>যাচাই ব্যর্থ!</b>\n\n"
        '<tg-emoji emoji-id="6217296801154731905">🟢</tg-emoji> '
        "Trader ID <code>{trader_id}</code> আমাদের Affiliate Link দিয়ে তৈরি করা হয়নি।"
        '<tg-emoji emoji-id="5397782960512444700">📌</tg-emoji>\n\n'
        '<tg-emoji emoji-id="6300891304414938793">»</tg-emoji> '
        "অনুগ্রহ করে পুরোনো Account Delete করে নিচের Affiliate Link থেকে নতুন Account তৈরি করুন।"
        '<tg-emoji emoji-id="5206607081334906820">✅</tg-emoji>\n\n'
        '<tg-emoji emoji-id="6214983170991853422">🔗</tg-emoji> '
        "Account Create URL :- {register_url}\n\n"
        '<tg-emoji emoji-id="6217732620076191135">✅</tg-emoji> Account Verify করুন\n'
        '<tg-emoji emoji-id="6217732620076191135">✅</tg-emoji> প্রথম Deposit সম্পন্ন করুন\n'
        '<tg-emoji emoji-id="6217732620076191135">✅</tg-emoji> '
        "তারপর আপনার নতুন 8 সংখ্যার Trader ID আবার পাঠান\n\n"
        "ধন্যবাদ। "
        '<tg-emoji emoji-id="6201956329024653832">💙</tg-emoji>'
    ),
    "need_deposit_hint": (
        "⏳ এখনো ভেরিফাই হয়নি।\n\n"
        "ন্যূনতম <b>${min_deposit}</b> Deposit করুন।\n"
        "ডিপোজিট + Trader ID মিললে VIP লিংক পাবেন।"
    ),

    "premium_info": (
        "🎁 <b>প্রিমিয়াম / VIP জয়েন প্রক্রিয়া</b>\n\n"
        "1️⃣ নিচের বাটনে ক্লিক করে রেজিস্ট্রেশন লিংক খুলুন\n"
        "2️⃣ সেই লিংক দিয়ে <b>নতুন</b> কোটেক্স অ্যাকাউন্ট তৈরি করুন\n"
        "3️⃣ মিনিমাম ডিপোজিট করুন (যদি লাগে)\n"
        "৪️⃣ বটে Trader ID পাঠান\n"
        "5️⃣ ভেরিফাই হলে VIP গ্রুপ লিংক পাবেন\n\n"
        "⚠️ শুধু বটের দেওয়া Affiliate Link ব্যবহার করুন।\n"
        "Partner ID (lid): <code>1480996</code>"
    ),
    "waiting_deposit": (
        "⏳ আপনার ডিপোজিটের অপেক্ষায়..."
    ),
    "already_verified": "✅ আপনি ইতিমধ্যে ভেরিফাইড!",

    "invite_ready": (
        '<tg-emoji emoji-id="5206607081334906820">✅</tg-emoji> '
        "<b>ভেরিফিকেশন সফল!</b> "
        '<tg-emoji emoji-id="5206607081334906820">✅</tg-emoji>\n\n'
        "আপনার Trader ID:\n"
        "<code>{trader_id}</code>\n\n"
        '<tg-emoji emoji-id="5397782960512444700">📌</tg-emoji> '
        "VIP গ্রুপে যোগ দিন: "
        '<tg-emoji emoji-id="5397782960512444700">📌</tg-emoji>\n'
        '<tg-emoji emoji-id="5215174853895660531">📢</tg-emoji> '
        '<a href="{link}">ক্লিক করুন VIP গ্রুপে যোগ দিতে</a>\n\n'
        '<tg-emoji emoji-id="5879757713658875847">✨</tg-emoji> '
        "VIP সুবিধা উপভোগ করুন!\n"
        '<tg-emoji emoji-id="6300954126901577963">👇</tg-emoji> '
        "প্রশ্ন থাকলে: @SK_SupportOfficial"
    ),

    "already_joined": "✅ আপনি ইতিমধ্যে VIP গ্রুপে জয়েন করেছেন।",
    "status_title": "📊 <b>আপনার অ্যাকাউন্ট স্ট্যাটাস</b>\n\n",
    "status_not_verified": "❌ এখনো ভেরিফাই হয়নি। আমাদের লিংক দিয়ে রেজিস্টার ও ডিপোজিট করুন।",
    "status_verified": (
        "✅ স্ট্যাটাস: <b>ভেরিফাইড</b>\n"
        "🆔 ট্রেডার আইডি: <code>{trader_id}</code>\n"
        "🌍 দেশ: {country}\n"
        "💰 মোট ডিপোজিট: ${total_deposit:.2f}\n"
        "💸 মোট উইথড্র: ${total_withdraw:.2f}\n"
        "📥 সর্বশেষ ডিপোজিট: ${last_deposit:.2f}\n"
        "📅 ভেরিফাইড: {verified_at}\n"
        "👥 VIP জয়েন: {joined}"
    ),
    "status_full": (
        "🆔 Trader ID: <code>{trader_id}</code>\n"
        "🌍 দেশ: {country}\n"
        "✅ ভেরিফাইড: {verified}\n"
        "📅 ভেরিফাই সময়: {verified_at}\n"
        "👥 VIP জয়েন: {joined}\n"
        "💰 মোট ডিপোজিট: ${total_deposit:.2f}\n"
        "📥 সর্বশেষ ডিপোজিট: ${last_deposit:.2f}\n"
        "💸 মোট উইথড্র: ${total_withdraw:.2f}\n"
        "🎯 মিনিমাম প্রয়োজন: ${min_deposit}"
    ),
    "history_title": "📜 <b>হিস্ট্রি (Postback)</b>",
    "history_empty": "📜 হিস্ট্রি: এখনো কোনো postback নেই।",

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
        "সাপোর্ট এন্ড ডিসকাশন গ্রুপ এখানে জয়েন থাকবেন "
        '<tg-emoji emoji-id="5449683594425410231">💬</tg-emoji>\n'
        "https://t.me/SKofficialdiscussionsupport\n\n"

        '<tg-emoji emoji-id="5039783602301175152">📩</tg-emoji> '
        "<b>Contact Me:</b> @Sk_TraderAsif_Official "
        '<tg-emoji emoji-id="5278488293950889949">✅</tg-emoji>'
    ),

    "support": "কোনো সমস্যা হলে অ্যাডমিনকে মেসেজ করুন: @TEADMIN9",
    "create_account_guide": (
        "⭐ <b>কীভাবে নতুন কোটেক্স অ্যাকাউন্ট তৈরি করবেন</b>\n\n"
        "1. নিচের <b>রেজিস্টার</b> বাটনে ক্লিক করুন\n"
        "2. নতুন ইমেইল/ফোন দিয়ে ফর্ম পূরণ করুন\n"
        "3. রেজিস্ট্রেশন শেষ করুন\n"
        "4. মিনিমাম ডিপোজিট করুন (যদি লাগে)\n"
        "5. বটে Trader ID পাঠান\n\n"
        "শুধু আমাদের Affiliate Link (lid=<code>1480996</code>) গ্রহণযোগ্য।"
    ),
    "delete_account_guide": (
        "❌ <b>কীভাবে পুরাতন কোটেক্স অ্যাকাউন্ট ডিলিট করবেন</b>\n\n"
        "1. পুরোনো অ্যাকাউন্টে লগইন\n"
        "2. প্রোফাইল / সেটিংস\n"
        "3. অ্যাকাউন্ট ডিলিট রিকোয়েস্ট\n"
        "4. আমাদের লিংক দিয়ে নতুন অ্যাকাউন্ট তৈরি"
    ),
}
