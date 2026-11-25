import os
import re
import threading
import time
import requests
import telebot
from flask import Flask
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

BOT_TOKEN = os.environ.get("BOT_TOKEN", "9122374513:AAGwrkV1pQKhxbq7Br6B2fCswgTCOtQMcIU")

PREMIUM_EMOJIS = {
    "✅": "5123248930124989216", "❌": "5210952531676504517",
    "⚠️": "5420323339723881652", "💰": "5893473283696759404",
    "⛓️": "6021344879689341042", "📊": "5895444149699612825",
    "👥": "6021690418398239007", "🤖": "5258093637450866522",
    "💡": "6023897907034330805", "🎟": "6021617983774791539",
    "👨‍💻": "5444965061749644170", "🔐": "6019568309417023812",
    "🎉": "6023579259115674297", "⏱": "6034973034257848185",
    "🎁": "6023826881160157558", "🏆": "5893376775781617954",
    "📅": "6023880246128810031", "🛡": "6019328362479097179",
    "👑": "6021428854889913572", "📈": "5938539885907415367",
    "✏️": "5879841310902324730", "🏦": "5332455502917949981",
    "📍": "6023989024765516223", "🆕": "5886306834410640699",
    "👋": "5247133031235329609", "🌐": "6019205852831947754",
    "➡️": "5807462045288766810", "🇬🇧": "5395560546865013953",
    "🇷🇺": "5267224089382116952", "🇮🇳": "6129782715035163979",
    "💎": "5298988357538328017", "🏠": "5258503720928288433",
    "📢": "5938589252328624108", "🔙": "5255703720078879038",
    "💧": "5334757303667232230", "🌧": "5393512611968995988",
    "⛈": "5224257782013769471", "🌩": "5089144476023128742",
    "🌨": "5839380464116175529", "🌦": "5258362837411045098",
    "☔": "5348289410955754971", "🎮": "5258508428212445001",
    "🎲": "5960608239623082921", "👎": "5084577224980431440",
    "🤝": "5974565221182741203", "🪙": "4918300654197277832",
    "1️⃣": "5393089050884202480", "2️⃣": "5361902709232377443",
    "👤": "4913497231492908158", "🌊": "5262553290972875718",
    "💀": "5042209657527993345", "⭕️": "5435993158536143379",
    "💼": "5938492039971737551", "ℹ️": "6028435952299413210",
    "ℹ": "6028435952299413210", "⏳": "6113844439292054570",
    "💸": "5798678875823153004", "📥": "5879841310902324730",
    "📤": "5879841310902324730", "🔄": "6030657343744644592",
    "🔁": "6030657343744644592", "💬": "6034831751308644168",
    "🎰": "5258356394959957754", "💣": "5879841310902324730",
    "🔒": "5879841310902324730", "💲": "5879841310902324730",
    "⭐": "5879841310902324730", "🌀": "5879841310902324730",
    "🔴": "5879841310902324730", "⚫": "5879841310902324730",
    "🟢": "5879841310902324730", "⬆️": "5879841310902324730",
}

# ==========================================
# Fake Web Server for Render Port Binding
# ==========================================
web_app = Flask(__name__)


@web_app.route("/")
def home():
    return "Bot is alive", 200


@web_app.route("/health")
def health():
    return "OK", 200


def run_web_server():
    port = int(os.environ.get("PORT", 10000))
    web_app.run(host="0.0.0.0", port=port, debug=False, use_reloader=False)


threading.Thread(target=run_web_server, daemon=True).start()

bot = telebot.TeleBot(BOT_TOKEN)

USER_LANG = {}

