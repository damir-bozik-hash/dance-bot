import logging
import json
import os
from telegram import Update, ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import (
    Application, CommandHandler, MessageHandler, filters,
    ContextTypes, ConversationHandler, CallbackQueryHandler
)

# ========== НАСТРОЙКИ ==========
TOKEN = "8827798820:AAFP2GsKSPSXBGeGtP3sn3gu6Av5kDKTgBA"
ADMIN_USERNAME = "Alisha_Fire_Tribal"
ADMIN_LINK = "https://t.me/Alisha_Fire_Tribal"
FREE_LESSON_LINK = "https://t.me/+l890f77SujQ4Mjcy"
DATA_FILE = "bot_data.json"

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ========== СОСТОЯНИЯ ==========
(MAIN_MENU, COURSE_DANCED, COURSE_FITNESS, COURSE_GOAL,
 ARCHETYPE_MENU, TEST_Q1, TEST_Q2, TEST_Q3, TEST_Q4,
 TEST_Q5, TEST_Q6, TEST_Q7) = range(12)

# ========== АРХЕТИПЫ ==========
ARCHETYPES = {
    "🌙 Жрица": {
        "cultures": "Греция: Гестия/Персефона • Египет: Исида • Индия: Сарасвати • Шумер: Инанна • Славяне: Мокошь",
        "description": "Жрица — женщина-загадка, целительница, хранительница сакрального знания. Живёт интуицией и внутренним миром, чувствует тонкие вибрации.\n\nПо Юнгу — архетип духовной связи и глубины. Не боится тени и тёмных сторон жизни — интегрирует их в мудрость.\n\nВ танце: медитативные волны, закрытые глаза, движение изнутри. Танец становится ритуалом.",
        "how_to_reveal": "• Начни с тишины — закрой глаза, почувствуй тело\n• Двигайся от дыхания, не от музыки\n• Представь что каждое движение — молитва\n• Практикуй медленные волны позвоночником\n• Работай с руками как с потоками энергии"
    },
    "🌹 Любовница": {
        "cultures": "Греция: Афродита • Рим: Венера • Египет: Хатхор • Индия: Лакшми • Шумер: Иштар • Славяне: Лада",
        "description": "Любовница — архетип чувственности, красоты и творческой силы. Это способность наслаждаться жизнью всеми чувствами и притягивать людей своей живостью.\n\nПо Юнгу — Анима в полном расцвете. Психологически умеет быть в настоящем моменте.\n\nВ танце: медленные бёдра, магнетический взгляд. Тело говорит: «я здесь, я живая».",
        "how_to_reveal": "• Танцуй для себя, не для зрителя\n• Работай с бёдрами — медленные восьмёрки, круги\n• Позволь взгляду быть мягким и притягивающим\n• Добавь паузы — остановка это самый сильный момент\n• Tribal Fusion раскрывает чувственность через восточную технику"
    },
    "⚔️ Воительница": {
        "cultures": "Греция: Артемида/Афина • Рим: Диана • Индия: Дурга/Кали • Скандинавия: Валькирии • Славяне: Морена",
        "description": "Воительница — архетип независимости, силы духа и бесстрашия. Знает свою цель и идёт к ней не оглядываясь.\n\nПо Юнгу — активная направленная энергия. Умеет устанавливать границы и действовать решительно.\n\nВ танце: чёткие акценты, мощные удары, уверенная осанка. Тело говорит: «я знаю свою силу».",
        "how_to_reveal": "• Работай с акцентами — резкие удары бёдрами и плечами\n• Держи осанку — грудь вперёд, взгляд прямо\n• Используй пространство — большие шаги, захват территории\n• Танец с огнём идеально раскрывает Воительницу"
    },
    "🌿 Мать": {
        "cultures": "Греция: Деметра • Рим: Церера • Египет: Исида • Китай: Нюй Ва • Славяне: Мать-Сыра-Земля • Христианство: Богородица",
        "description": "Мать — архетип безусловной любви, принятия и созидания. Питает, поддерживает, создаёт пространство для роста.\n\nПо Юнгу — один из древнейших архетипов коллективного бессознательного.\n\nВ танце: округлые движения, объятия пространства, плавность. Тело говорит: «здесь безопасно».",
        "how_to_reveal": "• Начни с ощущения земли под ногами\n• Работай с округлыми движениями — круги руками и торсом\n• Представь что обнимаешь пространство вокруг\n• Дыши глубоко — живот участвует в движении"
    },
    "🎨 Муза": {
        "cultures": "Греция: девять Муз/Эрато • Рим: Камены • Индия: Сарасвати • Кельты: Бригид",
        "description": "Муза — архетип вдохновения и творческого огня. Пробуждает лучшее в других, зажигает идеи.\n\nПо Юнгу — творческая Анима. Видит потенциал там где другие видят пустоту.\n\nВ танце: импровизация, лёгкость, неожиданные переходы. Тело говорит: «смотри — всё возможно».",
        "how_to_reveal": "• Практикуй импровизацию — без заранее выученных движений\n• Реагируй на каждый инструмент в музыке отдельно\n• Позволь рукам рисовать в воздухе\n• Экспериментируй с уровнями — пол, середина, высота"
    },
    "🔥 Трансформирующая": {
        "cultures": "Греция: Геката • Индия: Кали • Скандинавия: Хель • Египет: Нефтида • Славяне: Баба-Яга",
        "description": "Трансформирующая — архетип смерти старого и рождения нового. Не боится разрушить то что уже не служит.\n\nПо Юнгу — Тень, интегрированная в силу. Самый мощный архетип для личностного роста.\n\nВ танце: дикость, хаотичная энергия, огонь. Тело говорит: «я не боюсь темноты — я сама огонь».",
        "how_to_reveal": "• Позволь телу двигаться некрасиво — освободи контроль\n• Работай с резкими сменами динамики — тишина и взрыв\n• Танец с огнём — прямой путь к этому архетипу\n• Исследуй тёмные эмоции через тело — злость, страх, страсть"
    },
    "👑 Королева": {
        "cultures": "Греция: Гера • Рим: Юнона • Египет: Маат/Нефертити • Скандинавия: Фригг • Шумер: Нинхурсаг",
        "description": "Королева — архетип власти, достоинства и харизмы. Управляет пространством не силой, а присутствием.\n\nПо Юнгу — зрелое Эго в гармонии с Самостью. Умеет нести ответственность и вдохновлять одним своим видом.\n\nВ танце: медленная поступь, контроль пространства, взгляд который держит зал.",
        "how_to_reveal": "• Замедлись — Королева никуда не торопится\n• Работай с осанкой — корона невидима но ощутима\n• Практикуй медленные повороты с фиксацией взгляда\n• Используй паузы как инструмент власти"
    },
    "🌊 Мудрая": {
        "cultures": "Греция: Афина • Рим: Минерва • Египет: Маат/Нейт • Индия: Парвати • Китай: Гуань Инь • Христианство: София",
        "description": "Мудрая — архетип глубины, стратегии и принятия цикличности жизни. Видит картину целиком и умеет ждать нужного момента.\n\nПо Юнгу — интегрированная Тень и развитая Самость.\n\nВ танце: осознанность каждого движения, дыхание как основа. Тело говорит: «я принимаю всё что есть».",
        "how_to_reveal": "• Начни с дыхания — каждое движение рождается из выдоха\n• Двигайся медленно, осознавая каждый миллиметр\n• Практикуй баланс — устойчивость это мудрость тела\n• Позволь танцу быть несовершенным — мудрость принимает всё"
    }
}

