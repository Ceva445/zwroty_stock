from django.contrib import admin
from .models import (
    Shop,
    SkuInformation,
    Barcode,
    Product,
    ReasoneComment,
    ReturnOrder,
    SkuInformationBarcode,
)
from rangefilter.filters import DateRangeFilter


# ---------------- PRODUCT ----------------
@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("id", "sku", "quantity", "actual_barcode", "reasone")
    search_fields = (
        "actual_barcode",
        "sku__sku_log",
        "sku__name_of_product",
    )
    list_select_related = ("sku", "reasone")
    autocomplete_fields = ("sku", "reasone")


# ---------------- SKU ----------------
@admin.register(SkuInformation)
class SkuInformationAdmin(admin.ModelAdmin):
    search_fields = ("sku_log", "name_of_product")


# ---------------- SHOP ----------------
@admin.register(Shop)
class ShopAdmin(admin.ModelAdmin):
    search_fields = ("shop_nr", "description")


# ---------------- REASONE ----------------
@admin.register(ReasoneComment)
class ReasoneCommentAdmin(admin.ModelAdmin):
    search_fields = ("name",)


# ---------------- BARCODE ----------------
@admin.register(Barcode)
class BarcodeAdmin(admin.ModelAdmin):
    search_fields = ("barcode",)


# ---------------- SKU BARCODE ----------------
@admin.register(SkuInformationBarcode)
class SkuInformationBarcodeAdmin(admin.ModelAdmin):
    list_display = ("sku_information", "barcode")
    search_fields = (
        "sku_information__sku_log",
        "barcode__barcode",
    )
    list_select_related = ("sku_information", "barcode")

    autocomplete_fields = ("sku_information", "barcode")
# ---------------- RETURN ORDER ----------------
@admin.register(ReturnOrder)
class ReturnOrderAdmin(admin.ModelAdmin):
    list_display = (
        "identifier",
        "nr_order",
        "shop",
        "date_recive",
        "complite_status",
        "generate_xls_status",
    )

    list_select_related = ("shop", "user")

    search_fields = (
        "identifier",
        "nr_order",
        "shop__shop_nr",
    )

    list_filter = (
        "complite_status",
        "generate_xls_status",
        ("date_recive", DateRangeFilter),
    )

    autocomplete_fields = ("products",)

    # ✅ Rejestracja akcji masowych
    actions = [
        "set_generate_xls_true",
        "set_generate_xls_false",
    ]

    # -------------------------------------------------
    # AKCJA 1 – ustaw generate_xls_status = True
    # -------------------------------------------------
    @admin.action(description="Ustaw generate_xls_status wyłączony (True)")
    def set_generate_xls_true(self, request, queryset):
        updated = queryset.update(generate_xls_status=True)
        self.message_user(
            request,
            f"Zaktualizowano {updated} zamówień (generate_xls_status=True)"
        )

    # -------------------------------------------------
    # AKCJA 2 – ustaw generate_xls_status = False
    # -------------------------------------------------
    @admin.action(description="Ustaw generate_xls_status nie wygenerowane (False)")
    def set_generate_xls_false(self, request, queryset):
        updated = queryset.update(generate_xls_status=False)
        self.message_user(
            request,
            f"Zaktualizowano {updated} zamówień (generate_xls_status=False)"
        )

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related("shop", "user").prefetch_related(
            "products",
            "products__sku",
            "products__reasone",
        )