TEXTS = {
    "en": {
        "welcome_title": "Live Crypto USDT Price Bot",
        "welcome_body": (
            "Send <code>ton</code> or <code>gram</code> (same coin) to get TON's live USDT rate, "
            "or send an amount like <code>1 ton</code>, <code>2 ton</code>, or <code>/ton 1</code>.\n\n"
            "• Single / Convert: <code>ton</code>, <code>gram</code>, <code>1 ton</code>, <code>/ton 2</code>, <code>btc</code>, <code>eth</code>, <code>sol</code>, <code>ltc</code>, <code>xmr</code>, <code>xrp</code>, <code>bnb</code>, <code>trx</code>\n"
            "• All rates: <code>/rates</code> or <code>rates</code>\n"
            "• Language: <code>/lang</code>"
        ),
        "all_title": "Live Crypto USDT Rates",
        "single_title": "{name} ({short}) Live Rate",
        "amount_label": "Amount",
        "unit_price_label": "1 {short} Price",
        "total_label": "Total Value",
        "price_label": "Price",
        "change_label": "24h Change",
        "updated_label": "Updated",
        "refresh": "Refresh",
        "refresh_all": "Refresh All",
        "close": "Close",
        "not_owner": "This button is only for the command sender.",
        "updated_toast": "Rates updated.",
        "already_latest": "Rates are already up to date.",
        "lang_prompt": "Choose your preferred language:",
        "lang_set_en": "Language set to English.",
        "lang_set_ru": "Язык изменён на русский.",
        "invalid_amount": "Invalid amount. Enter a positive number like <code>/ton 1</code> or <code>2 ton</code>.",
    },
    "ru": {
        "welcome_title": "Бот курсов криптовалют к USDT",
        "welcome_body": (
            "Отправьте <code>ton</code> или <code>gram</code> (одна монета) для курса TON к USDT, "
            "или укажите сумму: <code>1 ton</code>, <code>2 ton</code>, <code>/ton 1</code>.\n\n"
            "• Монета / Конвертер: <code>ton</code>, <code>gram</code>, <code>1 ton</code>, <code>/ton 2</code>, <code>btc</code>, <code>eth</code>, <code>sol</code>, <code>ltc</code>, <code>xmr</code>, <code>xrp</code>, <code>bnb</code>, <code>trx</code>\n"
            "• Все курсы: <code>/rates</code> или <code>rates</code>\n"
            "• Язык: <code>/lang</code>"
        ),
        "all_title": "Курсы криптовалют к USDT",
        "single_title": "Курс {name} ({short})",
        "amount_label": "Количество",
        "unit_price_label": "Цена 1 {short}",
        "total_label": "Итого",
        "price_label": "Цена",
        "change_label": "За 24ч",
        "updated_label": "Обновлено",
        "refresh": "Обновить",
        "refresh_all": "Обновить все",
        "close": "Закрыть",
        "not_owner": "Эта кнопка доступна только автору запроса.",
        "updated_toast": "Курсы обновлены.",
        "already_latest": "Данные уже актуальны.",
        "lang_prompt": "Выберите язык:",
        "lang_set_en": "Language set to English.",
        "lang_set_ru": "Язык изменён на русский.",
        "invalid_amount": "Некорректная сумма. Введите положительное число, например: <code>/ton 1</code> или <code>2 ton</code>.",
    },
}