TEST_QUESTIONS = [
    {
        "q": "1/7 🌸 Когда входишь в незнакомую комнату — что делаешь первым?",
        "options": [
            ("А) Останавливаюсь, чувствую атмосферу", "🌙 Жрица"),
            ("Б) Ищу красивые детали и интересных людей", "🌹 Любовница"),
            ("В) Занимаю центральное место", "👑 Королева"),
            ("Г) Ищу того, кому нужна помощь", "🌿 Мать"),
        ]
    },
    {
        "q": "2/7 🔥 Что сейчас самое важное для тебя?",
        "options": [
            ("А) Найти своё предназначение", "🌙 Жрица"),
            ("Б) Любить и быть любимой", "🌹 Любовница"),
            ("В) Достигать целей и побеждать", "⚔️ Воительница"),
            ("Г) Вдохновлять и творить", "🎨 Муза"),
        ]
    },
    {
        "q": "3/7 💫 Как справляешься с трудностями?",
        "options": [
            ("А) Ухожу внутрь себя, жду знака", "🌙 Жрица"),
            ("Б) Действую решительно", "⚔️ Воительница"),
            ("В) Позволяю себе переродиться заново", "🔥 Трансформирующая"),
            ("Г) Анализирую и нахожу мудрое решение", "🌊 Мудрая"),
        ]
    },
    {
        "q": "4/7 🎵 Какая музыка резонирует с тобой?",
        "options": [
            ("А) Этническая, медитативная, с барабанами", "🌙 Жрица"),
            ("Б) Чувственная, медленная, с глубоким басом", "🌹 Любовница"),
            ("В) Мощная, ритмичная, драйвовая", "⚔️ Воительница"),
            ("Г) Классика или джаз — что-то с глубиной", "🌊 Мудрая"),
        ]
    },
    {
        "q": "5/7 🌺 Как тебя описывают близкие?",
        "options": [
            ("А) Загадочная, глубокая, необычная", "🌙 Жрица"),
            ("Б) Тёплая, заботливая, надёжная", "🌿 Мать"),
            ("В) Яркая, вдохновляющая, творческая", "🎨 Муза"),
            ("Г) Сильная, уверенная, харизматичная", "👑 Королева"),
        ]
    },
    {
        "q": "6/7 ✨ Что чувствуешь когда танцуешь?",
        "options": [
            ("А) Транс, единение с чем-то большим", "🌙 Жрица"),
            ("Б) Свободу и желание разрушить все рамки", "🔥 Трансформирующая"),
            ("В) Силу и власть над пространством", "👑 Королева"),
            ("Г) Радость и желание поделиться с миром", "🎨 Муза"),
        ]
    },
    {
        "q": "7/7 🔮 Какой образ тебе ближе?",
        "options": [
            ("А) Жрица у алтаря в ночном лесу", "🌙 Жрица"),
            ("Б) Воительница верхом на коне", "⚔️ Воительница"),
            ("В) Мать, обнимающая всю землю", "🌿 Мать"),
            ("Г) Женщина с огнём под звёздным небом", "🔥 Трансформирующая"),
        ]
    }
]

