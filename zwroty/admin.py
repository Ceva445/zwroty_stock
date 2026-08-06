from django.contrib import admin
from django.contrib.admin.views.main import ChangeList
from django.db.models import Q
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


# Semicolon-separated multi-value search for the ReturnOrder changelist.
# The three GET keys carry raw "a;b;c" strings; the custom ChangeList drops
# them from lookup validation so the admin doesn't treat them as ORM lookups.
RETURNORDER_SEARCH_KEYS = ("s_identifier", "s_nr_order", "s_position_nr")


def _split_multi(raw):
    """`"12; 34 ;;56"` -> `["12", "34", "56"]` (trimmed, blanks dropped)."""
    return [part.strip() for part in (raw or "").split(";") if part.strip()]


class ReturnOrderChangeList(ChangeList):
    """Keeps our custom search keys out of Django's lookup machinery."""

    def get_filters_params(self, params=None):
        lookup_params = super().get_filters_params(params)
        for key in RETURNORDER_SEARCH_KEYS:
            lookup_params.pop(key, None)
        return lookup_params

    def get_queryset(self, request, exclude_parameters=None):
        qs = super().get_queryset(request, exclude_parameters=exclude_parameters)
        return self.model_admin.apply_multi_search(request, qs)


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
        "position_nr",
        "shop",
        "date_recive",
        "complite_status",
        "generate_xls_status",
    )

    list_select_related = ("shop", "user")

    # Search is provided by three dedicated ";"-multi fields (see change_list
    # template + apply_multi_search below), not by the default admin search box.
    change_list_template = "admin/zwroty/returnorder/change_list.html"

    def get_changelist(self, request, **kwargs):
        return ReturnOrderChangeList

    def apply_multi_search(self, request, qs):
        # identifier (BigInteger) — exact match on any of the given numbers.
        raw_ident = _split_multi(request.GET.get("s_identifier"))
        if raw_ident:
            ids = [int(v) for v in raw_ident if v.lstrip("-").isdigit()]
            qs = qs.filter(identifier__in=ids) if ids else qs.none()

        # nr_order (Char) — partial match, OR across the given values.
        orders = _split_multi(request.GET.get("s_nr_order"))
        if orders:
            cond = Q()
            for value in orders:
                cond |= Q(nr_order__icontains=value)
            qs = qs.filter(cond)

        # position_nr (Integer) — exact match on any of the given numbers.
        raw_pos = _split_multi(request.GET.get("s_position_nr"))
        if raw_pos:
            positions = [int(v) for v in raw_pos if v.lstrip("-").isdigit()]
            qs = qs.filter(position_nr__in=positions) if positions else qs.none()

        return qs

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