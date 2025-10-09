from django.conf import settings
from django.db import models


class Shop(models.Model):
    shop_nr = models.IntegerField()
    description = models.CharField(max_length=100)
    ship_doc = models.CharField(max_length=4)

    def __str__(self) -> str:
        return f"{self.shop_nr} - {self.description}"


class SkuInformation(models.Model):
    sku_log = models.BigIntegerField()
    sku_hand = models.BigIntegerField(blank=True, null=True)
    name_of_product = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        if self.name_of_product:
            return f"{self.sku_log} {self.name_of_product}"
        return str(self.sku_log)


class Barcode(models.Model):
    barcode = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.barcode


class SkuInformationBarcode(models.Model):
    barcode = models.ForeignKey(Barcode, on_delete=models.CASCADE)
    sku_information = models.ForeignKey(SkuInformation, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.sku_information} {self.barcode}"

class ReasoneComment(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self) -> str:
        return self.name


class Product(models.Model):
    
    sku = models.ForeignKey("SkuInformation", on_delete=models.CASCADE, null=True)
    quantity = models.IntegerField()
    actual_barcode = models.CharField(max_length=20)
    date_time_recive = models.DateTimeField(null=True, blank=True)

    
    reasone = models.ForeignKey(ReasoneComment, on_delete=models.CASCADE)

    def __str__(self) -> str:
        if not self.sku.name_of_product:
            return f"{self.sku.sku_log} - {self.quantity}"
        return str(self.sku.name_of_product)


class ReturnOrder(models.Model):
    PALLET = "paleta"
    BOX = "paczka"

    TAPE_OF_DELIVERY_CHOICES = [
        (PALLET, "Paleta"),
        (BOX, "Paczka"),
    ]
    tape_of_delivery = models.CharField(
        max_length=6,
        choices=TAPE_OF_DELIVERY_CHOICES,
        default=BOX,
        verbose_name="tape_of_delivery",
    )
    nr_order = models.CharField(max_length=20)#bon wyjszcia
    position_nr = models.IntegerField()#NR WZ
    shop = models.ForeignKey(Shop, on_delete=models.CASCADE)
    products = models.ManyToManyField(Product, blank=True)

    identifier = models.BigIntegerField(unique=True)
    date_recive = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    comment = models.TextField(blank=True, null=True)
    transaction = models.TextField(blank=True)
    complite_status = models.BooleanField(default=False)
    generate_xls_status = models.BooleanField(default=False)

    def __str__(self) -> str:
        return f"{self.nr_order} - {self.shop}"