# TON and GRAM share the exact same coin definition ("ton")
COINS = [
    {"key": "ton",  "short": "TON / GRAM", "unit_short": "TON",  "name": "Toncoin / Gram", "emoji": "💎", "kucoin": "TON-USDT",  "paprika": "ton-toncoin",      "cg": "the-open-network"},
    {"key": "btc",  "short": "BTC",        "unit_short": "BTC",  "name": "Bitcoin",        "emoji": "🪙", "kucoin": "BTC-USDT",  "paprika": "btc-bitcoin",      "cg": "bitcoin"},
    {"key": "eth",  "short": "ETH",        "unit_short": "ETH",  "name": "Ethereum",       "emoji": "💎", "kucoin": "ETH-USDT",  "paprika": "eth-ethereum",     "cg": "ethereum"},
    {"key": "sol",  "short": "SOL",        "unit_short": "SOL",  "name": "Solana",         "emoji": "⚡", "kucoin": "SOL-USDT",  "paprika": "sol-solana",       "cg": "solana"},
    {"key": "ltc",  "short": "LTC",        "unit_short": "LTC",  "name": "Litecoin",       "emoji": "🪙", "kucoin": "LTC-USDT",  "paprika": "ltc-litecoin",     "cg": "litecoin"},
    {"key": "xmr",  "short": "XMR",        "unit_short": "XMR",  "name": "Monero",         "emoji": "🛡", "kucoin": "XMR-USDT",  "paprika": "xmr-monero",       "cg": "monero"},
    {"key": "xrp",  "short": "XRP",        "unit_short": "XRP",  "name": "XRP",            "emoji": "✖️", "kucoin": "XRP-USDT",  "paprika": "xrp-xrp",          "cg": "ripple"},
    {"key": "bnb",  "short": "BNB",        "unit_short": "BNB",  "name": "BNB",            "emoji": "💰", "kucoin": "BNB-USDT",  "paprika": "bnb-binance-coin", "cg": "binancecoin"},
    {"key": "trx",  "short": "TRX",        "unit_short": "TRX",  "name": "Tron",           "emoji": "🔺", "kucoin": "TRX-USDT",  "paprika": "trx-tron",         "cg": "tron"},
]

COIN_BY_KEY = {c["key"]: c for c in COINS}

ALIASES = {
    "ton": "ton", "toncoin": "ton", "gram": "ton", "grams": "ton",
    "btc": "btc", "bitcoin": "btc",
    "eth": "eth", "ethereum": "eth",
    "sol": "sol", "solana": "sol",
    "ltc": "ltc", "litecoin": "ltc",
    "xmr": "xmr", "monero": "xmr",
    "xrp": "xrp", "ripple": "xrp",
    "bnb": "bnb", "binancecoin": "bnb",
    "trx": "trx", "tron": "trx",
}

ALL_TRIGGERS = {"rates", "rate", "all", "prices", "price"}


def get_lang(user_id):
    return USER_LANG.get(user_id, "en")


def t(user_id, key):
    return TEXTS[get_lang(user_id)][key]


def pe(emoji_char):
    emoji_id = str(PREMIUM_EMOJIS.get(emoji_char, "")).strip()
    if emoji_id:
        return f'<tg-emoji emoji-id="{emoji_id}">{emoji_char}</tg-emoji>'
    return emoji_char


def format_usdt(price):
    if price is None:
        return "N/A"
    if price < 0.01:
        return f"${price:.6f} USDT"
    if price < 1:
        return f"${price:.4f} USDT"
    if price < 100:
        return f"${price:.2f} USDT"
    return f"${price:,.2f} USDT"


def format_amount(amount):
    if float(amount).is_integer():
        return f"{int(amount):,}"
    return f"{amount:g}"


def fetch_kucoin_all():
    result = {}
    try:
        url = "https://api.kucoin.com/api/v1/market/allTickers"
        res = requests.get(url, timeout=7)
        res.raise_for_status()
        tickers = res.json().get("data", {}).get("ticker", [])
        wanted = {c["kucoin"]: c["key"] for c in COINS if c.get("kucoin")}

        for item in tickers:
            sym = item.get("symbol")
            if sym in wanted:
                key = wanted[sym]
                last_price = item.get("last")
                change_rate = item.get("changeRate")
                if last_price is not None:
                    chg_pct = float(change_rate) * 100 if change_rate is not None else None
                    result[key] = {
                        "price": float(last_price),
                        "change": chg_pct,
                    }
    except Exception:
        pass
    return result


def fetch_coinpaprika_single(paprika_id):
    try:
        url = f"https://api.coinpaprika.com/v1/tickers/{paprika_id}"
        res = requests.get(url, timeout=6)
        res.raise_for_status()
        usd = res.json().get("quotes", {}).get("USD", {})
        if usd.get("price") is not None:
            return {
                "price": float(usd["price"]),
                "change": float(usd["percent_change_24h"]) if usd.get("percent_change_24h") is not None else None,
            }
    except Exception:
        pass
    return None