# ========== ХРАНИЛИЩЕ ==========
def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    return {}

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def get_admin_chat_id():
    return load_data().get("admin_chat_id")

def set_admin_chat_id(chat_id):
    data = load_data()
    data["admin_chat_id"] = chat_id
    save_data(data)

def save_archetype_stat(archetype):
    data = load_data()
    stats = data.get("archetype_stats", {})
    stats[archetype] = stats.get(archetype, 0) + 1
    data["archetype_stats"] = stats
    save_data(data)

# ========== КЛАВИАТУРЫ ==========
def main_menu_keyboard():
    return ReplyKeyboardMarkup([
        ["💃 Подобрать курс", "🎁 Получить бесплатный урок"],
        ["💰 Стоимость занятий", "❓ Частые вопросы"],
        ["🌙 Архетипы в танце", "🔥 Танец с Огнём"],
        ["🌀 Что такое Tribal Fusion"]
    ], resize_keyboard=True)

def archetype_menu_keyboard():
    keys = [[name] for name in ARCHETYPES.keys()]
    keys.append(["🧪 Узнать свой архетип (тест)"])
    keys.append(["🏠 Главное меню"])
    return ReplyKeyboardMarkup(keys, resize_keyboard=True)

def yes_no_keyboard():
    return ReplyKeyboardMarkup([["✅ Да", "❌ Нет"]], resize_keyboard=True)

