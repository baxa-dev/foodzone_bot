from django.db import models


# Create your models here.


class BotUser(models.Model):
    LANG = (
        ("uz", "uz"),
        ("ru", "ru")
    )

    tg_id = models.PositiveBigIntegerField(unique=True, verbose_name="ID")
    first_name = models.CharField(max_length=255, null=True, blank=True, verbose_name="Ism")
    last_name = models.CharField(max_length=255, null=True, blank=True, verbose_name="Familiya")
    phone = models.CharField(max_length=20, null=True, blank=True, verbose_name="Telefon nomer")
    is_active = models.BooleanField(default=False, null=True, blank=True, verbose_name="Aktiv")
    lang = models.CharField(max_length=2, choices=LANG, verbose_name="Til")
    create_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        if self.phone is not None:
            return self.phone
        return str(self.id)

    @property
    def get_full_name(self):
        return f"{self.first_name} {self.last_name}"

    class Meta:
        verbose_name = "Foydalanuvchi"
        verbose_name_plural = "Foydalanuvchilar"


class Menu(models.Model):
    name = models.CharField(max_length=255, verbose_name="Nomi")

    def __str__(self) -> str:
        return self.name

    class Meta:
        verbose_name = "Kategoriya"
        verbose_name_plural = "Kategoriyalar"


class Meal(models.Model):
    menu = models.ForeignKey(Menu, on_delete=models.RESTRICT, verbose_name="Kategoriya")
    name = models.CharField(max_length=255, verbose_name="Nomi")
    description = models.TextField(verbose_name="Tavsif")
    price = models.IntegerField(verbose_name="Narx")
    image = models.ImageField(verbose_name="Rasm")

    def __str__(self) -> str:
        return self.name

    class Meta:
        verbose_name = "Maxsulot"
        verbose_name_plural = "Maxsulotlar"


class OrderItem(models.Model):
    user = models.ForeignKey(BotUser, on_delete=models.RESTRICT)
    order = models.ForeignKey("Order", on_delete=models.SET_NULL, null=True, blank=True)
    meal = models.ForeignKey(Meal, on_delete=models.RESTRICT)
    quantitation = models.SmallIntegerField(default=0)
    is_ordered = models.BooleanField(default=False)

    @property
    def total_price(self):
        return self.meal.price * self.quantitation

    def __str__(self) -> str:
        return f"{self.user.get_full_name} {self.meal.name}"


class Order(models.Model):
    user = models.ForeignKey(BotUser, on_delete=models.RESTRICT)
    latitude = models.CharField(max_length=255, null=True)
    longitude = models.CharField(max_length=255, null=True)
    is_active = models.BooleanField(default=False)
    create_at = models.DateTimeField(auto_now_add=True, null=True)

    @property
    def total_price(self):
        orderItems = OrderItem.objects.filter(order_id=self.pk).order_by("pk")
        if orderItems is not None:
            total = 0
            for orderItem in orderItems:
                total += orderItem.total_price
            return total
        return 0