def fetch_coingecko_batch(missing_coins):
    out = {}
    ids = ",".join(c["cg"] for c in missing_coins if c.get("cg"))
    if not ids:
        return out
    try:
        url = "https://api.coingecko.com/api/v3/simple/price"
        params = {"ids": ids, "vs_currencies": "usd", "include_24hr_change": "true"}
        res = requests.get(url, params=params, timeout=7)
        res.raise_for_status()
        payload = res.json()
        for c in missing_coins:
            cg_id = c.get("cg")
            if cg_id and cg_id in payload:
                entry = payload[cg_id]
                if entry.get("usd") is not None:
                    out[c["key"]] = {
                        "price": float(entry["usd"]),
                        "change": float(entry["usd_24h_change"]) if entry.get("usd_24h_change") is not None else None,
                    }
    except Exception:
        pass
    return out


def get_rates_for_keys(keys):
    target_coins = [COIN_BY_KEY[k] for k in keys if k in COIN_BY_KEY]
    rates = fetch_kucoin_all()

    for c in target_coins:
        k = c["key"]
        if k not in rates and c.get("paprika"):
            p_data = fetch_coinpaprika_single(c["paprika"])
            if p_data:
                rates[k] = p_data

    missing = [c for c in target_coins if c["key"] not in rates]
    if missing:
        rates.update(fetch_coingecko_batch(missing))

    return rates


def parse_coin_and_amount(raw_text):
    """
    Parses inputs like:
      'ton' -> ('ton', 1.0)
      'gram' -> ('ton', 1.0)
      '1 ton' -> ('ton', 1.0)
      '2 gram' -> ('ton', 2.0)
      'ton 2' -> ('ton', 2.0)
      '0.5 btc' -> ('btc', 0.5)
    Returns (scope, amount) where scope is coin_key, 'all', or None.
    """
    cleaned = raw_text.strip().lower()
    if not cleaned:
        return "all", 1.0

    if cleaned in ALL_TRIGGERS:
        return "all", 1.0

    if cleaned in ALIASES:
        return ALIASES[cleaned], 1.0

    # Pattern 1: <amount> <coin> (e.g., "1 ton", "2.5 gram", "100 sol")
    m1 = re.fullmatch(r"([0-9]+(?:\.[0-9]+)?)\s*([a-zA-Z]+)", cleaned)
    if m1:
        amt = float(m1.group(1))
        coin_key = ALIASES.get(m1.group(2))
        if coin_key and amt > 0:
            return coin_key, amt

    # Pattern 2: <coin> <amount> (e.g., "ton 1", "gram 2")
    m2 = re.fullmatch(r"([a-zA-Z]+)\s+([0-9]+(?:\.[0-9]+)?)", cleaned)
    if m2:
        coin_key = ALIASES.get(m2.group(1))
        amt = float(m2.group(2))
        if coin_key and amt > 0:
            return coin_key, amt

    return None, 1.0