def fitness_keyboard():
    return ReplyKeyboardMarkup([["🐢 Низкий", "🚶 Средний", "🏃 Высокий"]], resize_keyboard=True)

def goal_keyboard():
    return ReplyKeyboardMarkup([["🌸 Для себя", "🌟 Выступать", "😊 Удовольствие"]], resize_keyboard=True)

def back_keyboard():
    return ReplyKeyboardMarkup([["🏠 Главное меню"]], resize_keyboard=True)

def contact_inline_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📩 Написать Алише", url=ADMIN_LINK)],
        [InlineKeyboardButton("⏳ Она свяжется со мной", callback_data="wait_contact")]
    ])

def online_course_keyboard():
    """Кнопки для онлайн курса новичок/средний"""
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🎓 Записаться на онлайн курс", url=ADMIN_LINK)],
        [InlineKeyboardButton("📩 Записаться вживую", url=ADMIN_LINK)],
        [InlineKeyboardButton("⏳ Она свяжется со мной", callback_data="wait_contact")]
    ])

def test_keyboard(q_index):
    options = TEST_QUESTIONS[q_index]["options"]
    return ReplyKeyboardMarkup([[opt[0]] for opt in options], resize_keyboard=True)

# ========== УВЕДОМЛЕНИЕ АДМИНУ ==========
async def notify_admin(context, user, message: str):
    admin_id = get_admin_chat_id()
    if admin_id:
        name = user.full_name or user.first_name or "Неизвестно"
        username = f"@{user.username}" if user.username else "нет username"
        text = f"🔔 *Новое уведомление!*\n\n👤 Имя: {name}\n🔗 Username: {username}\n\n{message}"
        await context.bot.send_message(chat_id=admin_id, text=text, parse_mode="Markdown")

# ========== CALLBACKS ==========
async def wait_contact_callback(update, context):
    query = update.callback_query
    await query.answer()
    await query.edit_message_text("✅ Отлично! Алиша свяжется с вами в ближайшее время 😊")

async def reveal_archetype_callback(update, context):
    query = update.callback_query
    await query.answer()
    arch_name = query.data.replace("reveal_", "")
    if arch_name in ARCHETYPES:
        arch = ARCHETYPES[arch_name]
        await query.message.reply_text(
            f"💃 *{arch_name} — как раскрыть в танце:*\n\n{arch['how_to_reveal']}\n\n"
            "Хочешь начать раскрывать этот архетип? Запишись на занятие 👇",
            parse_mode="Markdown",
            reply_markup=contact_inline_keyboard()
        )

# ========== СТАРТ (работает и через /start и через кнопку) ==========
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if user.username == ADMIN_USERNAME:
        set_admin_chat_id(update.effective_chat.id)
        await update.message.reply_text(
            "👑 Добро пожаловать, Алиша!\n\n"
            "Ваш chat_id сохранён — будете получать уведомления о клиентах.\n\n"
            "📊 Статистика архетипов: /stats",
            reply_markup=main_menu_keyboard()
        )
    else:
        await update.message.reply_text(
            f"✨ Привет, {user.first_name}!\n\n"
            "Я помогу тебе выбрать курс танца, узнать свой женский архетип "
            "и узнать всё об огненном танце.\n\n"
            "Выбери что тебя интересует 👇",
            reply_markup=main_menu_keyboard()
        )
    return MAIN_MENU

