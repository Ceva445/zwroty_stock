import datetime
import io
from django.conf import settings
from django.http import FileResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse
from django.views import View
from datetime import datetime
from user.mixins import CustomForcePasswordChangeMixin

from .get_or_create_sku import get_or_create_sku
from .models import (
    Barcode, Product, 
    ReturnOrder, Shop, 
    ReasoneComment, SkuInformation,
    SkuInformationBarcode
    )
from django.core.cache import cache
from django.core.exceptions import ObjectDoesNotExist
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.graphics.barcode import code128
from django.db.models import Min, Max


def admin_panel(request):
    return render(request, "zwroty/admin_panel.html")

class HomeView(LoginRequiredMixin, CustomForcePasswordChangeMixin ,View):
    template_name = "index.html"

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name)
    

class WZMenagment(LoginRequiredMixin, View):
    template_name = "zwroty/wz_menagment.html"

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name)


class ReturnOrderCreate(LoginRequiredMixin, View):
    template_name = "zwroty/return_order_create.html"

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name)

    def post(self, request, *args, **kwargs):

        nr_order = request.POST.get("order_number")
        shop_nr = request.POST.get("shop")
        comment = request.POST.get("comment", "")
        position_nr = request.POST.get("wz_nr")
        user = self.request.user
        shop = Shop.objects.get(shop_nr=int(shop_nr))

        return_order = ReturnOrder(
            nr_order=nr_order,
            shop=shop,
            comment=comment,
            position_nr=position_nr,
            user=user,
        )
        return_order.save()

        return render(request, "index.html")


class AddLineMenuView(LoginRequiredMixin, View):
    def get(self, request):
        return render(request, "zwroty/add_line_menu.html")
    def post(self, request, *args, **kwargs):
        identifier = request.POST.get('identifier', None)
        compile_exces = request.POST.get("compile_exces", None)
        try:
            order = ReturnOrder.objects.get(identifier=identifier)
            if compile_exces:
                order_line = order.products.all()
                order_line.delete()
                return HttpResponseRedirect(reverse('zwroty:add_product') + '?identifier=' + str(identifier))
            if order.complite_status:
              return render(
                request, 
                "zwroty/add_line_menu.html", 
                context={"error_message": "Uwaga ponowne otwrcie Wztki spowoduje utracenie dotychczasowych danych. Czy na pewno chcesz ją otworzyć?", "complite":True, "identifier":identifier}
                )  
        except ObjectDoesNotExist:
            return render(
                request, 
                "zwroty/add_line_menu.html", 
                context={"error_message": "Nieprawidlowy indetufukator"}
                )
        return HttpResponseRedirect(reverse('zwroty:add_product') + '?identifier=' + str(identifier))

class AddProduct(LoginRequiredMixin, View):
    template_name = "zwroty/add_product.html"

    def get_context_data(self, **kwargs):
        reas_list = ReasoneComment.objects.all()
        reasons = [{"id": reas.id, "name": reas.name} for reas in reas_list]
        context = {"reasons": reasons}
        return context

    def get(self, request, *args, **kwargs):
        identifier = self.request.GET.get("identifier")
        context = self.get_context_data()
        context["identifier"] = identifier
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        user = self.request.user
        reas_name = request.POST.get("reason_name")
        sku_deskript = request.POST.get("sku_deskription")
        
        ean = request.POST.get("ean")
        qty = request.POST.get("qty")
        finish = self.request.POST.get("finish")
        identifier = self.request.POST.get("identifier")
        
        if finish:
            tape_of_delivery = request.POST.get("tape_of_delivery")
            cache_data = cache.get(identifier)

            if cache_data is None:
                return redirect("zwroty:home")
            reas_queryset = ReasoneComment.objects.all()
            order = ReturnOrder.objects.get(identifier=identifier)
            product_list = Product.objects.bulk_create([
                Product(
                    sku = line["sku"],
                    quantity = line["qty"],
                    reasone = reas_queryset.get(name=line["reas_name"]),
                    actual_barcode = line["ean"],
                    date_time_recive = line["date_time_recive"],
                )
                for line in cache_data
            ])
           
            order.products.add(*product_list)
            order.complite_status = True
            order.tape_of_delivery = tape_of_delivery
            order.user = user
            order.date_recive = datetime.now()
            order.save()
            cached_value = cache.get(identifier)
            cache.delete(identifier)
            return redirect("zwroty:home")

        sku = get_or_create_sku(ean=ean, sku_description=sku_deskript)

        order_line = {
                "user": user, 
                "qty": qty,
                "reas_name": reas_name, 
                "sku": sku,
                "ean": ean, 
                "date_time_recive": datetime.now()
                }
        # "tape_of_delivery": tape_of_delivery 
        cached_value = cache.get(identifier)
        if cached_value:
            cached_value.append(order_line)
        else:
            cached_value = [order_line]
        cache.set(identifier, cached_value, timeout=300)
        return HttpResponseRedirect(reverse('zwroty:add_product') + '?identifier=' + str(identifier))


