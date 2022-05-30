from telegram import InlineKeyboardMarkup, InlineKeyboardButton

from bot.models import BotUser, Meal


class Message:
    def __init__(self, lang):
        if lang == "uz":
            self.HOME_MSG = "Yetkazib berish Toshkent shahrida soat 09:00 dan 23:00 gacha ishlaydi"
            self.ABOUT_MSG = "🛡 <b>Mazalli hotdoglar , sevimli burgerlar 🍔\nKafolatlanngan ta'm va tez yetkazib berish 🚚\n☎️ 95 476 14 97\n☎️71 276 14 97</b>"
            self.KORZINKA_MSG = "📥 <b>Savat:</b>\n\n"
            self.MENU_MSG = "📋 <b>FastFood buyurtma berish</b>"
            self.MEAL_MSG = "FastFood"
        else:
            self.HOME_MSG = "Доставка будет по Ташкенту с 09:00 до 23:00"
            self.ABOUT_MSG = "🛡 <b>Вкуснейшие хот-доги, любимые бургеры 🍔 Гарантия вкуса и быстрая доставка 🚚\n☎️ 95 476 14 97\n☎️71 276 14 97</b>"
            self.KORZINKA_MSG = "📥 <b>Корзина:</b>\n\n"
            self.MENU_MSG = "📋 <b>Заказать Фаст Фоод</b>"
            self.MEAL_MSG = "Фаст Фоод"


class ButtonText:
    def __init__(self, lang):
        if lang == "uz":
            self.HOME_BUTTON_TEXT = "Bosh sahifa"
            self.ABOUT_BUTTON_TEXT = "🛡 Biz haqimizda"
            self.KORZINKA_BUTTON_TEXT = "📥 Savat"
            self.MENU_BUTTON_TEXT = "📋 Menyu"
            self.MEAL_BUTTON_TEXT = "FastFood🍔"
        else:
            self.HOME_BUTTON_TEXT = "главный меню"
            self.ABOUT_BUTTON_TEXT = "🛡 О нас"
            self.KORZINKA_BUTTON_TEXT = "📥 Корзина"
            self.MENU_BUTTON_TEXT = "📋 Меню"
            self.MEAL_BUTTON_TEXT = "Фастфуд🍔"


class ContextData:
    ABOUT = "about"
    HOME = "home"
    KORZINKA = "basket"
    MENU = "menu"
    MEAL = "meal"


ContextData = ContextData()

def get_keyboard(lang):
    if lang == "uz":
        return InlineKeyboardMarkup([
            [
                InlineKeyboardButton(ButtonText("uz").MENU_BUTTON_TEXT, callback_data=ContextData.MENU)
            ],
            [
                InlineKeyboardButton(ButtonText("uz").ABOUT_BUTTON_TEXT, callback_data=ContextData.ABOUT),
                InlineKeyboardButton(ButtonText("uz").KORZINKA_BUTTON_TEXT, callback_data=ContextData.KORZINKA)
            ],
            [
                InlineKeyboardButton("✏️ Tilni o'zgartirish", callback_data="setLang")
            ],
            [
                InlineKeyboardButton("📜 Buyurtmalar tarixi", callback_data="orders")
            ]
        ])
    else:
        return InlineKeyboardMarkup([
            [
                InlineKeyboardButton(ButtonText("ru").MENU_BUTTON_TEXT, callback_data=ContextData.MENU)
            ],
            [
                InlineKeyboardButton(ButtonText("ru").ABOUT_BUTTON_TEXT, callback_data=ContextData.ABOUT),
                InlineKeyboardButton(ButtonText("ru").KORZINKA_BUTTON_TEXT, callback_data=ContextData.KORZINKA)
            ],
            [
                InlineKeyboardButton("✏️ Изменить язык", callback_data="setLang")
            ],
            [
                InlineKeyboardButton("📜История заказов", callback_data="orders")
            ]
        ])


def get_BotUser(tg_id) -> BotUser:
    return BotUser.objects.get_or_create(tg_id=tg_id)[0]


def get_meal(id):
    try:
        return Meal.objects.get(id=id)
    except Meal.DoesNotExist:
        return None
