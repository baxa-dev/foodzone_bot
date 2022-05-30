import os
from datetime import datetime
from django.conf import settings
from django.db import transaction
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, InputMediaPhoto, KeyboardButton, ReplyKeyboardMarkup, \
    Update
from telegram.ext import CallbackContext
from bot.helpers import Data
from bot.models import Meal, Menu, Order, OrderItem
from bot.management.commands.utils import Message, get_BotUser, get_meal, ContextData, get_keyboard
import logging

formatter = '[%(asctime)s] %(levelname)8s --- %(message)s (%(filename)s:%(lineno)s)'
logging.basicConfig(
    filename=f'bot-from-{datetime.now().date()}.log',
    filemode='w',
    format=formatter,
    datefmt='%Y-%m-%d %H:%M:%S',
    level=logging.WARNING
)
logger = logging.getLogger(__name__)


def home(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()
    user = get_BotUser(query.from_user.id)
    query.message.delete()

    query.message.reply_text(Message(lang=user.lang).HOME_MSG, reply_markup=get_keyboard(user.lang), parse_mode="HTML")


def about(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()
    user = get_BotUser(query.from_user.id)
    if user.lang == 'uz':
        text = "<b>Biz haqimizda</b>:\n" \
               "Menyu asosan klub sendvichlari, hot-doglar, gamburgerlar, pitsa  va donorlardan iborat." \
               " Fast foodlarning  xilma-xilligi, maqbul narxlar va mehmonlarning talabiga e'tibor berish bizning ustuvor vazifalarimizdir. " \
               "\n<a href='https://www.instagram.com/foodzone_uz'>Instagram</a>\n<a href='https://www.facebook.com/foodzoneuzb'>Facebook</a>"
        btn_text = '📍 Manzil'
        back = "🔙 Orqaga"
    else:
        text = "<b>О нас</b>:\n" \
               "Меню в основном состоит из клаб сендвичов, хот-догов, гамбургеров, пиццы и доноров. " \
               "Разнообразие фастфуда, приемлемые цены и внимание к спросу гостей-наши приоритеты." \
               "\n<a href='https://www.instagram.com/foodzone_uz'>Инстаграм</a>\n<a href='https://www.facebook.com/foodzoneuzb'>Фейсбук</a>"
        btn_text = '📍 Место нахождения'
        back = "🔙 Назад"

    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton(btn_text, url="https://goo.gl/maps/MqCLdXD613zgj3cVA")],
        [InlineKeyboardButton(back, callback_data=ContextData.HOME)]
    ])
    query.edit_message_text(text, reply_markup=keyboard, parse_mode="HTML")