class ReportWZView(LoginRequiredMixin, View):
    template_name = "zwroty/report_wz.html"

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name)
    def post(self, request, *args, **kwargs):
        rec_day_aft = self.request.POST.get("day_aft", None)
        rec_day_bef = self.request.POST.get("day_bef", None)


        order_list = ReturnOrder.objects.filter(complite_status=False)
        if rec_day_aft:
            rec_day_aft = datetime.strptime(rec_day_aft, "%Y-%m-%d")
            order_list = order_list.filter(date_recive__date__gte=rec_day_aft)
        if rec_day_bef:
            rec_day_bef = datetime.strptime(rec_day_bef, "%Y-%m-%d")
            order_list = order_list.filter(date_recive__date__lte=rec_day_bef)

        buffer = io.BytesIO()
        my_canvas = canvas.Canvas(buffer)
        
        pdfmetrics.registerFont(TTFont("FreeSans", "freesans/FreeSans.ttf"))
        for order in order_list:
            my_canvas.setFont("FreeSans", 20)
            barcode = code128.Code128(f"{order.identifier}", barWidth=1.7, barHeight=35)
            barcode.drawOn(my_canvas, 80, 564)
            
            rec_data = datetime.strftime(order.date_recive, "%Y-%m-%d")
            my_canvas.drawString(100, 674, f'Data: {rec_data}')
            my_canvas.drawString(100, 654, f"Bon wyjścia: {order.nr_order}")
            my_canvas.drawString(100, 634, f"Numer wuzetki: {order.position_nr}")
            my_canvas.drawString(100, 614, f"Sklep: {order.shop.description}")
            my_canvas.drawString(300, 570, f"<-- Zeskanuj ({order.identifier})")
            my_canvas.showPage()
        my_canvas.save()
        buffer.seek(0)
        response = FileResponse(buffer, as_attachment=False, filename="Protokół szkody.pdf")
        return response
    
class OrderStorageView(LoginRequiredMixin, View):
    template_name = "zwroty/return_order_filter.html"

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name)
    
    def post(self, request, *args, **kwargs):

        identifier = request.POST.get("identifier", None)
        nr_order = request.POST.get("nr_order", None)
        position_nr = request.POST.get("position_nr", None)
        status = request.POST.get("staus", None)
        date_recive = request.POST.get("date_recive", None)

        queryset = ReturnOrder.objects.all().select_related("shop", "user").prefetch_related("products")

        if identifier:
            queryset = queryset.filter(identifier__icontains=identifier)
        if position_nr:
            queryset = queryset.filter(identifier__icontains=position_nr)
        if nr_order:
            queryset = queryset.filter(nr_order__icontains=nr_order)
        if status:
            status = int(status)
            queryset = queryset.filter(complite_status=status)
        if date_recive:
            date_recive = datetime.strptime(date_recive, "%Y-%m-%d")
            queryset = queryset.filter(date_recive__date=date_recive)

        queryset = queryset.annotate(
                    first_product_time=Min("products__date_time_recive"),
                    last_product_time=Max("products__date_time_recive")
                )

        context = {"order_list": queryset.order_by("-date_recive")}
        return render(request, "zwroty/return_order_list.html", context)


class ReturnOrderDetailView(LoginRequiredMixin, View):
    def get_context_data(self, oredr_id):
        context = {}
        order = get_object_or_404(ReturnOrder, id=oredr_id)
        date_recive = order.date_recive.strftime("%d.%m.%Y")
        context["date_recive"] = date_recive
        context["order"] = order
        context["order_products"] = [
            (f"sku_log: {product.sku.sku_log}\n\
                sku_hand: {product.sku.sku_hand}\n\
                    sku_ean: {product.actual_barcode}\n\
                        sku_deskript: {product.sku.name_of_product}\n\
                            typ: {product.reasone.name}\n\
                                data przyjęcia: {product.date_time_recive.strftime('%d.%m.%Y %H:%M')}",
            product) 
                        
                for product in order.products.all()]
        return context

    def get(self, request, *args, **kwargs):
        order_id = self.kwargs.get("pk")
        context = self.get_context_data(oredr_id=order_id)
        return render(request, "zwroty/return_order_detail.html", context)

    def post(self, request, *args, **kwargs):
        return_order_id = self.kwargs.get("pk")
        delete_order = self.request.POST.get("delete_order")
        unprint = self.request.POST.get("unprint")
        revese_complete = self.request.POST.get("ureverse_complete_status")
        return_order = ReturnOrder.objects.get(id=return_order_id)
        if unprint:
            return_order.generate_xls_status = False
        if revese_complete:
            return_order.complite_status = not return_order.complite_status
        
        selected_products_ids = request.POST.getlist("selected_products")
        if selected_products_ids:
            selected_products = Product.objects.filter(id__in=selected_products_ids)
            selected_products.delete()
        return_order.save()

        if delete_order:
            return_order.delete()
            return redirect("zwroty:order_filter_page")
        return redirect("zwroty:return_order_detail", pk=return_order_id)

class ReturnOrderListView(LoginRequiredMixin, View):
    template_name = "zwroty/return_order_list.html"

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name)