# ========== СТАТИСТИКА ==========
async def stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if user.username != ADMIN_USERNAME:
        await update.message.reply_text("❌ Эта команда только для администратора.")
        return MAIN_MENU
    data = load_data()
    stats = data.get("archetype_stats", {})
    if not stats:
        await update.message.reply_text("📊 Статистика пока пуста.")
        return MAIN_MENU
    total = sum(stats.values())
    text = "📊 *Статистика архетипов:*\n\n"
    for arch, count in sorted(stats.items(), key=lambda x: -x[1]):
        percent = round(count / total * 100)
        bar = "▓" * (percent // 10) + "░" * (10 - percent // 10)
        text += f"{arch}\n{bar} {count} чел. ({percent}%)\n\n"
    text += f"👥 Всего прошли тест: {total} человек"
    await update.message.reply_text(text, parse_mode="Markdown")
    return MAIN_MENU

# ========== ГЛАВНОЕ МЕНЮ ==========
async def main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text

    # Кнопка Старт без слеша
    if text.lower() in ["старт", "start", "начать", "привет", "🏠 главное меню"]:
        return await start(update, context)

    if "Подобрать курс" in text:
        await update.message.reply_text(
            "💃 *Отлично!* Давай подберём идеальный курс.\n\nТы танцевала раньше?",
            parse_mode="Markdown", reply_markup=yes_no_keyboard()
        )
        return COURSE_DANCED

    elif "Бесплатный урок" in text:
        user = update.effective_user
        await notify_admin(context, user, "🎁 Хочет получить *бесплатный урок*.")
        await update.message.reply_text(
            "🎁 Вот твой бесплатный урок! Переходи по ссылке и смотри 👇",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("▶️ Смотреть бесплатный урок", url=FREE_LESSON_LINK)],
                [InlineKeyboardButton("📩 Написать Алише", url=ADMIN_LINK)]
            ])
        )
        await update.message.reply_text("Вернуться в главное меню:", reply_markup=back_keyboard())
        return MAIN_MENU

    elif "Стоимость" in text:
        await update.message.reply_text(
            "💰 *Стоимость занятий:*\n\n"
            "🔸 Пробное занятие (60 мин) — 1 500₽ / ~20$\n"
            "🔸 Разовое занятие — 3 000₽ / ~35-40$\n"
            "🔸 Пакет 5 занятий — 12 000₽\n\n"
            "Для записи и оплаты свяжитесь с руководителем 👇",
            parse_mode="Markdown", reply_markup=contact_inline_keyboard()
        )
        await update.message.reply_text("Вернуться в главное меню:", reply_markup=back_keyboard())
        await notify_admin(context, update.effective_user, "💰 Смотрел(а) *стоимость занятий*.")
        return MAIN_MENU

    elif "Частые вопросы" in text:
        await update.message.reply_text(
            "❓ *Частые вопросы:*\n\n"
            "📌 *Нужен ли опыт?*\nНет! Берём всех — от новичков до опытных.\n\n"
            "📌 *Что такое Tribal Fusion?*\nНажми кнопку 🌀 Что такое Tribal Fusion в главном меню!\n\n"
            "📌 *Что такое Танец с Огнём?*\nРабота с огненными реквизитами. Обучаем с нуля, безопасно!\n\n"
            "📌 *Как проходят занятия?*\nОнлайн и офлайн, индивидуально и в группах.\n\n"
            "💬 Остались вопросы? 👇",
            parse_mode="Markdown", reply_markup=contact_inline_keyboard()
        )
        await update.message.reply_text("Вернуться в главное меню:", reply_markup=back_keyboard())
        return MAIN_MENU

    elif "Tribal Fusion" in text:
        await update.message.reply_text(
            "🌀 *Что такое Tribal Fusion?*\n\n"
            "Tribal Fusion — это современный танцевальный стиль, рождённый в США в 1970-х годах. "
            "Дословно: *tribal* — «племенной», *fusion* — «слияние».\n\n"
            "💫 *Из чего состоит:*\n"
            "Это сплав танца живота, фламенко, индийских стилей (одисси, катхак), "
            "африканских и ближневосточных народных танцев — всё соединено в один живой современный стиль.\n\n"
            "🌍 *История:*\n"
            "Основательница трайбла — Джамила Салимпур. Она объединила танцы Северной Африки, "
            "Ближнего Востока, Индии и фламенко в единый стиль. "
            "В 90-х трайбл стремительно завоевал Европу.\n\n"
            "✨ *Чем отличается от обычного танца живота:*\n"
            "• Больше свободы и самовыражения\n"
            "• Нет жёстких правил — есть твой язык тела\n"
            "• Подходит любому уровню физподготовки\n"
            "• Развивает женственность, пластику и уверенность\n"
            "• Каждый танец — это история, рассказанная твоим телом\n\n"
            "🔥 В сочетании с Танцем с Огнём Tribal Fusion становится настоящим ритуалом силы!\n\n"
            "Хочешь попробовать? 👇",
            parse_mode="Markdown", reply_markup=contact_inline_keyboard()
        )
        await update.message.reply_text("Вернуться в главное меню:", reply_markup=back_keyboard())
        return MAIN_MENU

    elif "Архетипы" in text:
        await update.message.reply_text(
            "🌙 *Архетипы в танце*\n\n"
            "Архетипы — универсальные женские образы, которые живут в каждой из нас. "
            "Они присутствуют во всех культурах мира под разными именами.\n\n"
            "Выбери архетип чтобы узнать о нём — или пройди тест 👇",
            parse_mode="Markdown", reply_markup=archetype_menu_keyboard()
        )
        return ARCHETYPE_MENU

    elif "Танец с Огнём" in text:
        await update.message.reply_text(
            "🔥 *Танец с Огнём*\n\n"
            "Танец с огнём — древнейшая практика, которая существует в культурах всего мира: "
            "от ритуалов полинезийских племён до персидских храмовых танцев.\n\n"
            "🎪 *Реквизит:*\n"
            "Пои (шары на цепях), веера с огнём, огненный стафф, дракон-стафф, огненные кольца. "
            "Каждый реквизит требует отдельной техники.\n\n"
            "💫 *Зачем танцевать с огнём:*\n"
            "• Страх уходит — ты учишься доверять себе\n"
            "• Появляется уверенность в движениях и решениях\n"
            "• Огонь требует полного присутствия — мысли замолкают\n"
            "• Раскрывает архетип Трансформирующей и Воительницы\n"
            "• Выступление с огнём навсегда меняет отношение к себе\n\n"
            "🛡 *Безопасно ли это?*\n"
            "Да — при правильном обучении. Начинаем с безопасных реквизитов, "
            "огонь добавляем только когда ты готова технически и внутренне.\n\n"
            "Хочешь попробовать? 👇",
            parse_mode="Markdown", reply_markup=contact_inline_keyboard()
        )
        await update.message.reply_text("Вернуться в главное меню:", reply_markup=back_keyboard())
        await notify_admin(context, update.effective_user, "🔥 Интересуется *Танцем с Огнём*.")
        return MAIN_MENU

    else:
        await update.message.reply_text("Выбери один из вариантов 👇", reply_markup=main_menu_keyboard())
        return MAIN_MENU

