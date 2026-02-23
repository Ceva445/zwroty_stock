from rest_framework.views import APIView
from rest_framework.response import Response
from zwroty.models import ReturnOrder


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
