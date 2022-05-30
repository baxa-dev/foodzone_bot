from modeltranslation.translator import TranslationOptions, register
from .models import Menu, Meal


@register(Meal)
class MealTranlationOption(TranslationOptions):
    fields = ('name', 'description',)
    required_languages = ('uz', 'ru',)


@register(Menu)
class MenuTranlationOption(TranslationOptions):
    fields = ('name',)
    required_languages = ('uz', 'ru',)
