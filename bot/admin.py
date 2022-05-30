from django.contrib import admin
from bot.models import BotUser, Meal, Menu
from django.contrib.auth.models import User
from django.contrib.auth.models import Group

admin.site.unregister(User)
admin.site.unregister(Group)


@admin.register(BotUser)
class BotUserAdmin(admin.ModelAdmin):
    list_display_links = ("phone", "is_active", "first_name", "lang",)
    list_display = list_display_links
    search_fields = ("first_name", "phone",)
    readonly_fields = ("phone", "first_name", "last_name", "lang", "tg_id")

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(Meal)
class MealAdmin(admin.ModelAdmin):
    list_display_links = (
        "menu",
        "name",
        "description",
        "price",
    )
    list_display = list_display_links


@admin.register(Menu)
class MenuAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "name_uz",
        "name_ru",
    )
    list_display_links = list_display
