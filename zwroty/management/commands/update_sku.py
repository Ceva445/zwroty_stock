import pandas as pd
from tqdm import tqdm
from django.core.management.base import BaseCommand
from django.db import transaction

from zwroty.models import (
    SkuInformation,
    Barcode,
    SkuInformationBarcode,
)


class Command(BaseCommand):
    help = "Upsert SKU + Barcode mapping (no schema changes)"

    def handle(self, *args, **options):

        df = pd.read_excel("sku_litige_stock.xlsx", engine="openpyxl")
        df.columns = df.columns.str.strip().str.lower()

        self.stdout.write(f"Total rows in file: {len(df)}")

        # ============================================================
        # 0️⃣ ОЧИСТКА
        # ============================================================

        df = df[df["barcode"].notna()]
        df["barcode"] = df["barcode"].astype(str)

        # прибираємо дублікати barcode (залишаємо останній)
        df = df.drop_duplicates(subset=["barcode"], keep="last")

        self.stdout.write(f"Rows after deduplication: {len(df)}")

        records = df.to_dict("records")

        unique_skus = {int(r["sku"]) for r in records}
        unique_barcodes = {r["barcode"] for r in records}

        batch_size = 10000

        with transaction.atomic():

            # ============================================================
            # 1️⃣ SKU (з оновленням name_of_product)
            # ============================================================

            # sku → name_of_product (останній запис перемагає)
            sku_name_map = {}
            for r in records:
                sku_name_map[int(r["sku"])] = str(r.get("deskription", "")).strip()

            existing_skus = {
                s.sku_log: s
                for s in SkuInformation.objects.filter(sku_log__in=unique_skus)
            }

            sku_to_create = []
            sku_to_update = []

            for sku_value, product_name in sku_name_map.items():

                if sku_value in existing_skus:
                    obj = existing_skus[sku_value]
                    updated = False

                    if obj.sku_hand != sku_value:
                        obj.sku_hand = sku_value
                        updated = True

                    if obj.name_of_product != product_name:
                        obj.name_of_product = product_name
                        updated = True

                    if updated:
                        sku_to_update.append(obj)

                else:
                    sku_to_create.append(
                        SkuInformation(
                            sku_log=sku_value,
                            sku_hand=sku_value,
                            name_of_product=product_name,
                        )
                    )

            self.stdout.write(
                f"SKU → create: {len(sku_to_create)}, update: {len(sku_to_update)}"
            )

            if sku_to_create:
                SkuInformation.objects.bulk_create(
                    sku_to_create,
                    batch_size=batch_size,
                )

            if sku_to_update:
                SkuInformation.objects.bulk_update(
                    sku_to_update,
                    ["sku_hand", "name_of_product"],
                    batch_size=batch_size,
                )

            # ============================================================
            # 2️⃣ BARCODE (unique=True → ignore_conflicts)
            # ============================================================

            barcode_instances = [
                Barcode(barcode=b) for b in unique_barcodes
            ]

            Barcode.objects.bulk_create(
                barcode_instances,
                ignore_conflicts=True,
                batch_size=batch_size,
            )

            self.stdout.write("Base tables synced")

            # ============================================================
            # 3️⃣ MAPPING
            # ============================================================

            sku_map = {
                s.sku_log: s.id
                for s in SkuInformation.objects.filter(sku_log__in=unique_skus)
            }

            barcode_map = {
                b.barcode: b.id
                for b in Barcode.objects.filter(barcode__in=unique_barcodes)
            }

            existing_mappings = set(
                SkuInformationBarcode.objects.filter(
                    sku_information_id__in=sku_map.values(),
                    barcode_id__in=barcode_map.values(),
                ).values_list("sku_information_id", "barcode_id")
            )

            mapping_to_create = []

            for row in tqdm(records, desc="Preparing mappings"):
                sku_id = sku_map[int(row["sku"])]
                barcode_id = barcode_map[row["barcode"]]

                if (sku_id, barcode_id) not in existing_mappings:
                    mapping_to_create.append(
                        SkuInformationBarcode(
                            sku_information_id=sku_id,
                            barcode_id=barcode_id,
                        )
                    )

            if mapping_to_create:
                SkuInformationBarcode.objects.bulk_create(
                    mapping_to_create,
                    batch_size=batch_size,
                )

        self.stdout.write(
            self.style.SUCCESS("SKU + Barcode mapping updated successfully")
        )