def build_single_coin_text(coin_key, amount, user_id):
    c = COIN_BY_KEY.get(coin_key)
    if not c:
        return None
    rates = get_rates_for_keys([coin_key])
    data = rates.get(coin_key)

    title = t(user_id, "single_title").format(name=c["name"], short=c["short"])
    unit_price = data["price"] if data and data["price"] is not None else None
    chg = data["change"] if data else None

    amt_str = format_amount(amount)
    unit_price_str = format_usdt(unit_price)
    total_str = format_usdt(unit_price * amount) if unit_price is not None else "N/A"

    if chg is not None:
        trend_icon = pe("🟢") if chg >= 0 else pe("🔴")
        sign = "+" if chg >= 0 else ""
        chg_line = f"{trend_icon} <b>{t(user_id, 'change_label')}:</b> <code>{sign}{chg:.2f}%</code>\n"
    else:
        chg_line = ""

    if amount == 1.0:
        amount_block = f"{pe('💲')} <b>{t(user_id, 'price_label')}:</b> <code>{unit_price_str}</code>\n"
    else:
        amount_block = (
            f"{pe('💰')} <b>{t(user_id, 'amount_label')}:</b> <code>{amt_str} {c['unit_short']}</code>\n"
            f"{pe('💲')} <b>{t(user_id, 'unit_price_label').format(short=c['unit_short'])}:</b> <code>{unit_price_str}</code>\n"
            f"{pe('💵')} <b>{t(user_id, 'total_label')}:</b> <code>{total_str}</code>\n"
        )

    return (
        f"{pe(c['emoji'])} <b>{title}</b>\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        f"{amount_block}"
        f"{chg_line}"
        f"{pe('⏱')} <b>{t(user_id, 'updated_label')}:</b> <code>{time.strftime('%H:%M:%S')} IST</code>"
    )


def build_all_rates_text(user_id):
    all_keys = [c["key"] for c in COINS]
    rates = get_rates_for_keys(all_keys)
    lines = [
        f"{pe('📊')} <b>{t(user_id, 'all_title')}</b>",
        "━━━━━━━━━━━━━━━━━━━━",
    ]

    for c in COINS:
        k = c["key"]
        coin_icon = pe(c["emoji"])
        data = rates.get(k)

        if data and data["price"] is not None:
            p_str = format_usdt(data["price"])
            chg = data["change"]
            if chg is not None:
                trend_icon = pe("🟢") if chg >= 0 else pe("🔴")
                sign = "+" if chg >= 0 else ""
                chg_str = f"{trend_icon} <code>{sign}{chg:.2f}%</code>"
            else:
                chg_str = ""
            lines.append(
                f"{coin_icon} <b>{c['name']}</b> (<code>{c['short']}</code>): "
                f"{pe('💲')} <code>{p_str}</code> {chg_str}"
            )
        else:
            lines.append(
                f"{coin_icon} <b>{c['name']}</b> (<code>{c['short']}</code>): "
                f"<code>N/A</code>"
            )

    lines.append("━━━━━━━━━━━━━━━━━━━━")
    lines.append(f"{pe('⏱')} <b>{t(user_id, 'updated_label')}:</b> <code>{time.strftime('%H:%M:%S')} IST</code>")
    return "\n".join(lines)


def build_rate_keyboard(user_id, scope, amount):
    ref_label = t(user_id, "refresh_all") if scope == "all" else t(user_id, "refresh")
    close_label = t(user_id, "close")
    markup = InlineKeyboardMarkup()
    markup.row(
        InlineKeyboardButton(ref_label, callback_data=f"ref|{scope}|{amount:g}|{user_id}"),
        InlineKeyboardButton(close_label, callback_data=f"close|{user_id}"),
    )
    return markup


def build_lang_keyboard(user_id):
    cur = get_lang(user_id)
    en_txt = f"{'✅ ' if cur == 'en' else ''}English"
    ru_txt = f"{'✅ ' if cur == 'ru' else ''}Русский"
    markup = InlineKeyboardMarkup()
    markup.row(
        InlineKeyboardButton(en_txt, callback_data=f"setlang|en|{user_id}"),
        InlineKeyboardButton(ru_txt, callback_data=f"setlang|ru|{user_id}"),
    )
    return markup


def send_price_response(message, scope, amount=1.0):
    uid = message.from_user.id
    if scope == "all":
        text = build_all_rates_text(uid)
    else:
        text = build_single_coin_text(scope, amount, uid)
    bot.reply_to(message, text, parse_mode="HTML", reply_markup=build_rate_keyboard(uid, scope, amount))


@bot.message_handler(commands=["start", "help"])
def start_handler(message):
    uid = message.from_user.id
    text = (
        f"{pe('🤖')} <b>{t(uid, 'welcome_title')}</b>\n\n"
        f"{t(uid, 'welcome_body')}"
    )
    bot.reply_to(message, text, parse_mode="HTML")


