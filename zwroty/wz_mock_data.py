"""Тестові дані для мок-ендпоінта генерації WZ.

Формат ідентичний до відповіді ``WZApiView`` (``/api/wz-order-list/``),
тому генератор працює однаково і для мока, і для реальних даних.
"""

MOCK_ORDERS = [
    {
        "bw_nr": "80208369",
        "wz_nr": 1948,
        "data": "12.06.2026",
        "user_name": "LANGE ANNA",
        "shop_desct": "12-POZNAŃ SWARZĘDZ",
        "shop_nr": "12-POZNAŃ SWARZĘDZ",
        "ship_doc": "95A",
        "type_of_delivery": "paczka",
        "lines": [
            {
                "reasone": "Brak zgody Planisty Operacyjnego na przyjęcie",
                "sku_log": "93836062",
                "sku_hand": "93836062",
                "descript": "BAT NATR DUST ZLOTY SZCZOTK Z/ZEST",
                "qty": "2",
            },
            {
                "reasone": "Brak zgody Planisty Operacyjnego na przyjęcie",
                "sku_log": "93836063",
                "sku_hand": "93836063",
                "descript": "BAT NATR DUST MIEDZ SZCZOTK Z/ZEST",
                "qty": "1",
            },
        ],
    },
    {
        "bw_nr": "80189873",
        "wz_nr": 1941,
        "data": "12.06.2026",
        "user_name": "LANGE ANNA",
        "shop_desct": "19-KALISZ",
        "shop_nr": "19-KALISZ",
        "ship_doc": "115C",
        "type_of_delivery": "paleta",
        "lines": [
            {
                "reasone": "Uszkodzony towar",
                "sku_log": "82479027",
                "sku_hand": "82479027",
                "descript": "GL 40X120 LARCHWOOD ALDER 1 44/3",
                "qty": "1",
            }
        ],
    },
    {
        "bw_nr": "80336645",
        "wz_nr": 1947,
        "data": "12.06.2026",
        "user_name": "SZAFRANSKA Ewa",
        "shop_desct": "11-WARSZAWA GIGAMARKET",
        "shop_nr": "11-WARSZAWA GIGAMARKET",
        "ship_doc": "134A",
        "type_of_delivery": "paleta",
        "lines": [
            {
                "reasone": "Uszkodzone kartony/opakowania",
                "sku_log": "90171203",
                "sku_hand": "90171203",
                "descript": "GL 30X60CLIFFSTONE CREAM RETT.1 8/10",
                "qty": "1",
            }
        ],
    },
    {
        "bw_nr": "80290696",
        "wz_nr": 1946,
        "data": "12.06.2026",
        "user_name": "SZAFRANSKA Ewa",
        "shop_desct": "13-WROCŁAW KARKONOSKA",
        "shop_nr": "13-WROCŁAW KARKONOSKA",
        "ship_doc": "116C",
        "type_of_delivery": "paleta",
        "lines": [
            {
                "reasone": "Uszkodzone kartony/opakowania",
                "sku_log": "91874868",
                "sku_hand": "91874868",
                "descript": "GL 39 8X119 8BAND WOOD BEIGE MATT 0 95",
                "qty": "1",
            },
            {
                "reasone": "Uszkodzone kartony/opakowania",
                "sku_log": "97172972",
                "sku_hand": "97172972",
                "descript": "GR SZK 60X120 EMERALD BEIGE MAT 1 44/2",
                "qty": "1",
            },
        ],
    },
    {
        "bw_nr": "80181097",
        "wz_nr": 1949,
        "data": "12.06.2026",
        "user_name": "SZAFRANSKA Ewa",
        "shop_desct": "45-ZIELONA GÓRA",
        "shop_nr": "45-ZIELONA GÓRA",
        "ship_doc": "112A",
        "type_of_delivery": "paleta",
        "lines": [
            {
                "reasone": "Uszkodzone kartony/opakowania",
                "sku_log": "95485998",
                "sku_hand": "95485998",
                "descript": "GR SZK 60X120 MIA GOLD BLUE 1 44/2",
                "qty": "1",
            },
            {
                "reasone": "Ilość niezgodna z jednostką wyjścia",
                "sku_log": "95796227",
                "sku_hand": "95796227",
                "descript": "GR SZK 60X60 TYMFI WHITE POL MDH 1 44/4",
                "qty": "3",
            },
            {
                "reasone": "Ilość niezgodna z jednostką wyjścia",
                "sku_log": "95554277",
                "sku_hand": "95554277",
                "descript": "GR SZK 60X120 MEDEA BIANCO MAT GR 1 44/2",
                "qty": "1",
            },
        ],
    },
    {
        "bw_nr": "80025753",
        "wz_nr": 1950,
        "data": "12.06.2026",
        "user_name": "SZAFRANSKA Ewa",
        "shop_desct": "84-POZNAN SERBSKA",
        "shop_nr": "84-POZNAN SERBSKA",
        "ship_doc": "103A",
        "type_of_delivery": "paleta",
        "lines": [
            {
                "reasone": "Uszkodzone kartony/opakowania",
                "sku_log": "86790262",
                "sku_hand": "86790262",
                "descript": "GL 29 8X89 8BALADE CHEVRON WOODMDH1 07/4",
                "qty": "1",
            }
        ],
    },
]