def meals(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()
    query.message.delete()
    user = get_BotUser(query.from_user.id)

    menu_id = int(query.data.split('menu/')[1])
    menu = Menu.objects.get(id=menu_id)
    meals = Meal.objects.filter(menu_id=menu_id)
    index = 0
    keyboard = []

    if user.lang == "uz":
        main_menu_back = "🔙 Bosh menyuga qaytish"
        back = "🔙 Orqaga"
        menu_name = menu.name_uz
    else:
        main_menu_back = "🔙 Вернуться в главное меню"
        back = "🔙 Назад"
        menu_name = menu.name_ru

    for i in range(len(meals)):
        name = meals[i].name_uz if user.lang == 'uz' else meals[i].name_ru
        data = "menu/" + str(menu_id) + "/" + str(meals[i].id)
        if i % 2 == 0 and i != 0:
            index += 1
        if i % 2 == 0:
            keyboard.append([InlineKeyboardButton(text=name, callback_data=data)])
        else:
            keyboard[index].append(InlineKeyboardButton(text=name, callback_data=data))

    keyboard.append([InlineKeyboardButton(main_menu_back, callback_data=ContextData.HOME)])
    keyboard.append([InlineKeyboardButton(back, callback_data=ContextData.MENU)])
    query.message.reply_text(f"<b>{menu_name}</b>", reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="HTML")


def amount(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()


def addBasket(update: Update, context: CallbackContext):
    query = update.callback_query
    user = get_BotUser(query.from_user.id)
    if user.lang == "uz":
        query.answer(text=f'Savatga qo\'shildi ✅', show_alert=True)
    else:
        query.answer(text=f'В корзину ✅', show_alert=True)

    user = get_BotUser(tg_id=query.from_user.id)
    if user:
        pk = int(query.data.split('/')[-1])
        orderItem = OrderItem.objects.get_or_create(user=user, meal_id=pk, is_ordered=False)[0]
        data = Data(tg_id=query.from_user.id, product_id=pk)
        orderItem.quantitation += data.getOrCreateObject().get('data').get('amount')
        orderItem.save()
    meal(update, context)


def meal(update: Update, context: CallbackContext, setOne: bool = True):
    query = update.callback_query
    query.answer()
    user = get_BotUser(query.from_user.id)
    pk = int(query.data.split('/')[-1])
    data = Data(tg_id=query.from_user.id, product_id=pk)
    if setOne:
        data.setOne()
    amount = data.getOrCreateObject().get('data').get('amount')
    meals_data = "menu/" + query.data.split('/')[1]
    meal = get_meal(id=pk)
    addbasketdata = f"addBasket/{query.data.split('/')[1]}/{pk}"
    if user.lang == "uz":
        add_basket = "Savatga qo'shish"
        back_menu = "🔙 Menyuga qaytish"
        back = "🔙 Orqaga"
        back_home_menu = "🔙 Bosh menyuga qaytish"
        meal_name = meal.name_uz
        meal_description = meal.description_uz
    else:
        add_basket = "Добавить в корзину"
        back_menu = "🔙 Вернуться в меню"
        back = "🔙 Назад"
        back_home_menu = "🔙 Вернуться в главное меню"
        meal_name = meal.name_ru
        meal_description = meal.description_ru

    keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("-", callback_data=f"decr/{query.data.split('/')[1]}/{pk}"),
            InlineKeyboardButton(f"{amount}", callback_data="amount"),
            InlineKeyboardButton("+", callback_data=f"incr/{query.data.split('/')[1]}/{pk}"),
        ],
        [
            InlineKeyboardButton(add_basket, callback_data=addbasketdata)
        ],
        [
            InlineKeyboardButton(back_menu, callback_data='menu'),
        ],
        [
            InlineKeyboardButton(back, callback_data=meals_data)
        ],
        [
            InlineKeyboardButton(back_home_menu, callback_data=ContextData.HOME),
        ]
    ])
    image = open(str(os.path.join(settings.MEDIA_ROOT, str(meal.image))), 'rb')

    if setOne:
        som = "so'm" if user.lang == "uz" else 'сум'
        query.message.delete()
        query.message.reply_photo(
            photo=image,
            caption=f"""<b>{meal_name}</b>\n\n{meal_description}\n<b>{'Narxi' if user.lang == 'uz' else 'Цена'}:</b>{meal.price * amount} {som}""",
            parse_mode="HTML",
            reply_markup=keyboard
        )
    else:
        query.edit_message_media(
            media=InputMediaPhoto(
                media=image,
                caption=f"""<b>{meal_name}</b>\n\n{meal_description}\n<b>Narxi:</b>{meal.price * amount} so'm""",
                parse_mode="HTML"
            ),
            reply_markup=keyboard
        )