@bot.message_handler(commands=["lang", "language"])
def lang_handler(message):
    uid = message.from_user.id
    bot.reply_to(
        message,
        f"{pe('🌐')} <b>{t(uid, 'lang_prompt')}</b>",
        parse_mode="HTML",
        reply_markup=build_lang_keyboard(uid),
    )


@bot.message_handler(commands=["rates", "all", "prices"])
def all_rates_cmd(message):
    send_price_response(message, "all", 1.0)


@bot.message_handler(commands=list(ALIASES.keys()))
def shortcut_cmd(message):
    uid = message.from_user.id
    parts = message.text.split()
    cmd_name = parts[0][1:].lower().split("@")[0]
    coin_key = ALIASES.get(cmd_name)

    amount = 1.0
    if len(parts) > 1:
        try:
            amount = float(parts[1])
            if amount <= 0:
                raise ValueError()
        except ValueError:
            bot.reply_to(message, f"{pe('❌')} {t(uid, 'invalid_amount')}", parse_mode="HTML")
            return

    if coin_key:
        send_price_response(message, coin_key, amount)


@bot.message_handler(commands=["price", "p"])
def price_cmd(message):
    uid = message.from_user.id
    parts = message.text.split(maxsplit=1)
    if len(parts) < 2:
        send_price_response(message, "all", 1.0)
        return

    scope, amount = parse_coin_and_amount(parts[1])
    if scope is None:
        bot.reply_to(message, f"{pe('❌')} {t(uid, 'invalid_amount')}", parse_mode="HTML")
        return
    send_price_response(message, scope, amount)


@bot.message_handler(func=lambda m: bool(m.text and not m.text.startswith("/")))
def text_router(message):
    scope, amount = parse_coin_and_amount(message.text)
    if scope is None:
        # Random / general rate queries show all rates
        send_price_response(message, "all", 1.0)
    else:
        send_price_response(message, scope, amount)


@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    parts = call.data.split("|")
    action = parts[0]
    uid = call.from_user.id

    if action == "close":
        owner_id = int(parts[1])
        if uid != owner_id:
            bot.answer_callback_query(call.id, t(uid, "not_owner"), show_alert=True)
            return
        bot.delete_message(call.message.chat.id, call.message.message_id)
        return

    if action == "setlang":
        chosen_lang = parts[1]
        owner_id = int(parts[2])
        if uid != owner_id:
            bot.answer_callback_query(call.id, t(uid, "not_owner"), show_alert=True)
            return
        if chosen_lang in ("en", "ru"):
            USER_LANG[uid] = chosen_lang
        msg = t(uid, "lang_set_ru") if chosen_lang == "ru" else t(uid, "lang_set_en")
        try:
            bot.edit_message_text(
                f"{pe('✅')} <b>{msg}</b>",
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                parse_mode="HTML",
                reply_markup=build_lang_keyboard(uid),
            )
        except Exception:
            pass
        bot.answer_callback_query(call.id, msg)
        return

    if action == "ref":
        scope = parts[1]
        amount = float(parts[2])
        owner_id = int(parts[3])
        if uid != owner_id:
            bot.answer_callback_query(call.id, t(uid, "not_owner"), show_alert=True)
            return

        new_text = (
            build_all_rates_text(uid)
            if scope == "all"
            else build_single_coin_text(scope, amount, uid)
        )
        if new_text:
            try:
                bot.edit_message_text(
                    new_text,
                    chat_id=call.message.chat.id,
                    message_id=call.message.message_id,
                    parse_mode="HTML",
                    reply_markup=build_rate_keyboard(uid, scope, amount),
                )
                bot.answer_callback_query(call.id, t(uid, "updated_toast"))
            except Exception:
                bot.answer_callback_query(call.id, t(uid, "already_latest"))


if __name__ == "__main__":
    print("Bot is running...")
    bot.infinity_polling(skip_pending=True)