# ========== МЕНЮ АРХЕТИПОВ ==========
async def archetype_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text

    if "Главное меню" in text:
        await update.message.reply_text("Главное меню 👇", reply_markup=main_menu_keyboard())
        return MAIN_MENU

    elif "тест" in text.lower() or "Узнать свой" in text:
        context.user_data["test_scores"] = {}
        await update.message.reply_text(
            "🧪 *Тест на определение архетипа*\n\n"
            "7 вопросов — отвечай честно, первое что приходит в голову.\n"
            "Нет правильных или неправильных ответов 💫\n\n" +
            TEST_QUESTIONS[0]["q"],
            parse_mode="Markdown",
            reply_markup=test_keyboard(0)
        )
        return TEST_Q1

    elif text in ARCHETYPES:
        arch = ARCHETYPES[text]
        await update.message.reply_text(
            f"{text}\n\n"
            f"🌍 *В разных культурах:*\n{arch['cultures']}\n\n"
            f"📖 *Описание:*\n{arch['description']}",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("💃 Как раскрыть в танце?", callback_data=f"reveal_{text}")]
            ])
        )
        return ARCHETYPE_MENU

    else:
        await update.message.reply_text("Выбери архетип или пройди тест 👇", reply_markup=archetype_menu_keyboard())
        return ARCHETYPE_MENU

