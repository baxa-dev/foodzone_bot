# start third party packages
from django.core.management.base import BaseCommand
from django.conf import settings
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, InputMediaPhoto, KeyboardButton, Update, Bot, \
    ReplyKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackContext, ConversationHandler, MessageHandler, Filters, \
    CallbackQueryHandler
from telegram.utils.request import Request
from bot.management.commands.func import about, amount, baskets, ha, home, location, menu, orders, sendLocation, yoq
# end third party packages

# start my packages
from bot.management.commands.utils import get_BotUser, Message, ButtonText, get_meal, ContextData, get_keyboard

# end my packages
from bot.models import BotUser

LANG: int = 1
FIRST_NAME = 2
PHONE = 3
ALL = 4


def start(update: Update, context: CallbackContext):
    user_id = update.message.from_user.id
    user = get_BotUser(user_id)

    if user.is_active:
        update.message.reply_html(Message(user.lang).HOME_MSG, reply_markup=get_keyboard(user.lang))
        return ALL
    keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton(text="🇺🇿 O'zbek tili", callback_data='uz'),
            InlineKeyboardButton(text="🇷🇺 русский язык", callback_data="ru")
        ]
    ])
    update.message.reply_html("Tilni tanlang👇\n-----------\nВыберите язык👇", reply_markup=keyboard)
    return LANG


def set_lang(lang, user_id):
    user = get_BotUser(tg_id=user_id)
    user.lang = lang
    user.save()


def uz(update: Update, context: CallbackContext) -> int:
    query = update.callback_query
    query.answer()
    set_lang('uz', query.from_user.id)
    query.message.reply_html("Ismingizni kiriting")
    return FIRST_NAME


def ru(update: Update, context: CallbackContext) -> int:
    query = update.callback_query
    query.answer()
    set_lang('ru', query.from_user.id)
    query.message.reply_html("Введите ваше имя")
    return FIRST_NAME


def first_name(update: Update, context: CallbackContext) -> int:
    user_id = update.message.from_user.id
    user = get_BotUser(user_id)
    user.first_name = update.message.text
    user.save()
    if user.lang == 'uz':
        btn_text = '📲 Kontaktni jo\'natish'
        text = "📲 Telefon nomeringizni yuboring"
    else:
        btn_text = '📲 Отправить контакт'
        text = "📲 Отправьте свой номер телефона"

    reply_markup = ReplyKeyboardMarkup([[KeyboardButton(btn_text, request_contact=True)]],
                                       resize_keyboard=True)
    update.message.reply_html(text, reply_markup=reply_markup)
    return PHONE


def uz_set(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()
    set_lang(lang='uz', user_id=query.from_user.id)
    user = get_BotUser(query.from_user.id)
    query.message.delete()
    query.message.reply_html(Message(user.lang).HOME_MSG, reply_markup=get_keyboard(user.lang))


def ru_set(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()
    set_lang(lang='ru', user_id=query.from_user.id)
    user = get_BotUser(query.from_user.id)
    query.message.delete()
    query.message.reply_html(Message(user.lang).HOME_MSG, reply_markup=get_keyboard(user.lang))


def set_language(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()
    user = get_BotUser(query.from_user.id)
    keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton(text="🇺🇿 O'zbek tili", callback_data='uz-set'),
            InlineKeyboardButton(text="🇷🇺 русский язык", callback_data="ru-set")
        ]
    ])
    query.message.delete()
    query.message.reply_html('Tilni tanlang👇' if user.lang == 'uz' else 'Выберите язык👇', reply_markup=keyboard)


def phonenumber(update: Update, context: CallbackContext) -> int:
    user_id = update.message.from_user.id
    user = get_BotUser(user_id)
    user.phone = update.message.contact.phone_number
    user.is_active = True
    user.save()
    update.message.reply_html(Message(user.lang).HOME_MSG, reply_markup=get_keyboard(user.lang))
    return ALL


class Command(BaseCommand):
    help = "Telegram bot"

    def handle(self, *args, **options):
        request = Request(
            connect_timeout=0.5,
            read_timeout=1.0,
        )
        bot = Bot(
            request=request,
            token=settings.TOKEN,
            base_url=settings.PROXY_URL,
        )
        updater = Updater(
            bot=bot,
            use_context=True,

        )

        def entryPoints() -> list:
            return [
                CommandHandler('start', start),
                CallbackQueryHandler(about, pattern=f"^({ContextData.ABOUT})$"),
                CallbackQueryHandler(home, pattern=f"^({ContextData.HOME})$"),
                CallbackQueryHandler(amount, pattern="^(amount)$"),
                CallbackQueryHandler(baskets, pattern="^(basket)$"),
                CallbackQueryHandler(sendLocation, pattern="^(order)$"),
                CallbackQueryHandler(ha, pattern="^(ha)$"),
                CallbackQueryHandler(yoq, pattern="^(yoq)$"),
                CallbackQueryHandler(orders, pattern="^(orders)$"),
                CallbackQueryHandler(set_language, pattern='^(setLang)$'),
                CallbackQueryHandler(uz_set, pattern='^(uz-set)$'),
                CallbackQueryHandler(ru_set, pattern='^(ru-set)$'),
                # CallbackQueryHandler(self.menu, pattern=f"^({ContextData.MENU})$"),
                CallbackQueryHandler(menu),
            ]

        all_handler = ConversationHandler(
            entry_points=entryPoints(),
            states={
                1: [
                    CallbackQueryHandler(start, pattern='start'),
                    CallbackQueryHandler(uz, pattern='^(uz)$'),
                    CallbackQueryHandler(ru, pattern='^(ru)$')
                ],
                2: [
                    CommandHandler('start', start),
                    MessageHandler(Filters.text, first_name),
                ],
                3: [
                    CommandHandler('start', start),
                    MessageHandler(Filters.contact, phonenumber)
                ],
                4: entryPoints() + [
                    MessageHandler(Filters.location, location),
                ],

            },
            fallbacks=[]
        )

        updater.dispatcher.add_handler(all_handler)
        updater.start_polling()
        updater.idle()