def decr(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()
    pk = int(query.data.split('/')[-1])
    data = Data(tg_id=query.from_user.id, product_id=pk)
    data.decrement()
    meal(update, context, setOne=False)


def incr(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()
    pk = int(query.data.split('/')[-1])
    data = Data(tg_id=query.from_user.id, product_id=pk)
    data.increment()
    meal(update, context, setOne=False)


def menu(update: Update, context: CallbackContext):
    query = update.callback_query
    user = get_BotUser(query.from_user.id)
    if query.data == ContextData.MENU:
        query.answer()
        query.message.delete()
        menus = Menu.objects.all()
        keyboard = []
        index = 0
        for i in range(len(menus)):
            if user.lang == "uz":
                name = menus[i].name_uz
            else:
                name = menus[i].name_ru

            data = "menu/" + str(menus[i].id)
            if i % 2 == 0 and i != 0:
                index += 1
            if i % 2 == 0:
                keyboard.append([InlineKeyboardButton(text=name, callback_data=data)])
            else:
                keyboard[index].append(InlineKeyboardButton(text=name, callback_data=data))

        keyboard.append(
            [InlineKeyboardButton("🔙 Назад" if user.lang == 'ru' else "🔙 Orqaga", callback_data=ContextData.HOME)])
        query.message.reply_text(Message(user.lang).MENU_MSG, reply_markup=InlineKeyboardMarkup(keyboard),
                                 parse_mode="HTML")
    else:
        data = query.data.split('/')[0]
        if len(query.data.split('/')) == 2:
            if data == 'menu':
                meals(update, context)
            elif data == 'b-decr':
                b_decr(update, context)
            elif data == 'b-incr':
                b_incr(update, context)
            elif data == 'd-basket':
                b_delete(update, context)

        else:
            if data == 'decr':
                decr(update, context)
            elif data == 'incr':
                incr(update, context)
            elif data == 'addBasket':
                addBasket(update, context)
            else:
                meal(update, context)


def b_decr(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()
    pk = int(query.data.split('/')[-1])
    user = get_BotUser(tg_id=query.from_user.id)
    orderItem = OrderItem.objects.filter(user=user, is_ordered=False, meal_id=pk).last()
    if orderItem.quantitation > 1:
        orderItem.quantitation = orderItem.quantitation - 1
        orderItem.save()
    else:
        orderItem.delete()
    baskets(update, context)


def b_incr(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()
    pk = int(query.data.split('/')[-1])
    user = get_BotUser(tg_id=query.from_user.id)
    orderItem = OrderItem.objects.filter(user=user, is_ordered=False, meal_id=pk).last()
    orderItem.quantitation = orderItem.quantitation + 1
    orderItem.save()
    baskets(update, context)


def b_delete(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()
    pk = int(query.data.split('/')[-1])
    user = get_BotUser(tg_id=query.from_user.id)
    orderItem = OrderItem.objects.filter(user=user, is_ordered=False, meal_id=pk).last()
    orderItem.delete()
    baskets(update, context)


def baskets(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()
    user = get_BotUser(tg_id=query.from_user.id)
    orderItems = OrderItem.objects.filter(user=user, is_ordered=False)
    text = f"{Message(user.lang).KORZINKA_MSG}"
    keyboard = []
    if orderItems:
        i = 0
        totalsum = 0
        for orderItem in orderItems:
            def get_total_sum(total_sum, lang) -> str:
                if lang == "uz":
                    return f"\nUmumiy narxi: <b>{totalsum}</b> so'm"
                return f"\nИтоговая цена: <b>{totalsum}</b> сум"

            if user.lang == 'uz':
                name = orderItem.meal.name_uz
                order_text = "Buyurtma berish"
                som = "so'm"
            else:
                name = orderItem.meal.name_ru
                order_text = "Заказ"
                som = "сум"

            i += 1
            text += f"<b>{i}. {name}</b>\n  {orderItem.quantitation} x {orderItem.meal.price} = <b>{orderItem.total_price} {som}</b>\n"
            totalsum += orderItem.total_price
            keyboard.append([
                InlineKeyboardButton(f"❌ {name}", callback_data=f"d-basket/{orderItem.meal.id}")
            ])
            keyboard.append([
                InlineKeyboardButton('-', callback_data=f"b-decr/{orderItem.meal.id}"),
                InlineKeyboardButton(f'{orderItem.quantitation}', callback_data="basket"),
                InlineKeyboardButton('+', callback_data=f"b-incr/{orderItem.meal.id}"),
            ])
        keyboard.append([
            InlineKeyboardButton(order_text, callback_data="order")
        ])
        text += get_total_sum(total_sum=totalsum, lang=user.lang)
    else:
        text += "<i>Hozirda savatda hech narsa yo'q</i>" if user.lang == "uz" else "<i> Сейчас в корзине ничего нет </i>"
    keyboard.append([
        InlineKeyboardButton("Bosh menyuga qaytish" if user.lang == "uz" else "Вернуться в главное меню",
                             callback_data=ContextData.HOME)
    ])
    query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="HTML")


def sendLocation(update: Update, context: CallbackContext):
    query = update.callback_query
    user = get_BotUser(query.from_user.id)
    query.answer()
    query.message.reply_html(
        text="Manzilingizni yuboring" if user.lang == 'uz' else "Отправьте свой адрес",
        reply_markup=ReplyKeyboardMarkup(
            [[KeyboardButton('Manzilni yuborish' if user.lang == 'uz' else "Отправить адрес", request_location=True)]],
            resize_keyboard=True)
    )


def location(update: Update, context: CallbackContext):
    if update.edited_message:
        message = update.edited_message
    else:
        message = update.message
    current_pos = (message.location.latitude, message.location.longitude)
    user = get_BotUser(
        tg_id=message.from_user.id
    )
    order = Order(
        user=user,
        latitude=current_pos[0],
        longitude=current_pos[1]
    )
    with transaction.atomic():
        order.save()
        orderItems = OrderItem.objects.filter(user=user, is_ordered=False)
        for orderItem in orderItems:
            orderItem.order = order
            orderItem.is_ordered = True
            orderItem.save()
    keyboard = [
        [
            InlineKeyboardButton("Ha" if user.lang == 'uz' else 'да', callback_data=f"ha"),
            InlineKeyboardButton("Yo'q" if user.lang == 'uz' else 'Нет', callback_data=f"yoq"),
        ]
    ]
    update.message.reply_html("Buyurtmani tasdiqlaysizmi" if user.lang == 'uz' else "Вы подтверждаете заказ",
                              reply_markup=InlineKeyboardMarkup(keyboard))


def ha(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()
    user = get_BotUser(tg_id=query.from_user.id)
    order = Order.objects.filter(user=user, is_active=False).order_by('-pk').first()
    order.is_active = True
    order.save()
    i = 0
    totalsum = 0
    query.edit_message_text("Buyurtmaniz qabul qilindi" if user.lang == 'uz' else "Ваш заказ принят",
                            reply_markup=InlineKeyboardMarkup(
                                [
                                    [InlineKeyboardButton(
                                        'Bosh menyuga qaytish' if user.lang == 'uz' else 'Вернуться в главное меню',
                                        callback_data=ContextData.HOME)]
                                ]
                            ))
    text = f"<b>{order.user.first_name}</b> - <a href='{order.user.phone}'>{order.user.phone}</a>\n"
    orderItems = OrderItem.objects.filter(order=order)
    for orderItem in orderItems:
        i += 1
        som = "so'm" if user.lang == 'uz' else 'сум'
        text += f"<b>{i}. {orderItem.meal.name_uz if user.lang == 'uz' else orderItem.meal.name_ru}</b>\n  {orderItem.quantitation} x {orderItem.meal.price} = <b>{orderItem.total_price} {som}</b>\n"
        totalsum += orderItem.total_price
    text += f"\n {'Vaqti' if user.lang == 'uz' else 'Время'}: {order.create_at}"
    context.bot.send_location(chat_id="@foodzonezayafka", latitude=order.latitude, longitude=order.longitude)
    context.bot.send_message(chat_id="@foodzonezayafka", parse_mode="html", text=text)


def yoq(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()
    user = get_BotUser(tg_id=query.from_user.id)
    orders = Order.objects.filter(user=user, is_active=False).order_by('-pk')
    for order in orders:
        order.delete()
    query.edit_message_text("Buyurtmaniz qabul bekor qilindi" if user.lang == "uz" else "Ваш заказ был отменен",
                            reply_markup=InlineKeyboardMarkup(
                                [
                                    [InlineKeyboardButton(
                                        'Bosh menyuga qaytish' if user.lang == 'uz' else "Вернуться в главное меню",
                                        callback_data=ContextData.HOME)]
                                ]
                            ))


def orders(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()
    user = get_BotUser(tg_id=query.from_user.id)
    orders = Order.objects.filter(user=user, is_active=True).order_by("-pk")
    text = "<b>Buyurtmalar Tarixi</b>\n\n" if user.lang == 'uz' else "<b>История заказов</b>\n\n"
    if orders:
        index = 0
        for order in orders:
            index += 1
            indexOrderItem = 0
            orderItems = OrderItem.objects.filter(order=order).order_by('pk')
            text += f"<b>{index}</b>. {'Buyurtma raqami' if user.lang == 'uz' else 'номер заказа'} {order.id}\n"
            for orderItem in orderItems:
                indexOrderItem += 1
                text += f"  {indexOrderItem}. <b>{orderItem.meal.name_uz if user.lang == 'uz' else orderItem.meal.name_ru}</b> - {orderItem.meal.price} x {orderItem.quantitation} = {orderItem.total_price} so'm\n"
            else:
                text += "\n"
    else:
        text += "<i>Siz bizni botimiz orqali buyurtmalar amalga oshirmagansiz</i>" if user.lang == 'uz' else "<i>Вы не размещали у нас заказы через нашего бота</i>"
    query.edit_message_text(text=text, reply_markup=InlineKeyboardMarkup(
        [[InlineKeyboardButton("Orqaga" if user.lang == 'uz' else "Назад", callback_data=ContextData.HOME)]]),
                            parse_mode="HTML")