# ========== ПОДБОР КУРСА ==========
async def course_danced(update, context):
    context.user_data["danced"] = "Да" in update.message.text
    if "Нет" in update.message.text:
        await update.message.reply_text(
            "🌟 *Tribal Fusion* — слияние восточных и современных стилей. Развивает пластику и уверенность.\n\n"
            "🔥 *Танец с Огнём* — обучаем с нуля, безопасно и красиво!\n\n"
            "Каков твой уровень физической подготовки? 👇",
            parse_mode="Markdown", reply_markup=fitness_keyboard()
        )
    else:
        await update.message.reply_text("Каков твой уровень физической подготовки? 👇", reply_markup=fitness_keyboard())
    return COURSE_FITNESS

async def course_fitness(update, context):
    t = update.message.text
    context.user_data["fitness"] = "low" if "Низкий" in t else "medium" if "Средний" in t else "high"
    await update.message.reply_text("🎯 Какова твоя главная цель?", reply_markup=goal_keyboard())
    return COURSE_GOAL

async def course_goal(update, context):
    t = update.message.text
    context.user_data["goal"] = "self" if "себя" in t else "perform" if "Выступать" in t else "fun"
    danced = context.user_data.get("danced", False)
    fitness = context.user_data.get("fitness", "low")
    goal = context.user_data.get("goal", "fun")

    if not danced and fitness == "low":
        course = "🌸 *Tribal Fusion для начинающих*"
        level = "beginner"
        desc = "Мягкий старт — растяжка, базовые движения, никакого стресса. Идеально если никогда не танцевала."
    elif not danced and fitness in ["medium", "high"]:
        course = "🌸 *Tribal Fusion для начинающих (актив)*"
        level = "beginner"
        desc = "Базовый курс с более активной нагрузкой. Быстрый прогресс с первых занятий."
    elif danced and goal == "perform":
        course = "🌟 *Продвинутый Tribal Fusion + Танец с Огнём*"
        level = "advanced"
        desc = "Для тех кто хочет выступать и удивлять. Сценические постановки и работа с огнём."
    elif danced and goal == "self":
        course = "💃 *Tribal Fusion — Средний уровень*"
        level = "medium"
        desc = "Углубление техники и работа над пластикой. Для тех кто хочет расти в танце."
    else:
        course = "😊 *Tribal Fusion — Свободный поток*"
        level = "medium"
        desc = "Занятия в удовольствие без строгих требований."

    await update.message.reply_text(
        f"✨ *Твой идеальный курс:*\n\n{course}\n\n{desc}",
        parse_mode="Markdown"
    )

    if level in ["beginner", "medium"]:
        await update.message.reply_text(
            "🎓 *Онлайн курс для тебя:*\n\n"
            "Доступ к закрытому Telegram-каналу с уроками — занимайся в любое время из любой точки мира!\n\n"
            "Напиши Алише *«Хочу онлайн курс»* — она включит тебя в расписание и откроет доступ к каналу.\n\n"
            "Также можешь записаться на занятие *вживую* — уточни у Алиши наличие мест 👇",
            parse_mode="Markdown",
            reply_markup=online_course_keyboard()
        )
    else:
        await update.message.reply_text(
            "Для записи и оплаты свяжитесь с руководителем 👇",
            reply_markup=contact_inline_keyboard()
        )

    await update.message.reply_text("Вернуться в главное меню:", reply_markup=back_keyboard())
    await notify_admin(context, update.effective_user, f"💃 Подобрала курс: {course}")
    return MAIN_MENU

# ========== ТЕСТ ==========
def process_answer(text, q_index, context):
    scores = context.user_data.get("test_scores", {})
    for option_text, archetype in TEST_QUESTIONS[q_index]["options"]:
        if text == option_text:
            scores[archetype] = scores.get(archetype, 0) + 1
            break
    context.user_data["test_scores"] = scores

