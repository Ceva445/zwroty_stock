import os

from django.http import FileResponse
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from zwroty.models import ReturnOrder
from zwroty import wz_generator
from zwroty.wz_mock_data import MOCK_ORDERS


def _orders_from_db():
    """Готує список замовлень у тому ж форматі, що й ``WZApiView`` віддає JSON-ом."""
    orders = ReturnOrder.objects.filter(
        complite_status=True, generate_xls_status=False
    ).select_related("shop", "user").prefetch_related(
        "products__sku", "products__reasone"
    )
    order_list = []
    for order in orders:
        order_data = {
            "bw_nr": order.nr_order,
            "wz_nr": order.position_nr,
            "data": order.date_recive.strftime("%d.%m.%Y"),
            "user_name": order.user.full_name,
            "shop_desct": order.shop.description,
            "shop_nr": order.shop.description,
            "ship_doc": order.shop.ship_doc,
            "type_of_delivery": order.tape_of_delivery,
            "lines": [],
        }
        for product in order.products.all():
            sku_log = product.sku.sku_log
            sku_hand = product.sku.sku_hand
            name_of_product = product.sku.name_of_product
            order_data["lines"].append({
                "reasone": product.reasone.name,
                "sku_log": "" if sku_log is None or len(str(sku_log)) > 8
                else str(sku_log).replace("999999999999", ""),
                "sku_hand": "" if sku_hand is None or len(str(sku_hand)) > 8 else str(sku_hand),
                "descript": "" if name_of_product is None else name_of_product,
                "qty": f"{product.quantity}",
            })
        order_list.append(order_data)
    return order_list, list(orders.values_list("id", flat=True))


class WZGenerateView(APIView):
    """Генерує xlsx (по одному на замовлення) + спільний PDF (3 копії аркуша).

    ``?mock=1`` — використати тестові дані (нічого не чіпає в БД).
    Повертає ``{"batch_id", "files": [{"token", "filename", "type"}]}``.
    """

    def post(self, request):
        wz_generator.cleanup_stale_batches()
        if request.query_params.get("mock"):
            orders = MOCK_ORDERS
            order_ids = []
        else:
            orders, order_ids = _orders_from_db()

        if not orders:
            return Response({"batch_id": None, "files": []})

        batch_id, files = wz_generator.generate_wz_batch(orders, order_ids)
        payload = [
            {"token": f["token"], "filename": f["filename"], "type": f["type"]}
            for f in files
        ]
        return Response({"batch_id": batch_id, "files": payload})


class WZDownloadView(APIView):
    """Віддає один файл із batch за токеном."""

    def get(self, request, batch_id, token):
        resolved = wz_generator.resolve_file(batch_id, token)
        if not resolved:
            return Response({"detail": "not found"}, status=status.HTTP_404_NOT_FOUND)
        path, filename = resolved
        return FileResponse(open(path, "rb"), as_attachment=True, filename=filename)


class WZConfirmView(APIView):
    """Викликається Apps Script після успішного завантаження файлів.

    Тільки тут (після підтвердженого завантаження) замовлення позначаються як
    надруковані (``generate_xls_status=True``), щоб не потрапляти в наступну
    генерацію. Якщо завантаження не вдалось — confirm не викликається, статус
    лишається ``False`` і WZ можна згенерувати повторно.
    """

    def post(self, request, batch_id):
        # прочитати id ДО видалення теки (delete_batch знищує manifest)
        order_ids = wz_generator.batch_order_ids(batch_id)
        deleted = wz_generator.delete_batch(batch_id)
        if not deleted:
            return Response({"detail": "not found"}, status=status.HTTP_404_NOT_FOUND)
        marked = 0
        if order_ids:
            marked = ReturnOrder.objects.filter(id__in=order_ids).update(
                generate_xls_status=True
            )
        return Response({"status": "deleted", "marked": marked})


class WZApiView(APIView):
    def get(self, request):
        orders = ReturnOrder.objects.filter(
            complite_status=True, generate_xls_status=False
            ).select_related("shop", "user").prefetch_related(
        "products__sku",
        "products__reasone",
    )
        order_list = []
        for order in orders:
            order_data = {
                "bw_nr": order.nr_order,
                "wz_nr":  order.position_nr,
                "data": order.date_recive.strftime("%d.%m.%Y"),
                "user_name": order.user.full_name,
                "shop_desct": order.shop.description,
                "shop_nr": order.shop.description,
                "ship_doc": order.shop.ship_doc,
                "type_of_delivery":  order.tape_of_delivery,
                "lines": []
            }
            
            for product in order.products.all():

                sku_log = product.sku.sku_log
                sku_hand = product.sku.sku_hand
                name_of_product = product.sku.name_of_product

                product_data = {
                    "reasone":  product.reasone.name,
                    "sku_log": "" if sku_log == None or len(str(sku_log))>8 else str(sku_log).replace("999999999999",""),
                    "sku_hand": "" if sku_hand == None or len(str(sku_hand))>8 else str(sku_hand),
                    "descript": "" if name_of_product == None else name_of_product,
                    "qty": f"{product.quantity}"
                }
                order_data["lines"].append(product_data)
            order_list.append(order_data)

        orders.update(generate_xls_status=True)

        return Response(order_list)