async def ask_next(update, context, next_q_index, next_state):
    process_answer(update.message.text, next_q_index - 1, context)
    await update.message.reply_text(
        TEST_QUESTIONS[next_q_index]["q"],
        reply_markup=test_keyboard(next_q_index)
    )
    return next_state

async def finish_test(update, context):
    process_answer(update.message.text, 6, context)
    scores = context.user_data.get("test_scores", {})
    if not scores:
        await update.message.reply_text("Что-то пошло не так. Попробуй снова /start", reply_markup=main_menu_keyboard())
        return MAIN_MENU
    top = max(scores, key=scores.get)
    arch = ARCHETYPES[top]
    save_archetype_stat(top)
    await update.message.reply_text(
        f"✨ *Твой архетип — {top}!*\n\n"
        f"🌍 *В разных культурах:*\n{arch['cultures']}\n\n"
        f"📖 {arch['description']}\n\n"
        f"💃 *Как раскрыть в танце:*\n{arch['how_to_reveal']}\n\n"
        "Хочешь раскрыть этот архетип? Запишись на занятие 👇",
        parse_mode="Markdown", reply_markup=contact_inline_keyboard()
    )
    await update.message.reply_text("Вернуться в главное меню:", reply_markup=back_keyboard())
    await notify_admin(context, update.effective_user, f"🧪 Прошла тест. Архетип: *{top}*")
    return MAIN_MENU

async def test_q1(u, c): return await ask_next(u, c, 1, TEST_Q2)
async def test_q2(u, c): return await ask_next(u, c, 2, TEST_Q3)
async def test_q3(u, c): return await ask_next(u, c, 3, TEST_Q4)
async def test_q4(u, c): return await ask_next(u, c, 4, TEST_Q5)
async def test_q5(u, c): return await ask_next(u, c, 5, TEST_Q6)
async def test_q6(u, c): return await ask_next(u, c, 6, TEST_Q7)
async def test_q7(u, c): return await finish_test(u, c)

# ========== ЗАПУСК ==========
def main():
    app = Application.builder().token(TOKEN).build()

    conv = ConversationHandler(
        entry_points=[
            CommandHandler("start", start),
            MessageHandler(filters.Regex("^(старт|start|начать|привет)$"), start)
        ],
        states={
            MAIN_MENU: [MessageHandler(filters.TEXT & ~filters.COMMAND, main_menu)],
            COURSE_DANCED: [MessageHandler(filters.TEXT & ~filters.COMMAND, course_danced)],
            COURSE_FITNESS: [MessageHandler(filters.TEXT & ~filters.COMMAND, course_fitness)],
            COURSE_GOAL: [MessageHandler(filters.TEXT & ~filters.COMMAND, course_goal)],
            ARCHETYPE_MENU: [MessageHandler(filters.TEXT & ~filters.COMMAND, archetype_menu)],
            TEST_Q1: [MessageHandler(filters.TEXT & ~filters.COMMAND, test_q1)],
            TEST_Q2: [MessageHandler(filters.TEXT & ~filters.COMMAND, test_q2)],
            TEST_Q3: [MessageHandler(filters.TEXT & ~filters.COMMAND, test_q3)],
            TEST_Q4: [MessageHandler(filters.TEXT & ~filters.COMMAND, test_q4)],
            TEST_Q5: [MessageHandler(filters.TEXT & ~filters.COMMAND, test_q5)],
            TEST_Q6: [MessageHandler(filters.TEXT & ~filters.COMMAND, test_q6)],
            TEST_Q7: [MessageHandler(filters.TEXT & ~filters.COMMAND, test_q7)],
        },
        fallbacks=[
            CommandHandler("start", start),
            CommandHandler("stats", stats_command)
        ],
    )

    app.add_handler(conv)
    app.add_handler(CommandHandler("stats", stats_command))
    app.add_handler(CallbackQueryHandler(wait_contact_callback, pattern="^wait_contact$"))
    app.add_handler(CallbackQueryHandler(reveal_archetype_callback, pattern="^reveal_"))

    logger.info("Бот запущен!")
    app.run_polling()

if __name__ == "__main__":
    main()
